/**
 * PosterRenderer — SRP AI Marketing OS
 *
 * Renders poster JSON as pixel-accurate, visually stunning HTML/CSS.
 * Uses absolute positioning matching x/y/w/h coords from the poster JSON.
 * Handles ALL layer types produced by poster_generator.py + seed scripts:
 *   background, gradient, solid, shapes, accent_strip, logo, badge,
 *   title, subtitle, text, price_block, original_price, date_block,
 *   cta, cta_button, footer, service_grid, stat_row, checklist, divider,
 *   image, rect.
 */
import React, { useRef } from 'react';

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

interface RawShape {
  type: string;
  size?: number;
  x?: number; y?: number;
  right?: number; bottom?: number;
  w?: number; h?: number;
  width?: number; height?: number;
  color?: string;
  border?: boolean;
  border_width?: number;
  border_color?: string;
  rotate?: number;
  radius?: number;
}

interface RawLayer {
  type: string;
  value?: string;
  text?: string;
  x?: number; y?: number;
  w?: number; h?: number;
  width?: number; height?: number;
  color?: string;
  bg?: string;
  fill?: string;
  text_color?: string;
  font_size?: number;
  bold?: boolean;
  align?: string;
  strikethrough?: boolean;
  gradient?: string;
  colors?: string[];
  border_radius?: number;
  shapes?: RawShape[];
  items?: string[] | Array<{ value: string; label: string }>;
  columns?: number;
  icon?: string;
  icon_color?: string;
  item_bg?: string;
  value_color?: string;
  src?: string;
  brand_name?: string;
  phone?: string;
  address?: string;
  styling?: Record<string, any>;
  [key: string]: any;
}

interface PosterData {
  platform?: string;
  dimensions?: { width: number; height: number };
  layers?: RawLayer[];
  meta?: Record<string, any>;
  bilingual_content?: Record<string, string>;
}

