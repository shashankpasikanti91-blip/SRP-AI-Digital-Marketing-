import React, { useState } from 'react';
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

const PLATFORM_ICONS: Record<string, string> = {
  instagram_square: '📷',
  instagram_story: '📱',
  facebook_post: '👥',
  whatsapp_share: '💬',
  linkedin_banner: '💼',
};

export default function PosterPreview() {
  const qc = useQueryClient();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 12;

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

  // Group variants by campaign_data.template_slug + created date proximity
  const grouped = variants.reduce((acc, v) => {
    const key = `${v.campaign_data?.template_slug || 'unknown'}_${v.created_at?.slice(0, 10)}`;
    if (!acc[key]) acc[key] = [];
    acc[key].push(v);
    return acc;
  }, {} as Record<string, PosterVariant[]>);

  return (
    <div className="min-h-screen bg-gray-50 px-4 py-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">🖼️ Poster Gallery</h1>
            <p className="text-gray-500 mt-1">All generated campaign posters saved here.</p>
          </div>
          <a
            href="/app/campaign-builder"
            className="px-5 py-2.5 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 text-sm"
          >
            + New Campaign
          </a>
        </div>

        {isLoading && (
          <div className="flex items-center justify-center py-20 text-gray-400">
            <div className="animate-spin text-4xl mr-3">⏳</div>
            <span className="text-lg">Loading posters...</span>
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

        {/* Gallery grid */}
        {!selectedId && !isError && variants.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {variants.map(variant => (
              <div
                key={variant.id}
                onClick={() => setSelectedId(variant.id)}
                className="cursor-pointer group bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md hover:border-blue-300 transition-all"
              >
                <div className="relative bg-gray-100 flex items-center justify-center p-2">
                  <PosterRenderer posterJson={variant.poster_json} scale={0.15} />
                  <div className="absolute top-2 right-2 bg-black/60 text-white text-xs px-2 py-0.5 rounded-full">
                    {PLATFORM_ICONS[variant.platform]} {variant.platform?.replace('_', ' ')}
                  </div>
                </div>
                <div className="p-3">
                  <div className="font-semibold text-gray-800 text-xs truncate">
                    {variant.campaign_data?.template_slug?.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase())}
                  </div>
                  <div className="text-xs text-gray-400 mt-0.5">
                    {variant.campaign_data?.city || '—'} •{' '}
                    {new Date(variant.created_at).toLocaleDateString()}
                  </div>
                  {variant.campaign_data?.secondary_language && (
                    <span className="inline-block mt-1 px-2 py-0.5 bg-indigo-50 text-indigo-600 text-xs rounded-full">
                      EN + {variant.campaign_data.secondary_language}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Detail view */}
        {selectedId && selectedVariant && (
          <div>
            <div className="flex items-center gap-3 mb-6">
              <button
                onClick={() => setSelectedId(null)}
                className="px-3 py-2 rounded-lg bg-white border border-gray-200 text-gray-600 hover:bg-gray-50 text-sm"
              >
                ← Back to Gallery
              </button>
              <div className="text-gray-800 font-semibold">
                {selectedVariant.campaign_data?.template_slug?.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase())}
                {' '}— {selectedVariant.campaign_data?.city}
              </div>
              <div className="ml-auto">
                <button
                  onClick={() => { if (window.confirm('Delete this poster?')) deleteMutation.mutate(selectedId); }}
                  className="px-3 py-2 text-sm text-red-500 hover:bg-red-50 rounded-lg border border-red-200"
                >
                  🗑 Delete
                </button>
              </div>
            </div>

            {/* Poster + caption */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                <PosterRenderer posterJson={selectedVariant.poster_json} scale={0.45} showDownload />
              </div>

              <div className="space-y-4">
                {/* Campaign info */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
                  <h3 className="font-semibold text-gray-800 mb-3">📋 Campaign Details</h3>
                  <div className="space-y-2 text-sm">
                    {Object.entries(selectedVariant.campaign_data || {}).map(([key, val]) => (
                      val && typeof val !== 'object' ? (
                        <div key={key} className="flex gap-2">
                          <span className="text-gray-500 w-32 shrink-0">{key.replace(/_/g, ' ')}</span>
                          <span className="text-gray-800 font-medium">{String(val)}</span>
                        </div>
                      ) : null
                    ))}
                  </div>
                </div>

                {/* Caption */}
                {selectedVariant.social_caption && (
                  <div className="bg-gray-50 rounded-2xl border border-gray-200 p-5">
                    <h3 className="font-semibold text-gray-800 mb-2">📝 Social Caption</h3>
                    <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                      {selectedVariant.social_caption}
                    </p>
                  </div>
                )}

                {/* Hashtags */}
                {selectedVariant.hashtags && selectedVariant.hashtags.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {selectedVariant.hashtags.map(tag => (
                      <span key={tag} className="px-2 py-1 bg-blue-50 text-blue-600 text-xs rounded-full">{tag}</span>
                    ))}
                  </div>
                )}

                {/* Poster JSON (developer view) */}
                <details className="bg-gray-900 rounded-2xl p-4 text-xs text-green-400 cursor-pointer">
                  <summary className="text-gray-400 mb-2">🔧 View Poster JSON</summary>
                  <pre className="overflow-auto max-h-64 mt-2">
                    {JSON.stringify(selectedVariant.poster_json, null, 2)}
                  </pre>
                </details>
              </div>
            </div>
          </div>
        )}

        {/* Pagination */}
        {!selectedId && (variants.length >= PAGE_SIZE || page > 0) && (
          <div className="flex justify-center gap-3 mt-8">
            {page > 0 && (
              <button onClick={() => setPage(p => p - 1)} className="px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm">
                ← Previous
              </button>
            )}
            {variants.length >= PAGE_SIZE && (
              <button onClick={() => setPage(p => p + 1)} className="px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm">
                Next →
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
