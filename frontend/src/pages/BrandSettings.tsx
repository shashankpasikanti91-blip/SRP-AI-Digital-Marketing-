import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';

// Type for brand profile form
interface BrandProfileForm {
  brand_name: string;
  tagline?: string;
  logo_url?: string;
  primary_color: string;
  secondary_color: string;
  accent_color: string;
  font_family: string;
  regional_font_family: string;
  footer_text?: string;
  phone_numbers?: string; // comma-separated in form
  address?: string;
  email?: string;
  website?: string;
  industry?: string;
  city?: string;
  state?: string;
  default_languages?: string; // comma-separated
  watermark_text?: string;
}

const FONT_OPTIONS = ['Inter', 'Poppins', 'Roboto', 'Open Sans', 'Lato', 'Nunito'];
const REGIONAL_FONT_OPTIONS = ['Noto Sans', 'Noto Sans Telugu', 'Noto Sans Hindi', 'Noto Sans Tamil', 'Noto Sans Kannada', 'Noto Sans Malayalam'];
const INDUSTRY_OPTIONS = [
  { value: 'hospital', label: '🏥 Hospital / Clinic' },
  { value: 'marketing_agency', label: '📢 Marketing Agency' },
  { value: 'recruitment_agency', label: '👥 Recruitment Agency' },
  { value: 'restaurant', label: '🍽️ Restaurant / Cafe' },
  { value: 'retail', label: '🛍️ Retail / Fashion' },
  { value: 'education', label: '🎓 Education' },
  { value: 'real_estate', label: '🏢 Real Estate' },
  { value: 'other', label: '⚙️ Other' },
];

const LANGUAGE_OPTIONS = [
  { value: 'english', label: '🇬🇧 English' },
  { value: 'telugu', label: 'తెలుగు Telugu' },
  { value: 'hindi', label: 'हिंदी Hindi' },
  { value: 'tamil', label: 'தமிழ் Tamil' },
  { value: 'kannada', label: 'ಕನ್ನಡ Kannada' },
  { value: 'malayalam', label: 'മലയാളം Malayalam' },
];

