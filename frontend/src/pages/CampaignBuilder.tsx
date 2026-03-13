import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import api from '../services/api';
import VariantPreview from '../components/poster/VariantPreview';

// Template definitions — all major industry types
const TEMPLATE_CATEGORIES = [
  { id: 'healthcare', label: '🏥 Healthcare', color: 'blue' },
  { id: 'recruitment', label: '💼 Recruitment', color: 'indigo' },
  { id: 'food', label: '🍽️ Food & Restaurant', color: 'red' },
  { id: 'retail', label: '🛍️ Retail & Products', color: 'orange' },
  { id: 'real_estate', label: '🏠 Real Estate', color: 'amber' },
  { id: 'education', label: '📚 Education', color: 'sky' },
  { id: 'beauty', label: '💄 Beauty & Wellness', color: 'pink' },
  { id: 'events', label: '🎉 Events & Services', color: 'purple' },
];

const TEMPLATES = [
  // ── HEALTHCARE ────────────────────────────────────────────────────
  {
    slug: 'orthopedic_health_camp',
    label: 'Orthopaedic Health Camp',
    icon: '🦴',
    category: 'healthcare',
    description: 'Bone, joint & spine health camp',
    color: 'blue',
    fields: ['doctor_name', 'doctor_qualification', 'department', 'date_range', 'event_time', 'offer_price', 'original_price', 'services', 'locality'],
  },
  {
    slug: 'diabetes_health_camp',
    label: 'Diabetes Health Camp',
    icon: '💉',
    category: 'healthcare',
    description: 'Blood sugar tests & diabetes awareness',
    color: 'green',
    fields: ['doctor_name', 'doctor_qualification', 'department', 'date_range', 'event_time', 'offer_price', 'services', 'locality'],
  },
  {
    slug: 'cardiac_checkup_camp',
    label: 'Cardiac / Heart Camp',
    icon: '❤️',
    category: 'healthcare',
    description: 'ECG, BP check & cardiology consultation',
    color: 'rose',
    fields: ['doctor_name', 'doctor_qualification', 'department', 'date_range', 'event_time', 'offer_price', 'services', 'locality'],
  },
  {
    slug: 'eye_camp',
    label: 'Eye Check-up Camp',
    icon: '👁️',
    category: 'healthcare',
    description: 'Vision tests, cataract & eye surgery camps',
    color: 'teal',
    fields: ['doctor_name', 'doctor_qualification', 'department', 'date_range', 'event_time', 'offer_price', 'services', 'locality'],
  },
  {
    slug: 'dental_camp',
    label: 'Dental Health Camp',
    icon: '🦷',
    category: 'healthcare',
    description: 'Teeth cleaning, check-up & dental offers',
    color: 'cyan',
    fields: ['doctor_name', 'doctor_qualification', 'department', 'date_range', 'event_time', 'offer_price', 'services', 'locality'],
  },
  {
    slug: 'general_health_camp',
    label: 'General Health Camp',
    icon: '🏥',
    category: 'healthcare',
    description: 'Multi-speciality free health screening camp',
    color: 'blue',
    fields: ['doctor_name', 'doctor_qualification', 'department', 'date_range', 'event_time', 'offer_price', 'services', 'locality'],
  },
  {
    slug: 'pharmacy_sale',
    label: 'Pharmacy / Medicine Offer',
    icon: '💊',
    category: 'healthcare',
    description: 'Medicine discounts & pharmacy offers',
    color: 'green',
    fields: ['offer_price', 'original_price', 'services', 'date_range', 'locality'],
  },
  // ── RECRUITMENT ───────────────────────────────────────────────────
  {
    slug: 'job_opening',
    label: 'Job Opening',
    icon: '👔',
    category: 'recruitment',
    description: 'Hiring announcements for urgent positions',
    color: 'indigo',
    fields: ['job_title', 'vacancies', 'salary_range', 'experience', 'services'],
  },
  {
    slug: 'walkin_drive',
    label: 'Walk-in Drive',
    icon: '🚶',
    category: 'recruitment',
    description: 'Walk-in interview events with drive details',
    color: 'purple',
    fields: ['job_title', 'vacancies', 'experience', 'date_range', 'event_time', 'locality'],
  },
  // ── FOOD & RESTAURANT ─────────────────────────────────────────────
  {
    slug: 'restaurant_offer',
    label: 'Restaurant Offer',
    icon: '🍽️',
    category: 'food',
    description: 'Food deals, festive menus & combo offers',
    color: 'red',
    fields: ['offer_price', 'original_price', 'services', 'date_range'],
  },
  {
    slug: 'bakery_offer',
    label: 'Bakery / Sweet Shop',
    icon: '🎂',
    category: 'food',
    description: 'Cakes, sweets & seasonal bakery offers',
    color: 'orange',
    fields: ['offer_price', 'services', 'date_range'],
  },
  {
    slug: 'hotel_event',
    label: 'Hotel / Banquet Event',
    icon: '🏨',
    category: 'food',
    description: 'Hotel launches, buffets & catering events',
    color: 'amber',
    fields: ['offer_price', 'services', 'date_range', 'event_time', 'locality'],
  },
  // ── RETAIL & PRODUCTS ─────────────────────────────────────────────
  {
    slug: 'retail_discount',
    label: 'Retail / Shop Discount',
    icon: '🛍️',
    category: 'retail',
    description: 'Season sale, discount & clearance offers',
    color: 'orange',
    fields: ['offer_price', 'original_price', 'services', 'date_range'],
  },
  {
    slug: 'furniture_sale',
    label: 'Furniture Sale',
    icon: '🛋️',
    category: 'retail',
    description: 'Furniture, home decor & interiors sale',
    color: 'amber',
    fields: ['offer_price', 'original_price', 'services', 'date_range'],
  },
  {
    slug: 'garment_sale',
    label: 'Garment / Clothing Sale',
    icon: '👗',
    category: 'retail',
    description: 'Fashion, clothing & textile discount offers',
    color: 'pink',
    fields: ['offer_price', 'original_price', 'services', 'date_range'],
  },
  {
    slug: 'electronics_sale',
    label: 'Electronics Offer',
    icon: '📱',
    category: 'retail',
    description: 'Mobile, electronics & appliance offers',
    color: 'slate',
    fields: ['offer_price', 'original_price', 'services', 'date_range'],
  },
  // ── REAL ESTATE ───────────────────────────────────────────────────
  {
    slug: 'real_estate_launch',
    label: 'Property Launch',
    icon: '🏗️',
    category: 'real_estate',
    description: 'New project, flat & plot launch events',
    color: 'amber',
    fields: ['offer_price', 'original_price', 'services', 'date_range', 'event_time', 'locality'],
  },
  {
    slug: 'rental_property',
    label: 'Rental / PG / Hostel',
    icon: '🔑',
    category: 'real_estate',
    description: 'Property rentals, PG & hostel availability',
    color: 'teal',
    fields: ['offer_price', 'services', 'locality'],
  },
  // ── EDUCATION ─────────────────────────────────────────────────────
  {
    slug: 'coaching_institute',
    label: 'Coaching Institute',
    icon: '📖',
    category: 'education',
    description: 'NEET, JEE, IAS, degree & skill courses',
    color: 'sky',
    fields: ['offer_price', 'original_price', 'services', 'date_range', 'locality'],
  },
  {
    slug: 'school_admission',
    label: 'School Admissions',
    icon: '🎒',
    category: 'education',
    description: 'CBSE/State school admissions open',
    color: 'indigo',
    fields: ['offer_price', 'services', 'date_range', 'locality'],
  },
  {
    slug: 'skill_training',
    label: 'Skill Training / Course',
    icon: '🎓',
    category: 'education',
    description: 'Computer, spoken English & skill courses',
    color: 'purple',
    fields: ['offer_price', 'original_price', 'services', 'date_range', 'locality'],
  },
  // ── BEAUTY & WELLNESS ─────────────────────────────────────────────
  {
    slug: 'beauty_salon',
    label: 'Beauty Parlour / Salon',
    icon: '💄',
    category: 'beauty',
    description: 'Haircut, bridal, facial & parlour offers',
    color: 'pink',
    fields: ['offer_price', 'original_price', 'services', 'date_range'],
  },
  {
    slug: 'gym_offer',
    label: 'Gym / Fitness Offer',
    icon: '💪',
    category: 'beauty',
    description: 'Gym membership, yoga & fitness packages',
    color: 'slate',
    fields: ['offer_price', 'original_price', 'services', 'date_range'],
  },
  {
    slug: 'spa_wellness',
    label: 'Spa & Wellness',
    icon: '🧴',
    category: 'beauty',
    description: 'Massage, spa packages & wellness offers',
    color: 'teal',
    fields: ['offer_price', 'original_price', 'services', 'date_range'],
  },
  // ── EVENTS & SERVICES ─────────────────────────────────────────────
  {
    slug: 'event_announcement',
    label: 'Event / Programme',
    icon: '🎉',
    category: 'events',
    description: 'Cultural, social & community events',
    color: 'purple',
    fields: ['services', 'date_range', 'event_time', 'locality', 'offer_price'],
  },
  {
    slug: 'wedding_services',
    label: 'Wedding Services',
    icon: '💍',
    category: 'events',
    description: 'Wedding photography, catering & hall booking',
    color: 'rose',
    fields: ['offer_price', 'services', 'date_range', 'locality'],
  },
  {
    slug: 'automobile_service',
    label: 'Automobile / Service Centre',
    icon: '🚗',
    category: 'events',
    description: 'Car/bike service offers & new vehicle launch',
    color: 'slate',
    fields: ['offer_price', 'original_price', 'services', 'date_range'],
  },
  {
    slug: 'travel_tour',
    label: 'Travel & Tour Package',
    icon: '✈️',
    category: 'events',
    description: 'Tour packages, pilgrimage & travel offers',
    color: 'sky',
    fields: ['offer_price', 'original_price', 'services', 'date_range'],
  },
];

