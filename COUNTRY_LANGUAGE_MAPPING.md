# COUNTRY LANGUAGE MAPPING — Phase 14
## SRP Marketing OS — Global Language Reference

**Version:** 14.0.0  
**Date:** March 13, 2026

---

## Country → Language Matrix

| Country | Code | Primary | Secondary | Bilingual | Notes |
|---------|------|---------|-----------|-----------|-------|
| India | IN | English | *State-based* | ✅ | 28 states, each with own language |
| Malaysia | MY | English | Bahasa Melayu | ✅ | Multi-ethnic market |
| Indonesia | ID | English | Bahasa Indonesia | ✅ | World's 4th most populous country |
| Thailand | TH | English | Thai | ✅ | Thai script required |
| Singapore | SG | English | — | ❌ | English-only market |
| Australia | AU | English | — | ❌ | English-only market |
| New Zealand | NZ | English | — | ❌ | English-only market |

---

## India State → Language Mapping (28 States + UTs)

### South India

| State | Language | Script | Marketing Region |
|-------|----------|--------|-----------------|
| Telangana | Telugu | Telugu | South India |
| Andhra Pradesh | Telugu | Telugu | South India |
| Tamil Nadu | Tamil | Tamil | South India |
| Karnataka | Kannada | Kannada | South India |
| Kerala | Malayalam | Malayalam | South India |
| Puducherry | Tamil | Tamil | South India |

### West India

| State | Language | Script | Marketing Region |
|-------|----------|--------|-----------------|
| Maharashtra | Marathi | Devanagari | West India |
| Gujarat | Gujarati | Gujarati | West India |
| Goa | English | Latin | West India |
| Dadra and Nagar Haveli | Gujarati | Gujarati | West India |
| Daman and Diu | Gujarati | Gujarati | West India |

### North India

| State | Language | Script | Marketing Region |
|-------|----------|--------|-----------------|
| Uttar Pradesh | Hindi | Devanagari | North India |
| Rajasthan | Hindi | Devanagari | North India |
| Madhya Pradesh | Hindi | Devanagari | North India |
| Delhi | Hindi | Devanagari | North India |
| Haryana | Hindi | Devanagari | North India |
| Punjab | Punjabi | Gurmukhi | North India |
| Himachal Pradesh | Hindi | Devanagari | North India |
| Uttarakhand | Hindi | Devanagari | North India |
| Jammu and Kashmir | Hindi | Devanagari | North India |
| Ladakh | Hindi | Devanagari | North India |

### East India

| State | Language | Script | Marketing Region |
|-------|----------|--------|-----------------|
| West Bengal | Bengali | Bengali | East India |
| Bihar | Hindi | Devanagari | East India |
| Jharkhand | Hindi | Devanagari | East India |
| Odisha | Odia | Odia | East India |

### Central India

| State | Language | Script | Marketing Region |
|-------|----------|--------|-----------------|
| Chhattisgarh | Hindi | Devanagari | Central India |

### Northeast India

| State | Language | Script | Marketing Region |
|-------|----------|--------|-----------------|
| Assam | Assamese | Bengali (modified) | Northeast India |
| Manipur | English | Latin | Northeast India |
| Meghalaya | English | Latin | Northeast India |
| Mizoram | English | Latin | Northeast India |
| Nagaland | English | Latin | Northeast India |
| Tripura | Bengali | Bengali | Northeast India |
| Arunachal Pradesh | English | Latin | Northeast India |
| Sikkim | English | Latin | Northeast India |

---

## Full Language Registry

| Language Key | ISO Code | Name | Native Name | Script | Direction |
|-------------|---------|------|------------|--------|-----------|
| english | en | English | English | Latin | LTR |
| telugu | te | Telugu | తెలుగు | Telugu | LTR |
| hindi | hi | Hindi | हिन्दी | Devanagari | LTR |
| tamil | ta | Tamil | தமிழ் | Tamil | LTR |
| kannada | kn | Kannada | ಕನ್ನಡ | Kannada | LTR |
| malayalam | ml | Malayalam | മലയാളം | Malayalam | LTR |
| marathi | mr | Marathi | मराठी | Devanagari | LTR |
| gujarati | gu | Gujarati | ગુજરાતી | Gujarati | LTR |
| bengali | bn | Bengali | বাংলা | Bengali | LTR |
| punjabi | pa | Punjabi | ਪੰਜਾਬੀ | Gurmukhi | LTR |
| malay | ms | Bahasa Melayu | Bahasa Melayu | Latin | LTR |
| bahasa_indonesia | id | Bahasa Indonesia | Bahasa Indonesia | Latin | LTR |
| thai | th | Thai | ภาษาไทย | Thai | LTR |

---

## Language Decision Tree

```
Request comes in with country + state
           │
           ▼
Is country IN (India)?
    │           │
   YES          NO
    │           │
    ▼           ▼
Lookup state   Country has secondary_language?
in INDIA_STATE     │               │
_LANGUAGE_MAP     YES              NO
    │              │               │
    ▼              ▼               ▼
return state   return country  return "english"
   language    secondary_lang  (English-only)
```