export default function BrandSettings() {
  const qc = useQueryClient();
  const [saved, setSaved] = useState(false);
  const [selectedLangs, setSelectedLangs] = useState<string[]>(['english', 'telugu']);

  const { data: brandProfile, isLoading } = useQuery({
    queryKey: ['brand-profile'],
    queryFn: () => api.get('/posters/brand-profile').then(r => r.data).catch(() => null),
  });

  const { register, handleSubmit, reset, watch, formState: { errors } } = useForm<BrandProfileForm>({
    defaultValues: {
      primary_color: '#1E40AF',
      secondary_color: '#FFFFFF',
      accent_color: '#F59E0B',
      font_family: 'Inter',
      regional_font_family: 'Noto Sans',
      brand_name: '',
    },
  });

  // Populate form when brand profile loads  
  useEffect(() => {
    if (brandProfile) {
      reset({
        brand_name: brandProfile.brand_name || '',
        tagline: brandProfile.tagline || '',
        logo_url: brandProfile.logo_url || '',
        primary_color: brandProfile.primary_color || '#1E40AF',
        secondary_color: brandProfile.secondary_color || '#FFFFFF',
        accent_color: brandProfile.accent_color || '#F59E0B',
        font_family: brandProfile.font_family || 'Inter',
        regional_font_family: brandProfile.regional_font_family || 'Noto Sans',
        footer_text: brandProfile.footer_text || '',
        phone_numbers: (brandProfile.phone_numbers || []).join(', '),
        address: brandProfile.address || '',
        email: brandProfile.email || '',
        website: brandProfile.website || '',
        industry: brandProfile.industry || '',
        city: brandProfile.city || '',
        state: brandProfile.state || '',
        watermark_text: brandProfile.watermark_text || '',
      });
      if (brandProfile.default_languages) {
        setSelectedLangs(brandProfile.default_languages);
      }
    }
  }, [brandProfile, reset]);

  const saveMutation = useMutation({
    mutationFn: (data: any) =>
      api.post('/posters/brand-profile', data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['brand-profile'] });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    },
  });

  const onSubmit = (data: BrandProfileForm) => {
    const payload = {
      ...data,
      phone_numbers: data.phone_numbers
        ? data.phone_numbers.split(',').map(p => p.trim()).filter(Boolean)
        : [],
      default_languages: selectedLangs,
    };
    saveMutation.mutate(payload);
  };

  const primaryColor = watch('primary_color') || '#1E40AF';
  const accentColor = watch('accent_color') || '#F59E0B';

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Brand Settings</h1>
        <p className="text-gray-500 mt-1">
          Set your brand identity once — it will be reused across all campaigns and posters automatically.
        </p>
      </div>

      {/* Brand Preview Card */}
      <div
        className="rounded-2xl p-6 mb-8 text-white flex items-center gap-6 shadow-lg"
        style={{ background: `linear-gradient(135deg, ${primaryColor}, ${accentColor})` }}
      >
        <div className="w-16 h-16 bg-white/20 rounded-xl flex items-center justify-center text-2xl font-bold">
          {watch('brand_name')?.[0] || '🏷'}
        </div>
        <div>
          <div className="text-2xl font-bold">{watch('brand_name') || 'Your Brand Name'}</div>
          <div className="text-white/80 text-sm mt-1">{watch('tagline') || 'Your brand tagline here'}</div>
          <div className="flex gap-3 mt-2">
            <div className="w-6 h-6 rounded-full border-2 border-white" style={{ background: watch('primary_color') }}></div>
            <div className="w-6 h-6 rounded-full border-2 border-white" style={{ background: watch('secondary_color') }}></div>
            <div className="w-6 h-6 rounded-full border-2 border-white" style={{ background: watch('accent_color') }}></div>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">

        {/* Basic Info */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">🏷️ Brand Identity</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Brand Name *</label>
              <input
                {...register('brand_name', { required: true })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g. Apollo Hospital Kothagudem"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tagline</label>
              <input
                {...register('tagline')}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                placeholder="e.g. Caring for you, always"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Industry</label>
              <select
                {...register('industry')}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
              >
                <option value="">Select industry...</option>
                {INDUSTRY_OPTIONS.map(o => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Logo URL</label>
              <input
                {...register('logo_url')}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                placeholder="https://your-domain.com/logo.png"
              />
            </div>
          </div>
        </div>

        {/* Colors & Fonts */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">🎨 Colors & Fonts</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Primary Color</label>
              <div className="flex items-center gap-2">
                <input type="color" {...register('primary_color')} className="w-10 h-10 rounded cursor-pointer" />
                <input {...register('primary_color')} className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono" placeholder="#1E40AF" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Secondary Color</label>
              <div className="flex items-center gap-2">
                <input type="color" {...register('secondary_color')} className="w-10 h-10 rounded cursor-pointer" />
                <input {...register('secondary_color')} className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono" placeholder="#FFFFFF" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Accent Color</label>
              <div className="flex items-center gap-2">
                <input type="color" {...register('accent_color')} className="w-10 h-10 rounded cursor-pointer" />
                <input {...register('accent_color')} className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono" placeholder="#F59E0B" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">English Font</label>
              <select {...register('font_family')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                {FONT_OPTIONS.map(f => <option key={f} value={f}>{f}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Regional Font</label>
              <select {...register('regional_font_family')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                {REGIONAL_FONT_OPTIONS.map(f => <option key={f} value={f}>{f}</option>)}
              </select>
            </div>
          </div>
        </div>

        {/* Regional Languages */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-2">🌐 Default Languages</h2>
          <p className="text-sm text-gray-500 mb-4">Select which languages your campaigns default to for bilingual poster generation.</p>
          <div className="flex flex-wrap gap-3">
            {LANGUAGE_OPTIONS.map(lang => (
              <button
                key={lang.value}
                type="button"
                onClick={() => {
                  setSelectedLangs(prev =>
                    prev.includes(lang.value)
                      ? prev.filter(l => l !== lang.value)
                      : [...prev, lang.value]
                  );
                }}
                className={`px-4 py-2 rounded-full text-sm font-medium border-2 transition-all ${
                  selectedLangs.includes(lang.value)
                    ? 'bg-blue-600 border-blue-600 text-white'
                    : 'bg-white border-gray-300 text-gray-600 hover:border-blue-400'
                }`}
              >
                {lang.label}
              </button>
            ))}
          </div>
        </div>

        {/* Contact & Location */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">📍 Contact & Location</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone Numbers (comma-separated)</label>
              <input {...register('phone_numbers')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="040-12345678, +91-9876543210" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input type="email" {...register('email')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="info@yourbrand.com" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
              <input {...register('city')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="Kothagudem" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
              <input {...register('state')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="Telangana" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Address</label>
              <textarea {...register('address')} rows={2} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="123 Main Road, Kothagudem, Telangana - 507101" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Footer Text (appears on all posters)</label>
              <input {...register('footer_text')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="Government Approved | NABH Accredited | Open 24x7" />
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex items-center gap-4">
          <button
            type="submit"
            disabled={saveMutation.isPending}
            className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-sm transition-colors disabled:opacity-50"
          >
            {saveMutation.isPending ? '⏳ Saving...' : '💾 Save Brand Profile'}
          </button>
          {saved && (
            <span className="text-green-600 font-medium flex items-center gap-1">
              ✅ Brand profile saved!
            </span>
          )}
          {saveMutation.isError && (
            <span className="text-red-500 text-sm">Failed to save. Please try again.</span>
          )}
        </div>
      </form>
    </div>
  );
}