const LANGUAGE_OPTIONS = [
  // ── Indian Languages ────────────────────────────────────────────────
  { value: 'telugu',    label: 'తెలుగు Telugu',        region: '🇮🇳 India' },
  { value: 'hindi',     label: 'हिंदी Hindi',           region: '🇮🇳 India' },
  { value: 'tamil',     label: 'தமிழ் Tamil',           region: '🇮🇳 India' },
  { value: 'kannada',   label: 'ಕನ್ನಡ Kannada',         region: '🇮🇳 India' },
  { value: 'malayalam', label: 'മലയാളം Malayalam',      region: '🇮🇳 India' },
  { value: 'bengali',   label: 'বাংলা Bengali',         region: '🇮🇳 India' },
  { value: 'marathi',   label: 'मराठी Marathi',         region: '🇮🇳 India' },
  { value: 'gujarati',  label: 'ગુજરાતી Gujarati',      region: '🇮🇳 India' },
  { value: 'punjabi',   label: 'ਪੰਜਾਬੀ Punjabi',        region: '🇮🇳 India' },
  { value: 'odia',      label: 'ଓଡ଼ିଆ Odia',            region: '🇮🇳 India' },
  // ── South-East Asia ─────────────────────────────────────────────────
  { value: 'malay',              label: 'Bahasa Melayu',       region: '🇲🇾 Malaysia' },
  { value: 'indonesian',         label: 'Bahasa Indonesia',    region: '🇮🇩 Indonesia' },
  { value: 'thai',               label: 'ภาษาไทย Thai',        region: '🇹🇭 Thailand' },
  { value: 'chinese_simplified', label: '简体中文 Chinese',      region: '🇲🇾🇸🇬 MY/SG' },
];

