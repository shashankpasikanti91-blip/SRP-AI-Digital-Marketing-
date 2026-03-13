import React from 'react';

interface LanguageToggleProps {
  primaryLang: string;
  secondaryLang: string;
  active: 'english' | 'regional';
  onChange: (lang: 'english' | 'regional') => void;
}

const LANG_LABELS: Record<string, string> = {
  english: '🇬🇧 English',
  telugu: 'తెలుగు',
  hindi: 'हिंदी',
  tamil: 'தமிழ்',
  kannada: 'ಕನ್ನಡ',
  malayalam: 'മലയാളം',
};

export default function LanguageToggle({ primaryLang, secondaryLang, active, onChange }: LanguageToggleProps) {
  return (
    <div className="inline-flex rounded-xl overflow-hidden border border-gray-200 shadow-sm">
      <button
        type="button"
        onClick={() => onChange('english')}
        className={`px-4 py-2 text-sm font-medium transition-colors ${
          active === 'english'
            ? 'bg-blue-600 text-white'
            : 'bg-white text-gray-600 hover:bg-gray-50'
        }`}
      >
        {LANG_LABELS[primaryLang] || primaryLang}
      </button>
      <button
        type="button"
        onClick={() => onChange('regional')}
        className={`px-4 py-2 text-sm font-medium border-l border-gray-200 transition-colors ${
          active === 'regional'
            ? 'bg-indigo-600 text-white'
            : 'bg-white text-gray-600 hover:bg-gray-50'
        }`}
      >
        {LANG_LABELS[secondaryLang] || secondaryLang}
      </button>
    </div>
  );
}
