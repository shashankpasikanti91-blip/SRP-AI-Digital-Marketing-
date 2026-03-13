import React, { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';
import PosterRenderer from '../components/poster/PosterRenderer';
import VariantPreview from '../components/poster/VariantPreview';

interface PosterVariant {
  id: string;
  platform: string;
  campaign_data: Record<string, any>;
  poster_json: any;
  social_caption?: string;
  hashtags?: string[];
  created_at: string;
  status: string;
}

const PLATFORM_META: Record<string, { icon: string; label: string; color: string; bg: string }> = {
  instagram_square: { icon: '📸', label: 'Instagram',  color: 'text-pink-600',   bg: 'bg-pink-50 border-pink-200'   },
  instagram_story:  { icon: '📱', label: 'Story',       color: 'text-purple-600', bg: 'bg-purple-50 border-purple-200' },
  facebook_post:    { icon: '👥', label: 'Facebook',   color: 'text-blue-600',   bg: 'bg-blue-50 border-blue-200'    },
  whatsapp_share:   { icon: '💬', label: 'WhatsApp',   color: 'text-green-600',  bg: 'bg-green-50 border-green-200'  },
  linkedin_banner:  { icon: '💼', label: 'LinkedIn',   color: 'text-indigo-600', bg: 'bg-indigo-50 border-indigo-200' },
};

const LANG_LABELS: Record<string, string> = {
  telugu: 'తెలుగు', hindi: 'हिन्दी', tamil: 'தமிழ்', kannada: 'ಕನ್ನಡ',
  malayalam: 'മലയാളം', bengali: 'বাংলা', marathi: 'मराठी',
  gujarati: 'ગુજરાતી', punjabi: 'ਪੰਜਾਬੀ', odia: 'ଓଡ଼ିଆ',
  malay: 'BM', indonesian: 'ID', thai: 'ไทย', chinese_simplified: '中文',
};

const PLATFORMS = ['all', 'instagram_square', 'instagram_story', 'facebook_post', 'whatsapp_share', 'linkedin_banner'];

export default function PosterPreview() {
  const qc = useQueryClient();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [platformFilter, setPlatformFilter] = useState('all');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  // Bulk select
  const [selectMode, setSelectMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const PAGE_SIZE = 20;

  function toggleSelect(id: string) {
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  function selectAll() {
    setSelectedIds(new Set(filtered.map(v => v.id)));
  }

  function clearSelection() {
    setSelectedIds(new Set());
    setSelectMode(false);
  }

  const bulkDeleteMutation = useMutation({
    mutationFn: async (ids: string[]) => {
      await Promise.all(ids.map(id => api.delete(`/posters/variants/${id}`)));
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['poster-variants'] });
      setSelectedIds(new Set());
      setSelectMode(false);
    },
  });

  const { data: variants = [], isLoading, isError } = useQuery<PosterVariant[]>({
    queryKey: ['poster-variants', page],
    queryFn: () =>
      api.get('/posters/variants', { params: { page: page + 1, page_size: PAGE_SIZE } })
        .then(r => r.data?.variants ?? r.data ?? []),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/posters/variants/${id}`).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['poster-variants'] });
      setSelectedId(null);
    },
  });

  const selectedVariant = variants.find(v => v.id === selectedId);

  const copyCaption = useCallback((text: string, id: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    });
  }, []);

  // Group variants by campaign date+template
  const filtered = platformFilter === 'all' ? variants : variants.filter(v => v.platform === platformFilter);
  const grouped = filtered.reduce((acc, v) => {
    const key = `${v.campaign_data?.template_slug || 'unknown'}_${v.created_at?.slice(0, 10)}`;
    if (!acc[key]) acc[key] = [];
    acc[key].push(v);
    return acc;
  }, {} as Record<string, PosterVariant[]>);

  const totalPosters = variants.length;
  const langSet = new Set(variants.map(v => v.campaign_data?.secondary_language).filter(Boolean));
  const uniqueCampaigns = new Set(variants.map(v => v.campaign_data?.campaign_id)).size;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/40">
      {/* ── Hero header ── */}
      <div className="bg-gradient-to-r from-indigo-700 via-blue-700 to-blue-600 px-6 py-10 text-white shadow-lg">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <span className="text-4xl">🖼️</span>
                <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight">Poster Gallery</h1>
              </div>
              <p className="text-blue-200 text-sm md:text-base">All generated campaign creatives — download, copy & publish instantly.</p>
            </div>
            <a
              href="/app/campaign-builder"
              className="inline-flex items-center gap-2 px-6 py-3 bg-white text-blue-700 rounded-xl font-bold hover:bg-blue-50 shadow-md text-sm transition-all"
            >
              ✨ New Campaign
            </a>
          </div>

          {/* Stats strip */}
          {totalPosters > 0 && (
            <div className="flex flex-wrap gap-6 mt-6 pt-6 border-t border-white/20 text-sm">
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold">{totalPosters}</span>
                <span className="text-blue-200">Posters Created</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold">{uniqueCampaigns || '—'}</span>
                <span className="text-blue-200">Campaigns</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold">{langSet.size || 1}</span>
                <span className="text-blue-200">Languages</span>
              </div>
              {langSet.size > 0 && (
                <div className="flex items-center gap-1 flex-wrap">
                  {[...langSet].map(lang => (
                    <span key={lang} className="px-2 py-0.5 bg-white/20 rounded-full text-xs font-medium">
                      {LANG_LABELS[lang as string] || lang}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">

        {/* Platform filter tabs + bulk action toolbar */}
        {!selectedId && !isLoading && variants.length > 0 && (
          <div className="flex gap-2 flex-wrap mb-4 items-center justify-between">
            <div className="flex gap-2 flex-wrap">
              {PLATFORMS.map(p => {
                const meta = PLATFORM_META[p];
                const active = platformFilter === p;
                return (
                  <button
                    key={p}
                    onClick={() => setPlatformFilter(p)}
                    className={`px-4 py-1.5 rounded-full text-xs font-semibold border transition-all ${
                      active
                        ? 'bg-indigo-600 text-white border-indigo-600 shadow'
                        : 'bg-white text-gray-600 border-gray-200 hover:border-indigo-300'
                    }`}
                  >
                    {meta ? `${meta.icon} ${meta.label}` : '🌐 All'}
                  </button>
                );
              })}
            </div>
            <button
              onClick={() => { setSelectMode(s => !s); setSelectedIds(new Set()); }}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold border transition-all ${
                selectMode ? 'bg-red-50 text-red-600 border-red-300' : 'bg-white text-gray-600 border-gray-200 hover:border-gray-400'
              }`}
            >
              {selectMode ? '✕ Cancel Select' : '☑ Select'}
            </button>
          </div>
        )}

        {/* Bulk delete toolbar (shown when items selected) */}
        {selectedIds.size > 0 && !selectedId && (
          <div className="flex items-center gap-3 mb-4 px-4 py-3 bg-red-50 border border-red-200 rounded-xl">
            <span className="text-sm font-semibold text-red-700">{selectedIds.size} poster{selectedIds.size !== 1 ? 's' : ''} selected</span>
            <button onClick={selectAll} className="text-xs text-indigo-600 hover:underline">Select all {filtered.length}</button>
            <button onClick={clearSelection} className="text-xs text-gray-500 hover:underline">Clear</button>
            <div className="ml-auto">
              <button
                disabled={bulkDeleteMutation.isPending}
                onClick={() => {
                  if (window.confirm(`Delete ${selectedIds.size} poster${selectedIds.size !== 1 ? 's' : ''}? This cannot be undone.`)) {
                    bulkDeleteMutation.mutate([...selectedIds]);
                  }
                }}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white rounded-lg text-sm font-semibold transition-all"
              >
                {bulkDeleteMutation.isPending ? 'Deleting…' : `🗑 Delete ${selectedIds.size} Selected`}
              </button>
            </div>
          </div>
        )}

        {isLoading && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {Array.from({ length: 10 }).map((_, i) => (
              <div key={i} className="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 animate-pulse">
                <div className="bg-gray-200 h-48" />
                <div className="p-3 space-y-2">
                  <div className="h-3 bg-gray-200 rounded w-3/4" />
                  <div className="h-2 bg-gray-100 rounded w-1/2" />
                </div>
              </div>
            ))}
          </div>
        )}

        {isError && (
          <div className="flex flex-col items-center justify-center py-20 text-red-400">
            <div className="text-5xl mb-3">⚠️</div>
            <div className="text-lg font-semibold">Could not load gallery</div>
            <p className="text-sm mt-2 text-gray-500">Make sure the backend is running and you are logged in.</p>
            <a href="/app/campaign-builder" className="mt-4 px-5 py-2 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700">
              Create New Campaign
            </a>
          </div>
        )}

        {!isLoading && !isError && variants.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-gray-400">
            <div className="text-6xl mb-4">🎨</div>
            <div className="text-xl font-semibold mb-2">No posters yet</div>
            <p className="text-sm mb-6">Create your first campaign to start generating bilingual posters.</p>
            <a
              href="/app/campaign-builder"
              className="px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700"
            >
              Build Your First Campaign
            </a>
          </div>
        )}

        {/* Gallery — grouped by campaign */}
        {!selectedId && !isError && filtered.length > 0 && (
          <div className="space-y-8">
            {Object.entries(grouped).map(([key, group]) => {
              const sample = group[0];
              const slug = sample.campaign_data?.template_slug?.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase()) || 'Campaign';
              const city = sample.campaign_data?.city || '';
              const date = new Date(sample.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
              const secLang = sample.campaign_data?.secondary_language;
              return (
                <div key={key}>
                  {/* Campaign group header */}
                  <div className="flex items-center gap-3 mb-3">
                    <div className="flex-1 flex items-center gap-2">
                      <span className="text-lg font-bold text-gray-800">{slug}</span>
                      {city && <span className="text-sm text-gray-500">· {city}</span>}
                      <span className="text-xs text-gray-400">· {date}</span>
                      {secLang && (
                        <span className="px-2 py-0.5 bg-indigo-100 text-indigo-700 text-xs font-semibold rounded-full">
                          🌐 EN + {LANG_LABELS[secLang] || secLang}
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-gray-400">{group.length} variant{group.length !== 1 ? 's' : ''}</span>
                  </div>

                  {/* Variant cards */}
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                    {group.map(variant => {
                      const pmeta = PLATFORM_META[variant.platform] || { icon: '🖼', label: variant.platform, color: 'text-gray-600', bg: 'bg-gray-50 border-gray-200' };
                      const isSelected = selectedIds.has(variant.id);
                      return (
                        <div
                          key={variant.id}
                          onClick={() => selectMode ? toggleSelect(variant.id) : setSelectedId(variant.id)}
                          className={`cursor-pointer group bg-white rounded-2xl shadow-sm overflow-hidden transition-all duration-200 ${
                            isSelected
                              ? 'border-2 border-red-400 shadow-red-100 shadow-md'
                              : 'border border-gray-100 hover:shadow-xl hover:-translate-y-1 hover:border-blue-300'
                          }`}
                        >
                          {/* Poster thumbnail */}
                          <div className="relative overflow-hidden bg-gray-50 flex items-center justify-center" style={{ minHeight: 180 }}>
                            <PosterRenderer posterJson={variant.poster_json} scale={0.18} />
                            {/* Platform badge overlay */}
                            <div className={`absolute top-2 left-2 flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border ${pmeta.bg} ${pmeta.color}`}>
                              {pmeta.icon} {pmeta.label}
                            </div>
                            {/* Select mode checkbox */}
                            {selectMode && (
                              <div className={`absolute top-2 right-2 w-5 h-5 rounded border-2 flex items-center justify-center text-xs font-bold transition-all ${
                                isSelected ? 'bg-red-500 border-red-500 text-white' : 'bg-white border-gray-300'
                              }`}>
                                {isSelected && '✓'}
                              </div>
                            )}
                            {/* Hover delete (non-select mode) */}
                            {!selectMode && (
                              <button
                                onClick={e => {
                                  e.stopPropagation();
                                  if (window.confirm('Delete this poster?')) deleteMutation.mutate(variant.id);
                                }}
                                className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 bg-red-500 hover:bg-red-600 text-white rounded-full shadow text-xs"
                                title="Delete poster"
                              >
                                🗑
                              </button>
                            )}
                            {/* Hover overlay (non-select mode) */}
                            {!selectMode && (
                              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors flex items-center justify-center">
                                <span className="opacity-0 group-hover:opacity-100 transition-opacity bg-white/90 text-gray-800 text-xs font-bold px-3 py-1.5 rounded-full shadow">
                                  View →
                                </span>
                              </div>
                            )}
                          </div>

                          {/* Card footer */}
                          <div className="p-3 border-t border-gray-50">
                            {variant.campaign_data?.secondary_language ? (
                              <div className="flex items-center gap-1.5">
                                <span className="text-indigo-600 text-xs">🌐</span>
                                <span className="text-xs font-semibold text-indigo-700">
                                  {LANG_LABELS[variant.campaign_data.secondary_language] || variant.campaign_data.secondary_language} Bilingual
                                </span>
                              </div>
                            ) : (
                              <div className="text-xs text-gray-500 truncate">{slug}</div>
                            )}
                            <div className="text-xs text-gray-400 mt-0.5 truncate">
                              {variant.campaign_data?.city || variant.campaign_data?.industry || '—'}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* ── Detail view ── */}
        {selectedId && selectedVariant && (() => {
          const pmeta = PLATFORM_META[selectedVariant.platform] || { icon: '🖼', label: selectedVariant.platform, color: 'text-gray-600', bg: 'bg-gray-50 border-gray-200' };
          const slug = selectedVariant.campaign_data?.template_slug?.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase()) || 'Poster';
          const secLang = selectedVariant.campaign_data?.secondary_language;
          return (
            <div>
              {/* Breadcrumb / toolbar */}
              <div className="flex flex-wrap items-center gap-3 mb-6">
                <button
                  onClick={() => setSelectedId(null)}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-white border border-gray-200 text-gray-600 hover:bg-gray-50 text-sm font-medium shadow-sm"
                >
                  ← Gallery
                </button>
                <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-semibold ${pmeta.bg} ${pmeta.color}`}>
                  {pmeta.icon} {pmeta.label}
                </div>
                <div className="text-gray-800 font-bold text-lg hidden sm:block">{slug}</div>
                {secLang && (
                  <span className="px-3 py-1 bg-indigo-100 text-indigo-700 text-xs font-bold rounded-full">
                    🌐 Bilingual: EN + {LANG_LABELS[secLang] || secLang}
                  </span>
                )}
                <div className="ml-auto flex gap-2">
                  <button
                    onClick={() => { if (window.confirm('Delete this poster?')) deleteMutation.mutate(selectedId!); }}
                    className="px-3 py-2 text-sm text-red-500 hover:bg-red-50 rounded-lg border border-red-200 font-medium"
                  >
                    🗑 Delete
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
                {/* Poster — left column (wide) */}
                <div className="lg:col-span-3 bg-white rounded-2xl shadow border border-gray-100 p-6 flex flex-col items-center">
                  <PosterRenderer posterJson={selectedVariant.poster_json} scale={0.50} showDownload />
                  {/* Sibling variants */}
                  <div className="mt-5 w-full">
                    <p className="text-xs text-gray-400 mb-2 font-semibold uppercase tracking-wide">Other variants in this campaign</p>
                    <div className="flex gap-3 overflow-x-auto pb-1">
                      {variants
                        .filter(v => v.id !== selectedId &&
                          v.campaign_data?.template_slug === selectedVariant.campaign_data?.template_slug &&
                          v.created_at?.slice(0, 10) === selectedVariant.created_at?.slice(0, 10)
                        )
                        .map(v => {
                          const vm = PLATFORM_META[v.platform] || { icon: '🖼', label: v.platform, color: 'text-gray-500', bg: 'bg-gray-50 border-gray-200' };
                          return (
                            <button
                              key={v.id}
                              onClick={() => setSelectedId(v.id)}
                              className={`shrink-0 flex flex-col items-center gap-1 p-2 rounded-xl border text-xs font-semibold ${vm.bg} ${vm.color} hover:shadow-md transition-all`}
                            >
                              <div className="rounded-lg overflow-hidden" style={{ width: 60, height: 60 }}>
                                <PosterRenderer posterJson={v.poster_json} scale={0.05} />
                              </div>
                              <span>{vm.icon} {vm.label}</span>
                            </button>
                          );
                        })}
                    </div>
                  </div>
                </div>

                {/* Sidebar — right column */}
                <div className="lg:col-span-2 space-y-4">
                  {/* Campaign details card */}
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
                    <h3 className="font-bold text-gray-700 text-sm uppercase tracking-wide mb-3">📋 Campaign Details</h3>
                    <div className="space-y-2">
                      {Object.entries(selectedVariant.campaign_data || {}).map(([k, val]) =>
                        val && typeof val !== 'object' ? (
                          <div key={k} className="flex gap-2 text-sm">
                            <span className="text-gray-400 w-28 shrink-0 capitalize">{k.replace(/_/g, ' ')}</span>
                            <span className="text-gray-800 font-semibold">{String(val)}</span>
                          </div>
                        ) : null
                      )}
                    </div>
                  </div>

                  {/* Social caption */}
                  {selectedVariant.social_caption && (
                    <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-2xl border border-indigo-100 p-5">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-bold text-gray-700 text-sm uppercase tracking-wide">📝 Social Caption</h3>
                        <button
                          onClick={() => copyCaption(selectedVariant.social_caption!, selectedVariant.id)}
                          className={`text-xs px-3 py-1 rounded-full border font-semibold transition-all ${
                            copiedId === selectedVariant.id
                              ? 'bg-green-100 text-green-700 border-green-300'
                              : 'bg-white text-indigo-600 border-indigo-200 hover:bg-indigo-50'
                          }`}
                        >
                          {copiedId === selectedVariant.id ? '✓ Copied!' : '📋 Copy'}
                        </button>
                      </div>
                      <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                        {selectedVariant.social_caption}
                      </p>
                    </div>
                  )}

                  {/* Hashtags */}
                  {selectedVariant.hashtags && selectedVariant.hashtags.length > 0 && (
                    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
                      <h3 className="font-bold text-gray-700 text-xs uppercase tracking-wide mb-2">🏷️ Hashtags</h3>
                      <div className="flex flex-wrap gap-1.5">
                        {selectedVariant.hashtags.map(tag => (
                          <span key={tag} className="px-2 py-1 bg-blue-50 text-blue-600 text-xs rounded-full font-medium">{tag}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Dev JSON panel */}
                  <details className="bg-gray-950 rounded-2xl overflow-hidden text-xs cursor-pointer">
                    <summary className="px-4 py-3 text-gray-400 font-mono hover:text-gray-300 select-none">🔧 Poster JSON (debug)</summary>
                    <pre className="overflow-auto max-h-64 px-4 pb-4 text-green-400 leading-relaxed">
                      {JSON.stringify(selectedVariant.poster_json, null, 2)}
                    </pre>
                  </details>
                </div>
              </div>
            </div>
          );
        })()}

        {/* Pagination */}
        {!selectedId && (variants.length >= PAGE_SIZE || page > 0) && (
          <div className="flex justify-center gap-3 mt-10">
            {page > 0 && (
              <button
                onClick={() => setPage(p => p - 1)}
                className="px-5 py-2.5 bg-white border border-gray-200 rounded-xl text-sm font-semibold shadow-sm hover:border-blue-300"
              >
                ← Previous
              </button>
            )}
            {variants.length >= PAGE_SIZE && (
              <button
                onClick={() => setPage(p => p + 1)}
                className="px-5 py-2.5 bg-indigo-600 text-white rounded-xl text-sm font-semibold shadow-sm hover:bg-indigo-700"
              >
                Next Page →
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
