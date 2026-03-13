import React, { useRef } from 'react';

interface PosterLayer {
  type: 'background' | 'rect' | 'image' | 'badge' | 'text' | 'checklist' | 'cta_button' | 'footer' | 'divider' | string;
  role?: string;
  // background
  colors?: string[];
  color?: string;   // flat color for solid background or text color
  pattern?: string;
  // text / badge / cta
  text?: string;
  // checklist
  items?: string[];
  // image
  src?: string;
  width?: number;
  height?: number;
  // backend flat properties (mapped to styling via normalizeLayer)
  bg?: string;           // badge/cta/rect background color
  fill?: string;         // rect fill color
  text_color?: string;   // text/badge foreground color
  font_size?: number;    // font size in poster-space pixels
  bold?: boolean;        // bold flag
  align?: string;        // text alignment
  w?: number;            // image width alias
  h?: number;            // image height alias
  brand_name?: string;   // footer brand name
  phone?: string;        // footer phone
  address?: string;      // footer address
  // position hints (not used in HTML renderer — layout is flow-based)
  position?: { x: number; y: number };
  // styling overrides
  styling?: {
    color?: string;
    fontSize?: number | string;
    fontWeight?: string;
    fontFamily?: string;
    textAlign?: string;
    backgroundColor?: string;
    borderRadius?: number | string;
    padding?: string;
    marginTop?: number | string;
    opacity?: number;
  };
}

/**
 * normalizeLayer — converts flat backend-generated layer properties into
 * the nested `styling` format expected by render functions, and fixes the
 * background layer type (backend may emit "gradient"/"solid" instead of "background").
 */
function normalizeLayer(raw: any): PosterLayer {
  const layer: any = { ...raw };

  // 1. Fix background type: backend spreads bg-dict which overwrites "background"
  //    type with "gradient" or "solid"
  if (layer.type === 'gradient' || layer.type === 'solid') {
    layer.type = 'background';
    if (layer.type === 'solid' && layer.color && !layer.colors) {
      layer.colors = [layer.color];
    }
  }

  // 2. Normalise w/h → width/height for image layers
  if (layer.w !== undefined && layer.width === undefined) layer.width = layer.w;
  if (layer.h !== undefined && layer.height === undefined) layer.height = layer.h;

  // 3. Build / merge styling from flat backend properties
  const s: Record<string, any> = { ...(layer.styling || {}) };

  if ((layer.bg || layer.fill) && !s.backgroundColor) {
    s.backgroundColor = layer.bg || layer.fill;
  }
  if (layer.text_color && !s.color) {
    s.color = layer.text_color;
  }
  // For non-background/image layers, a top-level `color` is the text colour
  if (layer.color && !s.color && layer.type !== 'background' && layer.type !== 'image') {
    s.color = layer.color;
  }
  if (layer.font_size !== undefined && s.fontSize === undefined) {
    s.fontSize = layer.font_size;
  }
  if (layer.bold !== undefined && s.fontWeight === undefined) {
    s.fontWeight = layer.bold ? '800' : '400';
  }
  if (layer.align && !s.textAlign) {
    s.textAlign = layer.align;
  }
  if (layer.font_family && !s.fontFamily) {
    s.fontFamily = layer.font_family;
  }

  layer.styling = s;
  return layer as PosterLayer;
}

interface PosterData {
  version?: string;
  platform?: string;
  template_slug?: string;
  dimensions?: { width: number; height: number };
  meta?: {
    brand_name?: string;
    campaign_city?: string;
    language_secondary?: string;
  };
  bilingual_content?: Record<string, string>;
  layers?: PosterLayer[];
}

interface PosterRendererProps {
  posterJson: PosterData;
  scale?: number; // 0.3 for thumbnail, 1 for full
  showDownload?: boolean;
}

// Resolve a gradient or solid color from an array of color stops
function resolveBackground(colors?: string[]): string {
  if (!colors || colors.length === 0) return '#1E3A8A';
  if (colors.length === 1) return colors[0];
  return `linear-gradient(135deg, ${colors.join(', ')})`;
}

// Layer renderers
function renderBackground(layer: PosterLayer, idx: number) {
  const bg = resolveBackground(layer.colors);
  return (
    <div
      key={idx}
      className="absolute inset-0"
      style={{ background: bg, zIndex: 0 }}
    />
  );
}