interface PosterRendererProps {
  posterJson: PosterData;
  scale?: number;
  showDownload?: boolean;
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

const FONT = "'Inter','Noto Sans Devanagari','Noto Sans Telugu','Noto Sans',sans-serif";

/** Strip raw API error messages that leaked into poster JSON. */
function sanitize(s: string): string {
  if (!s) return '';
  if (
    s.startsWith('[Translation') || s.startsWith('[Error') ||
    s.includes('Error code:') || s.includes('Translation failed') ||
    /^\[.*error.*\]/i.test(s)
  ) return '';
  return s;
}

/** Resolve text from a layer — supports `value` (backend) and `text` (legacy). */
function txt(l: RawLayer): string {
  return sanitize(String(l.value ?? l.text ?? ''));
}

/** Resolve CSS background from gradient string OR colors array OR solid color. */
function resolveBg(l: RawLayer): string {
  if (l.gradient) {
    const g = l.gradient.trim();
    return g.startsWith('linear-gradient') || g.startsWith('radial-gradient') ? g : `linear-gradient(${g})`;
  }
  if (l.colors) {
    return l.colors.length === 1 ? l.colors[0] : `linear-gradient(135deg, ${l.colors.join(', ')})`;
  }
  return l.color || l.bg || l.fill || '#1E3A8A';
}

/** Absolute position style for a layer using its x/y/w/h coords. */
function pos(l: RawLayer, extra?: React.CSSProperties): React.CSSProperties {
  const hasPos = l.x !== undefined && l.y !== undefined;
  const w = l.w ?? l.width;
  const h = l.h ?? l.height;
  return {
    position: hasPos ? 'absolute' : 'relative',
    ...(hasPos ? { left: l.x, top: l.y } : {}),
    ...(w !== undefined ? { width: w } : {}),
    ...(h !== undefined ? { height: h } : {}),
    ...extra,
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// Individual layer renderers
// ─────────────────────────────────────────────────────────────────────────────

const LayerBackground = ({ l }: { l: RawLayer }) => (
  <div className="absolute inset-0" style={{ background: resolveBg(l), zIndex: 0 }} />
);

const LayerShapes = ({ l }: { l: RawLayer }) => (
  <div className="absolute inset-0 pointer-events-none overflow-hidden" style={{ zIndex: 1 }}>
    {(l.shapes || []).map((s, i) => {
      const base: React.CSSProperties = {
        position: 'absolute',
        left: s.x, top: s.y,
        right: s.right, bottom: s.bottom,
      };
      if (s.type === 'circle') return (
        <div key={i} style={{
          ...base,
          width: s.size, height: s.size,
          borderRadius: '50%',
          background: s.border ? 'transparent' : (s.color || 'rgba(255,255,255,0.06)'),
          border: s.border ? `${s.border_width || 2}px solid ${s.border_color || s.color || 'rgba(255,255,255,0.12)'}` : undefined,
        }} />
      );
      return (
        <div key={i} style={{
          ...base,
          width: s.w ?? s.width ?? 200,
          height: s.h ?? s.height ?? 200,
          background: s.color || 'rgba(255,255,255,0.06)',
          transform: s.rotate ? `rotate(${s.rotate}deg)` : undefined,
          borderRadius: s.radius ?? 0,
        }} />
      );
    })}
  </div>
);

const LayerAccentStrip = ({ l }: { l: RawLayer }) => (
  <div style={{
    position: 'absolute', left: 0, top: 0, right: 0,
    height: l.height ?? l.h ?? 8,
    background: l.color || '#F59E0B',
    zIndex: 3,
  }} />
);

const LayerLogo = ({ l }: { l: RawLayer }) => {
  const label = txt(l) || String(l.value || '').slice(0, 2).toUpperCase() || 'SR';
  const h = l.h ?? l.height ?? 60;
  return (
    <div style={{
      ...pos(l, { zIndex: 4 }),
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: l.src ? 'transparent' : 'rgba(255,255,255,0.15)',
      borderRadius: 10,
      backdropFilter: 'blur(4px)',
      border: l.src ? 'none' : '1px solid rgba(255,255,255,0.25)',
      overflow: 'hidden',
    }}>
      {l.src
        ? <img src={l.src} alt="logo" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
        : <span style={{ color: '#FFF', fontWeight: 900, fontSize: h * 0.45, fontFamily: FONT, letterSpacing: 1 }}>{label}</span>
      }
    </div>
  );
};

const LayerBadge = ({ l }: { l: RawLayer }) => {
  const label = txt(l); if (!label) return null;
  const bg = l.bg || l.color || '#F59E0B';
  const fs = l.font_size || 24;
  return (
    <div style={{
      ...pos(l, { zIndex: 5 }),
      display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
      background: bg,
      color: l.text_color || '#000',
      fontSize: fs, fontWeight: l.bold !== false ? 900 : 700, fontFamily: FONT,
      borderRadius: l.border_radius ?? 8,
      letterSpacing: '0.06em',
      padding: `${fs * 0.25}px ${fs * 0.6}px`,
      textTransform: 'uppercase' as const,
      boxShadow: `0 4px 16px ${bg}66`,
      whiteSpace: 'nowrap',
      textAlign: 'center',
    }}>{label}</div>
  );
};

const LayerTitle = ({ l }: { l: RawLayer }) => {
  const label = txt(l); if (!label) return null;
  const fs = l.font_size || 48;
  return (
    <div style={{
      ...pos(l, { zIndex: 5 }),
      fontSize: fs, fontWeight: 900, fontFamily: FONT,
      color: l.color || l.text_color || '#FFF',
      textAlign: (l.align || 'center') as React.CSSProperties['textAlign'],
      lineHeight: 1.15,
      textShadow: '0 2px 12px rgba(0,0,0,0.45)',
      letterSpacing: '-0.01em',
    }}>{label}</div>
  );
};

const LayerSubtitle = ({ l }: { l: RawLayer }) => {
  const label = txt(l); if (!label) return null;
  const fs = l.font_size || 26;
  return (
    <div style={{
      ...pos(l, { zIndex: 5 }),
      fontSize: fs, fontWeight: 600, fontFamily: FONT,
      color: l.color || l.text_color || '#BFDBFE',
      textAlign: (l.align || 'center') as React.CSSProperties['textAlign'],
      lineHeight: 1.3,
    }}>{label}</div>
  );
};

const LayerText = ({ l }: { l: RawLayer }) => {
  const label = txt(l); if (!label) return null;
  const fs = l.font_size || 22;
  return (
    <div style={{
      ...pos(l, { zIndex: 5 }),
      fontSize: fs, fontWeight: l.bold ? 700 : 400, fontFamily: FONT,
      color: l.color || l.text_color || '#FFF',
      textAlign: (l.align || 'left') as React.CSSProperties['textAlign'],
      lineHeight: 1.4,
    }}>{label}</div>
  );
};

const LayerPriceBlock = ({ l }: { l: RawLayer }) => {
  const label = txt(l); if (!label) return null;
  const fs = l.font_size || 72;
  const col = l.color || '#F59E0B';
  return (
    <div style={{
      ...pos(l, { zIndex: 5 }),
      fontSize: fs, fontWeight: 900, fontFamily: FONT,
      color: col,
      textAlign: (l.align || 'center') as React.CSSProperties['textAlign'],
      lineHeight: 1,
      filter: `drop-shadow(0 0 24px ${col}88)`,
      letterSpacing: '-0.03em',
    }}>{label}</div>
  );
};

const LayerOriginalPrice = ({ l }: { l: RawLayer }) => {
  const label = txt(l); if (!label) return null;
  const fs = l.font_size || 28;
  return (
    <div style={{
      ...pos(l, { zIndex: 5 }),
      fontSize: fs, fontWeight: 500, fontFamily: FONT,
      color: l.color || '#9CA3AF',
      textAlign: (l.align || 'center') as React.CSSProperties['textAlign'],
      textDecoration: 'line-through',
      opacity: 0.8,
    }}>{label}</div>
  );
};

const LayerDateBlock = ({ l }: { l: RawLayer }) => {
  const label = txt(l); if (!label) return null;
  const fs = l.font_size || 24;
  return (
    <div style={{
      ...pos(l, { zIndex: 5 }),
      fontSize: fs, fontWeight: l.bold ? 700 : 500, fontFamily: FONT,
      color: l.color || '#FFF',
      textAlign: (l.align || 'center') as React.CSSProperties['textAlign'],
      lineHeight: 1.4,
      background: 'rgba(0,0,0,0.28)',
      borderRadius: 8,
      padding: '6px 16px',
      backdropFilter: 'blur(4px)',
    }}>{label}</div>
  );
};

const LayerCta = ({ l }: { l: RawLayer }) => {
  const label = txt(l); if (!label) return null;
  const bg = l.bg || l.color || '#F59E0B';
  const fs = l.font_size || 32;
  return (
    <div style={{
      ...pos(l, {
        zIndex: 6,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }),
      background: bg,
      color: l.text_color || '#000',
      fontSize: fs, fontWeight: 900, fontFamily: FONT,
      borderRadius: l.border_radius ?? 12,
      boxShadow: `0 6px 28px ${bg}88, inset 0 1px 0 rgba(255,255,255,0.2)`,
      textAlign: 'center',
      letterSpacing: '0.01em',
    }}>{label}</div>
  );
};

const LayerFooter = ({ l }: { l: RawLayer }) => {
  const label = txt(l);
  const bg = l.bg || '#0F172A';
  const fs = l.font_size || 20;
  return (
    <div style={{
      ...pos(l, {
        zIndex: 6,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        overflow: 'hidden',
      }),
      background: bg,
      color: l.text_color || '#FFF',
      fontSize: fs, fontFamily: FONT, fontWeight: 500,
      textAlign: 'center', padding: '0 20px',
    }}>{label}</div>
  );
};

const LayerServiceGrid = ({ l }: { l: RawLayer }) => {
  const items = (l.items || []) as string[];
  if (!items.length) return null;
  const cols = l.columns || 2;
  const itemBg = l.item_bg || 'rgba(255,255,255,0.1)';
  const iconColor = l.icon_color || '#F59E0B';
  const icon = l.icon || '✓';
  const fs = l.font_size || 19;
  return (
    <div style={{
      ...pos(l, { zIndex: 5 }),
      display: 'grid',
      gridTemplateColumns: `repeat(${cols}, 1fr)`,
      gap: 8,
      overflow: 'hidden',
    }}>
      {items.map((item, i) => (
        <div key={i} style={{
          background: itemBg,
          backdropFilter: 'blur(6px)',
          borderRadius: 10,
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
          padding: '10px 8px',
          textAlign: 'center',
          border: '1px solid rgba(255,255,255,0.09)',
          minHeight: fs * 3.5,
        }}>
          <span style={{ color: iconColor, fontSize: fs * 1.3, lineHeight: 1 }}>{icon}</span>
          <span style={{ color: '#FFF', fontSize: fs * 0.85, fontWeight: 700, fontFamily: FONT, marginTop: 4, lineHeight: 1.2 }}>{item}</span>
        </div>
      ))}
    </div>
  );
};

const LayerStatRow = ({ l }: { l: RawLayer }) => {
  type SI = { value: string; label: string };
  const items = (l.items || []) as SI[];
  if (!items.length) return null;
  const valColor = l.value_color || '#F59E0B';
  const fs = l.font_size || 20;
  return (
    <div style={{
      ...pos(l, { zIndex: 5 }),
      display: 'flex', alignItems: 'stretch',
      background: l.bg || 'rgba(0,0,0,0.3)',
      borderRadius: 12,
      backdropFilter: 'blur(8px)',
      border: '1px solid rgba(255,255,255,0.09)',
      overflow: 'hidden',
    }}>
      {items.map((item, i) => (
        <React.Fragment key={i}>
          {i > 0 && <div style={{ width: 1, background: 'rgba(255,255,255,0.15)', flexShrink: 0 }} />}
          <div style={{
            flex: 1, display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center',
            padding: `${fs * 0.5}px ${fs * 0.4}px`,
          }}>
            <span style={{ color: valColor, fontSize: fs * 1.7, fontWeight: 900, fontFamily: FONT, lineHeight: 1 }}>{item.value}</span>
            <span style={{ color: 'rgba(255,255,255,0.7)', fontSize: fs * 0.75, fontWeight: 500, fontFamily: FONT, marginTop: 2, textAlign: 'center', lineHeight: 1.2 }}>{item.label}</span>
          </div>
        </React.Fragment>
      ))}
    </div>
  );
};

const LayerChecklist = ({ l }: { l: RawLayer }) => {
  const items = (l.items || []) as string[];
  if (!items.length) return null;
  const iconColor = l.icon_color || '#F59E0B';
  const icon = l.icon || '✓';
  const fs = l.font_size || 22;
  const textColor = l.color || l.text_color || '#FFF';
  const cols = l.columns || 1;
  return (
    <div style={{
      ...pos(l, { zIndex: 5 }),
      display: 'grid',
      gridTemplateColumns: `repeat(${cols}, 1fr)`,
      gap: 6,
    }}>
      {items.map((item, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8, fontSize: fs, color: textColor, fontFamily: FONT, lineHeight: 1.35 }}>
          <span style={{ color: iconColor, flexShrink: 0, marginTop: 1 }}>{icon}</span>
          <span>{item}</span>
        </div>
      ))}
    </div>
  );
};

const LayerDivider = ({ l }: { l: RawLayer }) => (
  <div style={{
    ...pos(l, { zIndex: 4 }),
    background: l.color || l.bg || 'rgba(255,255,255,0.2)',
    height: l.h ?? l.height ?? 1,
  }} />
);

// ─────────────────────────────────────────────────────────────────────────────
// Dispatcher
// ─────────────────────────────────────────────────────────────────────────────

function RenderLayer({ l, idx }: { l: RawLayer; idx: number }) {
  switch (l.type) {
    case 'background': case 'gradient': case 'solid':
      return <LayerBackground key={idx} l={l} />;
    case 'shapes':
      return <LayerShapes key={idx} l={l} />;
    case 'accent_strip':
      return <LayerAccentStrip key={idx} l={l} />;
    case 'logo':
      return <LayerLogo key={idx} l={l} />;
    case 'badge':
      return <LayerBadge key={idx} l={l} />;
    case 'title':
      return <LayerTitle key={idx} l={l} />;
    case 'subtitle':
      return <LayerSubtitle key={idx} l={l} />;
    case 'text':
      return <LayerText key={idx} l={l} />;
    case 'price_block':
      return <LayerPriceBlock key={idx} l={l} />;
    case 'original_price':
      return <LayerOriginalPrice key={idx} l={l} />;
    case 'date_block':
      return <LayerDateBlock key={idx} l={l} />;
    case 'cta': case 'cta_button':
      return <LayerCta key={idx} l={l} />;
    case 'footer':
      return <LayerFooter key={idx} l={l} />;
    case 'service_grid':
      return <LayerServiceGrid key={idx} l={l} />;
    case 'stat_row':
      return <LayerStatRow key={idx} l={l} />;
    case 'checklist':
      return <LayerChecklist key={idx} l={l} />;
    case 'divider':
      return <LayerDivider key={idx} l={l} />;
    case 'image':
      return l.src ? (
        <img key={idx} src={l.src} alt="" style={{ ...pos(l, { objectFit: 'cover' as const, borderRadius: l.border_radius ?? 0, zIndex: 4 }) }} />
      ) : null;
    case 'rect':
      return <div key={idx} style={{ ...pos(l, { background: l.bg || l.fill || l.color || '#F59E0B', borderRadius: l.border_radius ?? 0, zIndex: 3 }) }} />;
    default:
      return null;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Platform labels
// ─────────────────────────────────────────────────────────────────────────────

const PLATFORM_LABELS: Record<string, string> = {
  instagram_square: '📷 Instagram Square',
  instagram_story:  '📱 Instagram Story',
  facebook_post:    '👥 Facebook Post',
  whatsapp_share:   '💬 WhatsApp',
  linkedin_banner:  '💼 LinkedIn',
  twitter_post:     '🐦 Twitter',
  youtube_thumbnail:'▶️ YouTube Thumbnail',
};

// ─────────────────────────────────────────────────────────────────────────────
// Main export
// ─────────────────────────────────────────────────────────────────────────────

export default function PosterRenderer({
  posterJson,
  scale = 0.35,
  showDownload = false,
}: PosterRendererProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const dims = posterJson.dimensions || { width: 1080, height: 1080 };
  const layers = posterJson.layers || [];

  const handleDownload = () => {
    if (!containerRef.current) return;
    const inner = containerRef.current.cloneNode(true) as HTMLElement;
    inner.style.transform = 'none';
    inner.style.transformOrigin = 'top left';
    inner.style.position = 'relative';
    inner.style.width = `${dims.width}px`;
    inner.style.height = `${dims.height}px`;
    const platformLabel = PLATFORM_LABELS[posterJson.platform || ''] || posterJson.platform || 'Poster';
    const html = `<!DOCTYPE html>
<html><head><meta charset="UTF-8"/>
<title>${platformLabel} — SRP AI Marketing OS</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=Noto+Sans:wght@400;700;800&family=Noto+Sans+Telugu:wght@400;700&family=Noto+Sans+Devanagari:wght@400;700&display=swap" rel="stylesheet"/>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#111;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;font-family:Inter,sans-serif}
.wrap{width:${dims.width}px;height:${dims.height}px;position:relative;overflow:hidden;border-radius:8px;box-shadow:0 8px 60px rgba(0,0,0,0.6)}
.title{margin-bottom:12px;font-size:14px;color:#888;letter-spacing:.05em}
.btns{margin-top:16px;display:flex;gap:12px}
button{padding:10px 28px;border:none;border-radius:8px;cursor:pointer;font-size:14px;font-weight:700}
.pb{background:#4F46E5;color:#fff}.cb{background:#374151;color:#fff}
@media print{body{background:#fff}.title,.btns{display:none}@page{size:${dims.width}px ${dims.height}px;margin:0}}
</style>
</head>
<body>
<p class="title">${platformLabel} — ${dims.width}×${dims.height}px</p>
<div class="wrap">${inner.outerHTML}</div>
<div class="btns">
  <button class="pb" onclick="window.print()">⬇ Save / Print</button>
  <button class="cb" onclick="window.close()">✕ Close</button>
</div>
</body></html>`;
    const win = window.open('', '_blank', `width=${Math.min(dims.width + 100, 1400)},height=${Math.min(dims.height + 160, 920)}`);
    if (win) { win.document.write(html); win.document.close(); }
  };

  const hasBg = layers.some(l => ['background','gradient','solid'].includes(l.type));

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="text-xs font-medium text-gray-500">
        {PLATFORM_LABELS[posterJson.platform || ''] || posterJson.platform}
        {' — '}{dims.width}×{dims.height}
      </div>

      <div
        className="rounded-xl shadow-2xl ring-1 ring-white/10"
        style={{ width: dims.width * scale, height: dims.height * scale, overflow: 'hidden', position: 'relative', flexShrink: 0 }}
      >
        <div
          ref={containerRef}
          style={{
            position: 'absolute', top: 0, left: 0,
            width: dims.width, height: dims.height,
            transform: `scale(${scale})`,
            transformOrigin: 'top left',
            fontFamily: FONT,
            overflow: 'hidden',
          }}
        >
          {/* Fallback bg */}
          {!hasBg && (
            <div className="absolute inset-0" style={{ background: 'linear-gradient(135deg,#1E3A8A,#1E40AF)', zIndex: 0 }} />
          )}

          {layers.map((l, i) => <RenderLayer key={i} l={l} idx={i} />)}
        </div>
      </div>

      {showDownload && (
        <button
          onClick={handleDownload}
          className="text-xs px-4 py-1.5 rounded-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold shadow flex items-center gap-1 transition-colors"
        >
          ⬇ Download / Preview
        </button>
      )}
    </div>
  );
}