const COLOR_MAP: Record<string, string> = {
  blue: 'bg-blue-50 border-blue-300 text-blue-700',
  green: 'bg-green-50 border-green-300 text-green-700',
  indigo: 'bg-indigo-50 border-indigo-300 text-indigo-700',
  purple: 'bg-purple-50 border-purple-300 text-purple-700',
  red: 'bg-red-50 border-red-300 text-red-700',
  rose: 'bg-rose-50 border-rose-300 text-rose-700',
  teal: 'bg-teal-50 border-teal-300 text-teal-700',
  cyan: 'bg-cyan-50 border-cyan-300 text-cyan-700',
  orange: 'bg-orange-50 border-orange-300 text-orange-700',
  amber: 'bg-amber-50 border-amber-300 text-amber-700',
  sky: 'bg-sky-50 border-sky-300 text-sky-700',
  pink: 'bg-pink-50 border-pink-300 text-pink-700',
  slate: 'bg-slate-50 border-slate-300 text-slate-700',
};

const ACTIVE_COLOR_MAP: Record<string, string> = {
  blue: 'bg-blue-600 border-blue-600 text-white',
  green: 'bg-green-600 border-green-600 text-white',
  indigo: 'bg-indigo-600 border-indigo-600 text-white',
  purple: 'bg-purple-600 border-purple-600 text-white',
  red: 'bg-red-600 border-red-600 text-white',
  rose: 'bg-rose-600 border-rose-600 text-white',
  teal: 'bg-teal-600 border-teal-600 text-white',
  cyan: 'bg-cyan-600 border-cyan-600 text-white',
  orange: 'bg-orange-500 border-orange-500 text-white',
  amber: 'bg-amber-500 border-amber-500 text-white',
  sky: 'bg-sky-600 border-sky-600 text-white',
  pink: 'bg-pink-600 border-pink-600 text-white',
  slate: 'bg-slate-700 border-slate-700 text-white',
};