function renderRect(layer: PosterLayer, idx: number) {
  const bg = layer.styling?.backgroundColor || (layer.colors ? resolveBackground(layer.colors) : '#F59E0B');
  const { textAlign: _ta, ...restStyling } = layer.styling || {};
  const safeTextAlign = (_ta as React.CSSProperties['textAlign']) || undefined;
  return (
    <div
      key={idx}
      className="relative w-full"
      style={{
        background: bg,
        height: layer.height || 8,
        ...restStyling,
        ...(safeTextAlign ? { textAlign: safeTextAlign } : {}),
        zIndex: 1,
      }}
    />
  );
}

function renderBadge(layer: PosterLayer, idx: number) {
  const badgeText = sanitizePosterText(layer.text || '');
  if (!badgeText || badgeText.trim() === '') return null;
  // shadow original text with sanitised value
  layer = { ...layer, text: badgeText };
  return (
    <div
      key={idx}
      className="relative inline-block px-4 py-1 rounded-full font-bold text-center"
      style={{
        background: layer.styling?.backgroundColor || '#F59E0B',
        color: layer.styling?.color || '#1a1a1a',
        fontSize: layer.styling?.fontSize || 13,
        fontWeight: layer.styling?.fontWeight || '800',
        letterSpacing: '0.08em',
        margin: '4px auto',
        zIndex: 2,
        ...(layer.styling as React.CSSProperties || {}),
      }}
    >
      {layer.text}
    </div>
  );
}

function renderImage(layer: PosterLayer, idx: number) {
  if (!layer.src) {
    return (
      <div
        key={idx}
        className="relative mx-auto rounded-xl bg-white/20 flex items-center justify-center text-white/50 text-xs"
        style={{ width: layer.width || 80, height: layer.height || 80, zIndex: 2 }}
      >
        Logo
      </div>
    );
  }
  return (
    <img
      key={idx}
      src={layer.src}
      alt="logo"
      className="relative mx-auto rounded-xl object-contain"
      style={{ width: layer.width || 80, height: layer.height || 80, zIndex: 2 }}
    />
  );
}

/**
 * Sanitise poster text — strip any translation error messages that may have been
 * saved into the poster JSON before the graceful-fallback fix was applied.
 * These look like: "[Translation failed: Error code: 401 - {'error': ...]"
 */
function sanitizePosterText(text: string): string {
  if (!text) return '';
  // Remove text that is a raw error message (starts with [ and contains 'failed' or 'Error')
  if (text.startsWith('[Translation') || text.startsWith('[Error') ||
      text.includes('Error code:') || text.includes('Translation failed') ||
      /^\[.*error.*\]/i.test(text)) {
    return '';
  }
  return text;
}

function renderText(layer: PosterLayer, idx: number) {
  // Skip empty text layers — prevents blank boxes when translation is unavailable
  const rawText = sanitizePosterText(layer.text || '');
  if (!rawText || rawText.trim() === '') return null;
  // Use cleaned text for rendering
  const displayText = rawText;

  const isTitle = layer.role?.includes('title');
  const isSubtitle = layer.role?.includes('subtitle');
  const isDoctor = layer.role?.includes('doctor');
  const isDate = layer.role?.includes('date') || layer.role?.includes('event');
  const isPrice = layer.role?.includes('price') || layer.role?.includes('offer');

  const defaultStyle: React.CSSProperties = {
    color: layer.styling?.color || '#FFFFFF',
    fontWeight: isTitle ? '800' : (isDoctor ? '700' : '400'),
    fontSize: isTitle
      ? (layer.styling?.fontSize || 22)
      : isSubtitle
      ? (layer.styling?.fontSize || 14)
      : isPrice
      ? (layer.styling?.fontSize || 20)
      : (layer.styling?.fontSize || 13),
    textAlign: (layer.styling?.textAlign as any) || 'center',
    marginTop: layer.styling?.marginTop || (isTitle ? 4 : 2),
    lineHeight: isTitle ? 1.25 : 1.4,
    opacity: layer.styling?.opacity || 1,
    zIndex: 2,
    position: 'relative',
    padding: layer.styling?.padding || '0 4px',
    ...(layer.styling || {}),
  };

  return (
    <div key={idx} style={defaultStyle}>
      {displayText}
    </div>
  );
}

