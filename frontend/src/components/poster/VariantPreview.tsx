import React, { useState } from 'react';
import PosterRenderer from './PosterRenderer';
import LanguageToggle from './LanguageToggle';

interface PosterData {
  platform?: string;
  dimensions?: { width: number; height: number };
  layers?: any[];
  bilingual_content?: Record<string, string>;
  meta?: Record<string, any>;
}

/**
 * Swap text layers to their regional equivalents when the user picks the
 * regional preview language.
 *
 * Strategy:
 *  - Every layer with role ending in `_english` gets its text swapped with
 *    the matching `_regional` layer (same role prefix) if that layer exists
 *    and has a non-empty `text` field.
 *  - Standalone `_regional` layers are then removed (they were only needed for
 *    the bilingual combined view; in regional-only mode we embed them inline).
 *  - If a `_regional` match has no text we leave the English text in place so
 *    the poster never renders a blank block.
 */
function getPosterForView(poster: PosterData, view: 'english' | 'regional'): PosterData {
  if (view === 'english' || !poster.layers) return poster;

  const layers = poster.layers;

  // Build lookup: english_role_key → regional layer
  const regionalByEnglishKey = new Map<string, any>();
  layers.forEach(layer => {
    const role: string = layer.role || '';
    if (role.endsWith('_regional')) {
      regionalByEnglishKey.set(role.replace('_regional', '_english'), layer);
    }
  });

  const processed = layers
    .map(layer => {
      const role: string = layer.role || '';
      if (role.endsWith('_english')) {
        const reg = regionalByEnglishKey.get(role);
        if (reg && reg.text && reg.text.trim() !== '') {
          return {
            ...layer,
            text: reg.text,
            font_family: reg.font_family || layer.font_family,
            font_size: reg.font_size || layer.font_size,
          };
        }
        return layer; // keep English if no regional text available
      }
      if (role.endsWith('_regional')) return null; // already merged above
      return layer;
    })
    .filter(Boolean);

  return { ...poster, layers: processed };
}

/** Check if the poster actually has any regional text in its layers */
function hasRegionalContent(poster: PosterData): boolean {
  return (poster.layers || []).some(
    l => (l.role || '').endsWith('_regional') && l.text && l.text.trim() !== ''
  );
}

interface VariantPreviewProps {
  variants: Record<string, PosterData>; // platform → poster_json
  secondaryLanguage?: string;
  captions?: Record<string, string>;
}

const PLATFORM_ORDER = [
  'instagram_square',
  'instagram_story',
  'facebook_post',
  'whatsapp_share',
  'linkedin_banner',
];

const PLATFORM_ICONS: Record<string, string> = {
  instagram_square: '📷',
  instagram_story: '📱',
  facebook_post: '👥',
  whatsapp_share: '💬',
  linkedin_banner: '💼',
};

const PLATFORM_LABELS: Record<string, string> = {
  instagram_square: 'Instagram',
  instagram_story: 'Story',
  facebook_post: 'Facebook',
  whatsapp_share: 'WhatsApp',
  linkedin_banner: 'LinkedIn',
};

export default function VariantPreview({ variants, secondaryLanguage = 'telugu', captions }: VariantPreviewProps) {
  const [activePlatform, setActivePlatform] = useState<string>(
    PLATFORM_ORDER.find(p => variants[p]) || Object.keys(variants)[0] || ''
  );
  const [langView, setLangView] = useState<'english' | 'regional'>('english');

  const platforms = PLATFORM_ORDER.filter(p => variants[p]);
  const activePoster = variants[activePlatform];
  const posterForView = activePoster ? getPosterForView(activePoster, langView) : null;
  const regionalAvailable = activePoster ? hasRegionalContent(activePoster) : false;

  if (!activePoster || !posterForView) {
    return <div className="text-gray-400 text-sm text-center py-8">No variants generated yet.</div>;
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Platform tabs */}
      <div className="flex gap-2 flex-wrap">
        {platforms.map(p => (
          <button
            key={p}
            type="button"
            onClick={() => setActivePlatform(p)}
            className={`flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium border-2 transition-all ${
              activePlatform === p
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-200 text-gray-600 hover:border-gray-300'
            }`}
          >
            <span>{PLATFORM_ICONS[p]}</span>
            <span>{PLATFORM_LABELS[p]}</span>
          </button>
        ))}
      </div>

      {/* Language toggle */}
      <div className="flex items-center gap-3 flex-wrap">
        <span className="text-sm text-gray-500">Preview language:</span>
        <LanguageToggle
          primaryLang="english"
          secondaryLang={secondaryLanguage}
          active={langView}
          onChange={setLangView}
        />
        {langView === 'regional' && !regionalAvailable && (
          <span className="text-xs text-amber-600 bg-amber-50 border border-amber-200 px-2.5 py-1 rounded-full">
            ⚠ Regional translation unavailable — showing English
          </span>
        )}
        {langView === 'regional' && regionalAvailable && (
          <span className="text-xs text-emerald-600 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full">
            ✓ Showing {secondaryLanguage} translation
          </span>
        )}
      </div>

      {/* Active poster */}
      <div className="flex flex-wrap gap-6 items-start justify-center min-h-[420px]">
        <PosterRenderer
          posterJson={posterForView}
          scale={activePlatform === 'instagram_story' ? 0.29 : 0.40}
          showDownload
        />

        {/* Caption panel */}
        {captions && captions[activePlatform] && (
          <div className="max-w-xs bg-gray-50 rounded-xl p-4 border border-gray-200">
            <div className="text-xs font-semibold text-gray-500 uppercase mb-2">Caption</div>
            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
              {captions[activePlatform]}
            </p>
          </div>
        )}
      </div>

      {/* Thumbnail strip */}
      <div className="flex gap-3 overflow-x-auto pb-2">
        {platforms.map(p => (
          <div
            key={p}
            onClick={() => setActivePlatform(p)}
            className={`cursor-pointer rounded-lg overflow-hidden border-2 flex-shrink-0 transition-all ${
              p === activePlatform ? 'border-blue-500 shadow-md' : 'border-gray-200 opacity-70 hover:opacity-100'
            }`}
          >
            <PosterRenderer posterJson={variants[p]} scale={0.12} />
          </div>
        ))}
      </div>
    </div>
  );
}