---

## Bilingual Content Examples

### India — Telangana (Telugu + English)

**Campaign: Free Health Camp**

| Element | English | Telugu |
|---------|---------|--------|
| Headline | Free Orthopedic Health Camp | ఉచిత ఆర్థోపెడిక్ ఆరోగ్య శిబిరం |
| Body | Expert doctors, free consultation | నిపుణ వైద్యులు, ఉచిత సంప్రదింపు |
| CTA | Book Your Free Appointment | మీ ఉచిత అపాయింట్‌మెంట్ బుక్ చేసుకోండి |
| Badge | FREE CHECKUP | ఉచిత తనిఖీ |

### Malaysia (Malay + English)

**Campaign: Restaurant Promotion**

| Element | English | Malay |
|---------|---------|-------|
| Headline | Weekend Special Offer | Tawaran Khas Hujung Minggu |
| Body | Best local cuisine in KL | Masakan tempatan terbaik di KL |
| CTA | Order Now | Pesan Sekarang |
| Badge | 30% OFF | 30% DISKAUN |

### Indonesia (Bahasa Indonesia + English)

**Campaign: Ramadan Promo**

| Element | English | Bahasa Indonesia |
|---------|---------|-----------------|
| Headline | Ramadan Special Discount | Diskon Spesial Ramadan |
| Body | Celebrate Ramadan with us | Rayakan Ramadan bersama kami |
| CTA | Shop Now | Belanja Sekarang |
| Badge | UP TO 50% OFF | DISKON HINGGA 50% |

### Thailand (Thai + English)

**Campaign: Songkran Festival**

| Element | English | Thai |
|---------|---------|------|
| Headline | Songkran New Year Sale | ลดราคาปีใหม่สงกรานต์ |
| Body | Celebrate Thai New Year with great deals | ฉลองปีใหม่ไทยด้วยดีลสุดพิเศษ |
| CTA | Shop Now | ซื้อเลย |

---

## Festival Calendar by Country

### India
| Festival | Month | Type | States | Template Slug |
|---------|-------|------|--------|---------------|
| Diwali | October | National | All | diwali_offer |
| Ugadi | March | Regional | TG, AP, KA | ugadi_offer |
| Pongal | January | Regional | TN | pongal_offer |
| Holi | March | National | All | holi_offer |
| Eid ul-Fitr | April | National | All | eid_offer |
| Ganesh Chaturthi | September | Regional | MH, KA | ganesh_chaturthi_offer |
| Onam | September | Regional | KL | onam_offer |
| Durga Puja | October | Regional | WB | durga_puja_offer |
| Navratri | October | National | All | navratri_offer |
| Independence Day | August | National | All | independence_day |
| Republic Day | January | National | All | republic_day |

### Malaysia
| Festival | Month | Template Slug |
|---------|-------|---------------|
| Hari Raya Aidilfitri | April | hari_raya_offer |
| Chinese New Year | January | cny_offer |
| Deepavali | November | deepavali_offer |
| Malaysia Day | September | malaysia_day |

### Indonesia
| Festival | Month | Template Slug |
|---------|-------|---------------|
| Ramadan | March | ramadan_promo |
| Lebaran (Eid) | April | lebaran_offer |
| Independence Day | August | independence_id |

### Thailand
| Festival | Month | Template Slug |
|---------|-------|---------------|
| Songkran | April | songkran_offer |
| Loy Krathong | November | loy_krathong |
| National Day | December | thailand_national_day |

### Singapore
| Festival | Month | Template Slug |
|---------|-------|---------------|
| Chinese New Year | January | cny_sg |
| National Day | August | sg_national_day |
| Deepavali | November | deepavali_sg |

---

## SEO Keyword Patterns by Country

### India (Hyderabad, Hospital)
```
English: "best hospital in Hyderabad", "top hospital Hyderabad"
Near-me: "hospital near me", "hospital near Hyderabad"
Telugu: "హైదరాబాద్‌లో బెస్ట్ hospital", "hospital దగ్గర హైదరాబాద్"
```

### Malaysia (Kuala Lumpur, Restaurant)
```
English: "best restaurant in Kuala Lumpur", "top restaurant Kuala Lumpur"
Near-me: "restaurant near me", "restaurant near Kuala Lumpur"
Malay: "restaurant terbaik di Kuala Lumpur", "kedai makan Kuala Lumpur"
```

### Thailand (Bangkok, Fitness)
```
English: "best fitness in Bangkok", "top fitness Bangkok"
Near-me: "fitness near me", "fitness near Bangkok"
Thai: "fitnessที่ดีที่สุดในBangkok", "บริการfitness Bangkok"
```

---

*Phase 14 — Country Language Mapping Reference*  
*SRP Marketing OS — March 13, 2026*