interface GenerateResult {
  variants: Record<string, any>;
  summary?: {
    bilingual_content?: any;
    captions?: Record<string, string>;
    hashtags?: string[];
  };
}

export default function CampaignBuilder() {
  const [step, setStep] = useState(1);
  const [selectedTemplate, setSelectedTemplate] = useState<typeof TEMPLATES[0] | null>(null);
  const [secondaryLang, setSecondaryLang] = useState('telugu');
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  // Form fields
  const [form, setForm] = useState({
    city: '',
    locality: '',
    state: '',
    org_name: '',
    phone: '',
    doctor_name: '',
    doctor_qualification: '',
    department: '',
    date_range: '',
    event_time: '',
    offer_price: '',
    original_price: '',
    services: '',
    job_title: '',
    vacancies: '',
    salary_range: '',
    experience: '',
  });

  const updateField = (key: string, val: string) => setForm(f => ({ ...f, [key]: val }));

  const generateMutation = useMutation({
    mutationFn: (payload: any) =>
      api.post('/posters/generate-all-variants', payload).then(r => r.data),
    onSuccess: (data) => {
      setResult(data);
      setStep(4);
    },
  });

  const handleGenerate = () => {
    if (!selectedTemplate) return;
    const servicesArr = form.services
      ? form.services.split(',').map(s => s.trim()).filter(Boolean)
      : [];

    generateMutation.mutate({
      template_slug: selectedTemplate.slug,
      industry: selectedTemplate.category,
      city: form.city || 'Your City',
      locality: form.locality,
      state: form.state,
      org_name: form.org_name,
      phone: form.phone,
      doctor_name: form.doctor_name,
      doctor_qualification: form.doctor_qualification,
      department: form.department,
      date_range: form.date_range,
      event_time: form.event_time,
      offer_price: form.offer_price,
      original_price: form.original_price,
      services: servicesArr,
      job_title: form.job_title,
      vacancies: form.vacancies ? parseInt(form.vacancies) : undefined,
      salary_range: form.salary_range,
      experience: form.experience,
      secondary_language: secondaryLang,
      primary_language: 'english',
    });
  };

  const fieldDef = (name: string) => {
    const defs: Record<string, { label: string; placeholder: string; type?: string }> = {
      doctor_name: { label: 'Doctor Name', placeholder: 'Dr. Ramana Reddy' },
      doctor_qualification: { label: 'Qualification', placeholder: 'MBBS, MS Ortho' },
      department: { label: 'Department / Speciality', placeholder: 'Orthopaedics & Joint Replacement' },
      date_range: { label: 'Date Range', placeholder: '15-20 March 2026' },
      event_time: { label: 'Time', placeholder: '9:00 AM – 2:00 PM' },
      offer_price: { label: 'Offer Price', placeholder: '₹299' },
      original_price: { label: 'Original Price', placeholder: '₹1500' },
      services: { label: 'Services (comma-separated)', placeholder: 'Consultation, X-Ray, Physiotherapy' },
      locality: { label: 'Locality', placeholder: 'Kothagudem' },
      job_title: { label: 'Job Title', placeholder: 'Staff Nurse / Receptionist' },
      vacancies: { label: 'Vacancies', placeholder: '5', type: 'number' },
      salary_range: { label: 'Salary Range', placeholder: '₹15,000 – ₹25,000/month' },
      experience: { label: 'Experience Required', placeholder: '0-2 years / Freshers OK' },
    };
    return defs[name] || { label: name, placeholder: '' };
  };

  return (
    <div className="min-h-screen bg-gray-50 px-4 py-8 max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">🎨 Campaign Builder</h1>
        <p className="text-gray-500 mt-1">Generate bilingual campaign posters for all social media platforms in seconds.</p>
      </div>

      {/* Step indicators */}
      <div className="flex items-center gap-2 mb-8">
        {[1, 2, 3, 4].map(s => (
          <React.Fragment key={s}>
            <button
              type="button"
              onClick={() => { if (s < step || (s === 2 && selectedTemplate) || (s === 3 && selectedTemplate)) setStep(s); }}
              className={`flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm transition-all ${
                s === step ? 'bg-blue-600 text-white shadow-md' :
                s < step ? 'bg-blue-100 text-blue-600 cursor-pointer' :
                'bg-gray-200 text-gray-400 cursor-default'
              }`}
            >{s}</button>
            {s < 4 && <div className={`flex-1 h-1 rounded ${s < step ? 'bg-blue-400' : 'bg-gray-200'}`} />}
          </React.Fragment>
        ))}
      </div>

      {/* Step 1: Choose Template */}
      {step === 1 && (
        <div>
          <h2 className="text-xl font-semibold text-gray-800 mb-3">Step 1: Choose Campaign Type</h2>

          {/* Category filter chips */}
          <div className="flex flex-wrap gap-2 mb-5">
            <button
              onClick={() => setActiveCategory(null)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-all ${
                activeCategory === null ? 'bg-gray-800 text-white border-gray-800' : 'bg-white text-gray-600 border-gray-300 hover:border-gray-500'
              }`}
            >
              All Industries
            </button>
            {TEMPLATE_CATEGORIES.map(cat => (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-all ${
                  activeCategory === cat.id ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {TEMPLATES.filter(t => activeCategory === null || t.category === activeCategory).map(t => (
              <div
                key={t.slug}
                onClick={() => { setSelectedTemplate(t); setStep(2); }}
                className={`cursor-pointer rounded-2xl border-2 p-5 hover:shadow-md transition-all ${
                  selectedTemplate?.slug === t.slug ? ACTIVE_COLOR_MAP[t.color] : `bg-white border-gray-200 hover:border-blue-400`
                }`}
              >
                <div className="text-3xl mb-2">{t.icon}</div>
                <div className="font-bold text-base">{t.label}</div>
                <div className="text-xs mt-1 opacity-70">{t.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Step 2: Fill Details */}
      {step === 2 && selectedTemplate && (
        <div>
          <button onClick={() => setStep(1)} className="text-sm text-blue-600 mb-4 hover:underline">← Back to templates</button>
          <h2 className="text-xl font-semibold text-gray-800 mb-1">
            Step 2: Campaign Details — {selectedTemplate.icon} {selectedTemplate.label}
          </h2>
          <p className="text-sm text-gray-500 mb-4">Fill in the dynamic content for this campaign.</p>

          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 space-y-4">
            {/* Always-present fields */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">City *</label>
                <input value={form.city} onChange={e => updateField('city', e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="Hyderabad" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Organisation / Brand Name</label>
                <input value={form.org_name} onChange={e => updateField('org_name', e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="Apollo Hospital" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                <input value={form.phone} onChange={e => updateField('phone', e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="040-12345678" />
              </div>
            </div>

            {/* Template-specific fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {selectedTemplate.fields.map(fieldName => {
                const def = fieldDef(fieldName);
                return (
                  <div key={fieldName}>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{def.label}</label>
                    <input
                      type={def.type || 'text'}
                      value={(form as any)[fieldName] || ''}
                      onChange={e => updateField(fieldName, e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                      placeholder={def.placeholder}
                    />
                  </div>
                );
              })}
            </div>
          </div>

          <div className="mt-4 flex justify-end">
            <button
              type="button"
              onClick={() => setStep(3)}
              className="px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700"
            >
              Next: Choose Language →
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Language */}
      {step === 3 && selectedTemplate && (
        <div>
          <button onClick={() => setStep(2)} className="text-sm text-blue-600 mb-4 hover:underline">← Back to details</button>
          <h2 className="text-xl font-semibold text-gray-800 mb-1">Step 3: Choose Regional Language</h2>
          <p className="text-sm text-gray-500 mb-6">The poster will be generated in <strong>English + your chosen language</strong>. Supports 14 languages across India, SE Asia & Oceania.</p>

          {/* India group */}
          <div className="mb-5">
            <div className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">🇮🇳 Indian Languages</div>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {LANGUAGE_OPTIONS.filter(l => l.region?.includes('India')).map(lang => (
                <div
                  key={lang.value}
                  onClick={() => setSecondaryLang(lang.value)}
                  className={`cursor-pointer rounded-xl border-2 p-3 text-center transition-all ${
                    secondaryLang === lang.value
                      ? 'border-indigo-500 bg-indigo-50 shadow-md'
                      : 'border-gray-200 bg-white hover:border-indigo-300 hover:bg-indigo-50/40'
                  }`}
                >
                  <div className="text-xl mb-0.5">{lang.label.split(' ')[0]}</div>
                  <div className={`text-xs font-semibold ${secondaryLang === lang.value ? 'text-indigo-700' : 'text-gray-600'}`}>
                    {lang.label.split(' ').slice(1).join(' ') || lang.label}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* SE Asia group */}
          <div className="mb-6">
            <div className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">🌏 South-East Asia</div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {LANGUAGE_OPTIONS.filter(l => !l.region?.includes('India')).map(lang => (
                <div
                  key={lang.value}
                  onClick={() => setSecondaryLang(lang.value)}
                  className={`cursor-pointer rounded-xl border-2 p-3 text-center transition-all ${
                    secondaryLang === lang.value
                      ? 'border-indigo-500 bg-indigo-50 shadow-md'
                      : 'border-gray-200 bg-white hover:border-indigo-300 hover:bg-indigo-50/40'
                  }`}
                >
                  <div className="text-base font-semibold mb-0.5">{lang.region}</div>
                  <div className={`text-xs font-semibold ${secondaryLang === lang.value ? 'text-indigo-700' : 'text-gray-600'}`}>
                    {lang.label}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6 text-sm text-blue-800">
            💡 AI will generate campaign text in <strong>English + {LANGUAGE_OPTIONS.find(l => l.value === secondaryLang)?.label || secondaryLang}</strong>,
            then build visually-designed posters for Instagram, Facebook, WhatsApp, and LinkedIn automatically.
          </div>

          <div className="flex justify-end">
            <button
              type="button"
              disabled={generateMutation.isPending}
              onClick={handleGenerate}
              className="px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold text-lg shadow-md hover:shadow-lg disabled:opacity-50 transition-all"
            >
              {generateMutation.isPending ? '⏳ Generating posters...' : '✨ Generate Campaign Posters'}
            </button>
          </div>

          {generateMutation.isError && (
            <div className="mt-3 text-red-500 text-sm text-center">
              Generation failed. Make sure the AI provider API key is configured.
            </div>
          )}
        </div>
      )}

      {/* Step 4: Results */}
      {step === 4 && result && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-semibold text-gray-800">🎉 Campaign Generated!</h2>
              <p className="text-sm text-gray-500">Your bilingual campaign posters are ready for all platforms.</p>
            </div>
            <button
              type="button"
              onClick={() => { setStep(1); setSelectedTemplate(null); setResult(null); setActiveCategory(null); setForm({ city: '', locality: '', state: '', org_name: '', phone: '', doctor_name: '', doctor_qualification: '', department: '', date_range: '', event_time: '', offer_price: '', original_price: '', services: '', job_title: '', vacancies: '', salary_range: '', experience: '' }); }}
              className="px-4 py-2 text-sm bg-white border border-gray-300 rounded-xl text-gray-600 hover:bg-gray-50"
            >
              + New Campaign
            </button>
          </div>

          {/* Bilingual content summary */}
          {result.summary?.bilingual_content && (() => {
            const bc = result.summary.bilingual_content;
            const langLabel = LANGUAGE_OPTIONS.find(l => l.value === secondaryLang)?.label || secondaryLang;
            const hasRegional = !!bc.regional_title;
            return (
              <div className="rounded-2xl border overflow-hidden mb-6 shadow-sm">
                {/* Header */}
                <div className="flex items-center justify-between bg-gradient-to-r from-indigo-600 to-blue-600 px-4 py-2.5">
                  <span className="text-white text-sm font-semibold">📝 Generated Content</span>
                  <span className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${hasRegional ? 'bg-emerald-400 text-emerald-900' : 'bg-amber-300 text-amber-900'}`}>
                    {hasRegional ? `✓ Bilingual (EN + ${langLabel})` : '⚠ English only'}
                  </span>
                </div>
                {/* Content columns */}
                <div className="grid grid-cols-2 divide-x divide-gray-100 bg-white">
                  {/* English */}
                  <div className="p-4">
                    <div className="flex items-center gap-1.5 mb-2">
                      <span className="text-base">🇬🇧</span>
                      <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">English</span>
                    </div>
                    <p className="font-bold text-gray-900 text-sm leading-snug mb-1">{bc.english_title}</p>
                    <p className="text-xs text-gray-500 leading-relaxed">{bc.english_subtitle}</p>
                    {bc.english_cta && (
                      <span className="inline-block mt-2 text-xs bg-indigo-100 text-indigo-700 font-semibold px-2 py-0.5 rounded-full">{bc.english_cta}</span>
                    )}
                  </div>
                  {/* Regional */}
                  <div className="p-4">
                    <div className="flex items-center gap-1.5 mb-2">
                      <span className="text-base">🌐</span>
                      <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">{langLabel}</span>
                    </div>
                    {hasRegional ? (
                      <>
                        <p className="font-bold text-gray-900 text-sm leading-snug mb-1">{bc.regional_title}</p>
                        <p className="text-xs text-gray-500 leading-relaxed">{bc.regional_subtitle}</p>
                        {bc.regional_cta && (
                          <span className="inline-block mt-2 text-xs bg-indigo-100 text-indigo-700 font-semibold px-2 py-0.5 rounded-full">{bc.regional_cta}</span>
                        )}
                      </>
                    ) : (
                      <div className="flex flex-col gap-1.5 mt-1">
                        <p className="text-xs text-amber-700 font-medium leading-relaxed">
                          Translation couldn't be generated — AI API may not be configured.
                        </p>
                        <p className="text-xs text-gray-400 leading-relaxed">
                          Set <code className="bg-gray-100 px-1 rounded">OPENAI_API_KEY</code> in <code className="bg-gray-100 px-1 rounded">.env</code> to enable bilingual output.
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })()}

          {/* Hashtags */}
          {result.summary?.hashtags && result.summary.hashtags.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-6">
              {result.summary.hashtags.slice(0, 10).map(tag => (
                <span key={tag} className="px-2 py-1 bg-gray-100 text-blue-600 rounded-full text-xs font-medium">{tag}</span>
              ))}
            </div>
          )}

          {/* Variant previews */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <VariantPreview
              variants={result.variants}
              secondaryLanguage={secondaryLang}
              captions={result.summary?.captions}
            />
          </div>
        </div>
      )}
    </div>
  );
}