function renderChecklist(layer: PosterLayer, idx: number) {
  if (!layer.items || layer.items.length === 0) return null;
  const raw = layer as any;
  const iconChar: string = raw.icon || '✓';
  const iconColor: string = raw.icon_color || (layer.styling?.color ? '#F59E0B' : '#F59E0B');
  const textColor: string = layer.styling?.color || '#FFFFFF';
  const fSize: number = Number(layer.styling?.fontSize ?? 22);
  const cols: number = raw.columns || 2;
  return (
    <div key={idx} className="relative w-full px-3 py-1" style={{ zIndex: 2 }}>
      <div className={`grid gap-1`} style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
        {layer.items.map((item, i) => (
          <div key={i} className="flex items-start gap-1" style={{ fontSize: fSize, color: textColor, lineHeight: 1.3 }}>
            <span className="shrink-0 mt-0.5" style={{ color: iconColor }}>{iconChar}</span>
            <span>{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function renderCtaButton(layer: PosterLayer, idx: number) {
  if (!layer.text || layer.text.trim() === '') return null;
  const raw = layer as any;
  const bg = layer.styling?.backgroundColor || '#F59E0B';
  const color = layer.styling?.color || '#1a1a1a';
  const fontSize = layer.styling?.fontSize || 28;
  const borderRadius = raw.border_radius || raw.styling?.borderRadius || 12;
  const w = raw.w || raw.width;
  const h = raw.h || raw.height || 64;
  return (
    <div key={idx} className="relative flex justify-center mt-2" style={{ zIndex: 2, width: '100%' }}>
      <div
        className="font-bold text-center flex items-center justify-center"
        style={{
          background: bg,
          color,
          fontSize,
          fontWeight: '800',
          borderRadius,
          height: h,
          width: w || '100%',
          letterSpacing: '0.01em',
          padding: '0 24px',
          boxShadow: `0 4px 16px ${bg}66`,
        }}
      >
        {layer.text}
      </div>
    </div>
  );
}

function renderFooter(layer: PosterLayer, idx: number) {
  const fSize = layer.styling?.fontSize ?? 20;
  const fColor = layer.styling?.color || '#FFFFFF';
  return (
    <div
      key={idx}
      className="relative px-3 py-2 mt-auto w-full"
      style={{
        background: layer.styling?.backgroundColor || 'rgba(0,0,0,0.5)',
        zIndex: 2,
      }}
    >
      {/* Brand name on top row */}
      {(layer as any).brand_name && (
        <div className="text-center font-bold" style={{ color: fColor, fontSize: fSize, lineHeight: 1.3 }}>
          {(layer as any).brand_name}
        </div>
      )}
      <div className="text-center" style={{ color: fColor, fontSize: Math.max(12, Number(fSize) * 0.75), lineHeight: 1.4, opacity: 0.9 }}>
        {layer.text}
      </div>
    </div>
  );
}

function renderDivider(layer: PosterLayer, idx: number) {
  return (
    <div
      key={idx}
      className="relative w-3/4 mx-auto my-1"
      style={{
        height: 1,
        background: layer.styling?.backgroundColor || 'rgba(255,255,255,0.3)',
        zIndex: 2,
      }}
    />
  );
}

/**
 * Decorative geometric shapes — circles, diagonals, rectangles.
 * Absolutely positioned so they don't affect flow layout.
 */
function renderShapes(layer: PosterLayer, idx: number) {
  const shapes = (layer as any).shapes as Array<any> || [];
  return (
    <div
      key={idx}
      className="absolute inset-0 pointer-events-none overflow-hidden"
      style={{ zIndex: 1 }}
    >
      {shapes.map((shape: any, i: number) => {
        const base: React.CSSProperties = {
          position: 'absolute',
          background: shape.color || 'rgba(255,255,255,0.07)',
          ...(shape.x !== undefined    ? { left: shape.x }    : {}),
          ...(shape.right !== undefined ? { right: shape.right } : {}),
          ...(shape.y !== undefined    ? { top: shape.y }     : {}),
          ...(shape.bottom !== undefined ? { bottom: shape.bottom } : {}),
        };
        if (shape.type === 'circle') {
          return (
            <div key={i} style={{
              ...base,
              width: shape.size,
              height: shape.size,
              borderRadius: '50%',
              border: shape.border ? `${shape.border_width || 3}px solid ${shape.border_color || 'rgba(255,255,255,0.15)'}` : undefined,
              background: shape.border ? 'transparent' : base.background,
            }} />
          );
        }
        if (shape.type === 'rect' || shape.type === 'diagonal') {
          return (
            <div key={i} style={{
              ...base,
              width: shape.w || shape.width || 200,
              height: shape.h || shape.height || 200,
              transform: `rotate(${shape.rotate || 0}deg)`,
              borderRadius: shape.radius || 0,
            }} />
          );
        }
        return null;
      })}
    </div>
  );
}

/**
 * Service / feature grid — displays items as attractive color-backed tiles.
 * Used for agency, business, and hospital service posters.
 */
function renderServiceGrid(layer: PosterLayer, idx: number) {
  const raw = layer as any;
  const items: string[] = raw.items || [];
  if (items.length === 0) return null;
  const cols: number = raw.columns || 3;
  const itemBg: string = raw.item_bg || 'rgba(255,255,255,0.13)';
  const textColor: string = layer.styling?.color || '#FFFFFF';
  const iconColor: string = raw.icon_color || '#F59E0B';
  const icon: string = raw.icon || '◆';
  const fSize: number = Number(layer.styling?.fontSize ?? 18);
  return (
    <div key={idx} className="relative w-full px-2 py-1" style={{ zIndex: 2 }}>
      <div className="grid gap-1.5" style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
        {items.map((item, i) => (
          <div
            key={i}
            className="flex flex-col items-center justify-center text-center rounded-xl px-1 py-2"
            style={{
              background: itemBg,
              color: textColor,
              fontSize: fSize,
              lineHeight: 1.25,
              minHeight: fSize * 3.5,
            }}
          >
            <span style={{ color: iconColor, fontSize: fSize * 1.35, lineHeight: 1.2 }}>{icon}</span>
            <span style={{ fontWeight: 700, marginTop: 2, fontSize: fSize * 0.88 }}>{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Stat row — displays 3 stats (value + label) horizontally.
 * Common in agency/business posters: "500+ Clients  •  1200+ Projects  •  98% Success"
 */
function renderStatRow(layer: PosterLayer, idx: number) {
  const raw = layer as any;
  const items: Array<{ value: string; label: string }> = raw.items || [];
  if (items.length === 0) return null;
  const textColor: string = layer.styling?.color || 'rgba(255,255,255,0.7)';
  const valueColor: string = raw.value_color || '#F59E0B';
  const fSize: number = Number(layer.styling?.fontSize ?? 20);
  const divColor: string = raw.divider_color || 'rgba(255,255,255,0.2)';
  return (
    <div key={idx} className="relative w-full px-3 py-2" style={{ zIndex: 2 }}>
      <div
        className="rounded-2xl flex justify-around items-center py-3"
        style={{ background: raw.bg || 'rgba(0,0,0,0.25)' }}
      >
        {items.map((item, i) => (
          <React.Fragment key={i}>
            {i > 0 && <div style={{ width: 1, height: fSize * 2, background: divColor }} />}
            <div className="flex flex-col items-center text-center px-2">
              <span style={{ color: valueColor, fontSize: fSize * 1.7, fontWeight: 800, lineHeight: 1.1 }}>{item.value}</span>
              <span style={{ color: textColor, fontSize: fSize * 0.8, lineHeight: 1.4 }}>{item.label}</span>
            </div>
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

function renderLayer(layer: PosterLayer, idx: number): React.ReactNode {
  switch (layer.type) {
    case 'background': return renderBackground(layer, idx);
    case 'rect': return renderRect(layer, idx);
    case 'badge': return renderBadge(layer, idx);
    case 'image': return renderImage(layer, idx);
    case 'text': return renderText(layer, idx);
    case 'checklist': return renderChecklist(layer, idx);
    case 'cta_button': return renderCtaButton(layer, idx);
    case 'footer': return renderFooter(layer, idx);
    case 'divider': return renderDivider(layer, idx);
    case 'shapes': return renderShapes(layer, idx);
    case 'service_grid': return renderServiceGrid(layer, idx);
    case 'stat_row': return renderStatRow(layer, idx);
    default: return null;
  }
}

// Platform label display
const PLATFORM_LABELS: Record<string, string> = {
  instagram_square: '📷 Instagram Square',
  instagram_story: '📱 Instagram Story',
  facebook_post: '👥 Facebook Post',
  whatsapp_share: '💬 WhatsApp',
  linkedin_banner: '💼 LinkedIn',
  twitter_post: '🐦 Twitter',
  youtube_thumbnail: '▶️ YouTube Thumbnail',
};

export default function PosterRenderer({ posterJson, scale = 0.35, showDownload = false }: PosterRendererProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const dims = posterJson.dimensions || { width: 1080, height: 1080 };

  // Normalize all layers: fix background type & map flat backend props → styling
  const layers = (posterJson.layers || []).map(normalizeLayer);

  // Background layer must be absolutely positioned; rest flow inside
  const bgLayer = layers.find(l => l.type === 'background');
  const contentLayers = layers.filter(l => l.type !== 'background');

  // Padding relative to the full (unscaled) poster width
  const padPx = Math.round(dims.width * 0.035);

  const handleDownload = () => {
    if (!containerRef.current) return;

    // Build a standalone HTML page that renders the poster at full resolution
    const dims = posterJson.dimensions || { width: 1080, height: 1080 };
    const platform = posterJson.platform || 'poster';
    const platformLabel = PLATFORM_LABELS[platform] || platform;

    // Grab the inner poster element HTML
    const inner = containerRef.current.cloneNode(true) as HTMLElement;

    // Reset transform/scale so it renders at native resolution
    inner.style.transform = 'none';
    inner.style.transformOrigin = 'top left';
    inner.style.position = 'relative';
    inner.style.width = `${dims.width}px`;
    inner.style.height = `${dims.height}px`;

    const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <title>${platformLabel} — SRP AI Marketing OS</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Noto+Sans:wght@400;600;700;800&family=Noto+Sans+Telugu:wght@400;700&family=Noto+Sans+Devanagari:wght@400;700&display=swap" rel="stylesheet"/>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #f0f0f0; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; font-family: 'Inter', sans-serif; }
    .poster-wrap { width: ${dims.width}px; height: ${dims.height}px; position: relative; overflow: hidden; border-radius: 8px; box-shadow: 0 8px 40px rgba(0,0,0,0.25); }
    .poster-title { margin-bottom: 12px; font-size: 16px; color: #555; }
    @media print {
      body { background: white; margin: 0; padding: 0; min-height: auto; }
      .poster-wrap { border-radius: 0; box-shadow: none; }
      .no-print { display: none !important; }
      @page { size: ${dims.width}px ${dims.height}px; margin: 0; }
    }
  </style>
</head>
<body>
  <p class="poster-title no-print">${platformLabel} — ${dims.width}×${dims.height}px</p>
  <div class="poster-wrap">
    ${inner.outerHTML}
  </div>
  <div class="no-print" style="margin-top:16px; display:flex; gap:12px;">
    <button onclick="window.print()" style="padding:10px 24px;background:#4F46E5;color:white;border:none;border-radius:8px;cursor:pointer;font-size:14px;font-weight:600;">⬇ Save as PDF / Image</button>
    <button onclick="window.close()" style="padding:10px 24px;background:#e5e7eb;color:#374151;border:none;border-radius:8px;cursor:pointer;font-size:14px;">✕ Close</button>
  </div>
  <script>
    // Auto-trigger print after fonts load
    // window.addEventListener('load', () => setTimeout(() => window.print(), 800));
  </script>
</body>
</html>`;

    const win = window.open('', '_blank', `width=${Math.min(dims.width + 120, 1400)},height=${Math.min(dims.height + 180, 900)}`);
    if (win) {
      win.document.write(html);
      win.document.close();
    }
  };

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="text-xs font-medium text-gray-500">
        {PLATFORM_LABELS[posterJson.platform || ''] || posterJson.platform}
        {' '}— {dims.width}×{dims.height}
      </div>

      {/*
        Outer wrapper clips to the scaled size.
        Inner poster renders at full poster dimensions, then CSS-scaled down.
        This ensures font sizes (e.g. 54px heading on a 1080px poster) look
        proportionally correct at any thumbnail size.
      */}
      <div
        className="relative rounded-xl shadow-lg"
        style={{
          width: dims.width * scale,
          height: dims.height * scale,
          overflow: 'hidden',
        }}
      >
        <div
          ref={containerRef}
          className="absolute top-0 left-0 flex flex-col"
          style={{
            width: dims.width,
            height: dims.height,
            transform: `scale(${scale})`,
            transformOrigin: 'top left',
            fontFamily: 'Inter, Noto Sans, sans-serif',
          }}
        >
          {/* Background fills the full poster */}
          {bgLayer ? (
            <div
              className="absolute inset-0"
              style={{ background: resolveBackground(bgLayer.colors), zIndex: 0 }}
            />
          ) : (
            // Fallback: dark gradient so white text is readable
            <div
              className="absolute inset-0"
              style={{ background: 'linear-gradient(135deg, #1E3A8A, #1E40AF)', zIndex: 0 }}
            />
          )}

          {/* Content layers stack vertically */}
          <div
            className="relative flex flex-col w-full h-full items-center justify-start overflow-hidden"
            style={{ padding: `${padPx}px`, zIndex: 1 }}
          >
            {contentLayers.map((layer, i) => renderLayer(layer, i))}
          </div>
        </div>
      </div>

      {showDownload && (
        <button
          onClick={handleDownload}
          className="text-xs px-4 py-1.5 rounded-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold shadow-sm flex items-center gap-1"
        >
          ⬇ Download / Preview
        </button>
      )}
    </div>
  );
}
