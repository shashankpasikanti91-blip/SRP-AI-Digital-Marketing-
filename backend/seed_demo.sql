-- ============================================================
-- SRP Marketing OS - Demo Seed Data (IDEMPOTENT - safe to run multiple times)
-- Run: Get-Content seed_demo.sql | docker exec -i ats-postgres psql -U ats_user -d srp_marketing
-- Accounts: 5 tenants covering all industry demos
-- Password for ALL bunty accounts: Bunty@2026
-- Password for demo@srp.ai: Demo@12345
-- ============================================================

-- -- 0. CLEANUP previous demo data for bunty accounts (idempotency) -----------
DO $$
DECLARE bunty_ids UUID[];
BEGIN
  SELECT ARRAY(SELECT id FROM tenants WHERE slug LIKE 'bunty-%') INTO bunty_ids;
  IF array_length(bunty_ids, 1) > 0 THEN
    DELETE FROM email_campaigns  WHERE tenant_id = ANY(bunty_ids);
    DELETE FROM social_posts     WHERE tenant_id = ANY(bunty_ids);
    DELETE FROM crm_pipelines    WHERE tenant_id = ANY(bunty_ids);
    DELETE FROM brand_profiles   WHERE tenant_id = ANY(bunty_ids);
    DELETE FROM leads            WHERE tenant_id = ANY(bunty_ids);
  END IF;
END $$;
-- Also clean srp-demo leads (keep tenant)
DELETE FROM leads WHERE tenant_id = (SELECT id FROM tenants WHERE slug = 'srp-demo');

-- â”€â”€ 1. UPDATE existing demo account password if needed â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
UPDATE tenants SET
  hashed_password = '$2b$12$HoVGTOT0hGnkbWCN3lSGOuCFWDdJvkktLZI5uIkf/Pe5dcMO9iipa',
  plan = 'professional',
  company_name = 'SRP Digital Marketing Agency',
  phone = '9100000001',
  timezone = 'Asia/Kolkata'
WHERE slug = 'srp-demo';

-- â”€â”€ 2. CREATE Bunty Hospital â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
INSERT INTO tenants (name, slug, email, hashed_password, plan, company_name, phone, timezone, api_key)
VALUES (
  'Bunty Hospital Demo',
  'bunty-hospital',
  'bunty@hospital.demo',
  '$2b$12$JrEJfsdUDMQziDxER6sqnu01TGI69E6QS/ujxWVw/p9rdpee0bKsi',
  'professional',
  'Kothagudem General & Orthopedic Hospital',
  '9100000010',
  'Asia/Kolkata',
  md5(random()::text || clock_timestamp()::text)
) ON CONFLICT (slug) DO UPDATE SET
  hashed_password = EXCLUDED.hashed_password,
  company_name    = EXCLUDED.company_name,
  plan            = EXCLUDED.plan;

-- â”€â”€ 3. CREATE Bunty Recruitment â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
INSERT INTO tenants (name, slug, email, hashed_password, plan, company_name, phone, timezone, api_key)
VALUES (
  'Bunty Recruitment Demo',
  'bunty-recruitment',
  'bunty@recruitment.demo',
  '$2b$12$JrEJfsdUDMQziDxER6sqnu01TGI69E6QS/ujxWVw/p9rdpee0bKsi',
  'professional',
  'BuntyHire â€” Pan India Staffing Solutions',
  '9100000020',
  'Asia/Kolkata',
  md5(random()::text || clock_timestamp()::text)
) ON CONFLICT (slug) DO UPDATE SET
  hashed_password = EXCLUDED.hashed_password,
  company_name    = EXCLUDED.company_name,
  plan            = EXCLUDED.plan;

-- â”€â”€ 4. CREATE Bunty Digital Marketing / FB Ads â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
INSERT INTO tenants (name, slug, email, hashed_password, plan, company_name, phone, timezone, api_key)
VALUES (
  'Bunty Digital Ads Demo',
  'bunty-ads',
  'bunty@ads.demo',
  '$2b$12$JrEJfsdUDMQziDxER6sqnu01TGI69E6QS/ujxWVw/p9rdpee0bKsi',
  'professional',
  'BuntyAds â€” Facebook & Google Lead Generation',
  '9100000030',
  'Asia/Kolkata',
  md5(random()::text || clock_timestamp()::text)
) ON CONFLICT (slug) DO UPDATE SET
  hashed_password = EXCLUDED.hashed_password,
  company_name    = EXCLUDED.company_name,
  plan            = EXCLUDED.plan;

-- â”€â”€ 5. CREATE Bunty Restaurant â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
INSERT INTO tenants (name, slug, email, hashed_password, plan, company_name, phone, timezone, api_key)
VALUES (
  'Bunty Restaurant Demo',
  'bunty-restaurant',
  'bunty@restaurant.demo',
  '$2b$12$JrEJfsdUDMQziDxER6sqnu01TGI69E6QS/ujxWVw/p9rdpee0bKsi',
  'professional',
  'Bunty''s Kitchen â€” Multi-Cuisine Family Restaurant',
  '9100000040',
  'Asia/Kolkata',
  md5(random()::text || clock_timestamp()::text)
) ON CONFLICT (slug) DO UPDATE SET
  hashed_password = EXCLUDED.hashed_password,
  company_name    = EXCLUDED.company_name,
  plan            = EXCLUDED.plan;

-- â”€â”€ 6. Verify tenants created â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
SELECT slug, email, plan, company_name FROM tenants ORDER BY created_at;

-- ============================================================
-- HOSPITAL DEMO LEADS
-- ============================================================
WITH hosp AS (SELECT id FROM tenants WHERE slug = 'bunty-hospital')
INSERT INTO leads (tenant_id, name, email, phone, company, source, campaign, status, ai_score, ai_label, notes)
SELECT
  hosp.id,
  v.name, v.email, v.phone, v.company, v.source, v.campaign, v.status::leadstatus, v.score, v.label, v.notes
FROM hosp, (VALUES
  ('Ramesh Kumar',    'ramesh@gmail.com',    '9876501001', 'Self',             'organic',  'Ortho Camp March',    'new',        82, 'hot',  'Knee pain 3 months, wants free checkup'),
  ('Sunitha Devi',    'sunitha@gmail.com',   '9876501002', 'Self',             'whatsapp', 'Ortho Camp March',    'contacted',  75, 'warm', 'Hip replacement enquiry'),
  ('Vijay Rao',       'vijay@gmail.com',     '9876501003', 'Apollo Referral',  'referral', 'Diabetes Camp',       'qualified',  90, 'hot',  'HbA1c 9.2, needs endocrinologist'),
  ('Kavitha Lakshmi', 'kavitha@gmail.com',   '9876501004', 'Self',             'facebook', 'Diabetes Camp',       'new',        60, 'warm', 'Type 2 diabetes, 5 years'),
  ('Suresh Patil',    'suresh.p@gmail.com',  '9876501005', 'Insurance Ref',    'referral', 'General Surgery',     'qualified',  88, 'hot',  'Appendix surgery inquiry'),
  ('Anitha Reddy',    'anitha.r@yahoo.com',  '9876501006', 'Self',             'instagram','Maternity Package',   'qualified',  72, 'warm', 'Second trimester, interested in package'),
  ('Pradeep Nair',    'pradeep@gmail.com',   '9876501007', 'Corporate',        'linkedin', 'Corporate Health',    'new',        55, 'cold', 'Company health checkup package'),
  ('Meena Sharma',    'meena.s@gmail.com',   '9876501008', 'Self',             'organic',  'Eye Camp',            'contacted',  68, 'warm', 'Cataract bilateral, early stage'),
  ('Ravi Teja',       'ravi.t@gmail.com',    '9876501009', 'Doctor Referral',  'referral', 'Ortho Camp March',    'qualified',  91, 'hot',  'Spine surgery L4-L5 disc'),
  ('Lakshmi Bai',     'lakshmib@gmail.com',  '9876501010', 'Self',             'whatsapp', 'Diabetes Camp',       'converted',  95, 'hot',  'Admitted for treatment â€” converted lead'),
  ('Naresh Goud',     'naresh.g@gmail.com',  '9876501011', 'Walk-in',          'organic',  'General OPD',         'new',        40, 'cold', 'General checkup enquiry'),
  ('Padma Vathi',     'padma.v@gmail.com',   '9876501012', 'Self',             'facebook', 'Cardiology Camp',     'contacted',  77, 'warm', 'BP 160/100, cardiologist needed')
) AS v(name, email, phone, company, source, campaign, status, score, label, notes)
ON CONFLICT DO NOTHING;

-- ============================================================
-- RECRUITMENT DEMO LEADS
-- ============================================================
WITH rec AS (SELECT id FROM tenants WHERE slug = 'bunty-recruitment')
INSERT INTO leads (tenant_id, name, email, phone, company, source, campaign, status, ai_score, ai_label, notes)
SELECT
  rec.id,
  v.name, v.email, v.phone, v.company, v.source, v.campaign, v.status::leadstatus, v.score, v.label, v.notes
FROM rec, (VALUES
  ('Apollo HR Dept',     'hr@apollohyd.com',      '9876502001', 'Apollo Hospitals',       'linkedin',  'Staff Nurse Drive Mar',  'qualified',  88, 'hot',  'Need 15 staff nurses urgently for ICU'),
  ('Infosys Recruiter',  'talent@infosys.com',    '9876502002', 'Infosys',                'linkedin',  'IT Walkin Drive',        'new',        72, 'warm', 'Bulk hiring 50 Java devs'),
  ('Zomato HR',          'recruit@zomato.com',    '9876502003', 'Zomato',                 'facebook',  'Delivery Partner Drive', 'contacted',  60, 'warm', 'Delivery exec recruitment 200+'),
  ('Amazon HR',          'hr.amz@amazon.in',      '9876502004', 'Amazon Logistics',       'organic',   'Warehouse Staff Drive',  'qualified',  85, 'hot',  'Warehouse associates Hyderabad'),
  ('KIMS HR',            'hr@kimshospitals.com',  '9876502005', 'KIMS Hospitals',         'referral',  'Medical Staff Drive',    'qualified',  91, 'hot',  'Pharmacists x10, Lab technician x5'),
  ('Byju''s HR',         'hr@byjus.com',          '9876502006', 'Byju''s',                'linkedin',  'Sales Jobs Drive',       'new',        65, 'warm', 'Academic counselors 30 positions'),
  ('L&T HR',             'talent@lntecc.com',     '9876502007', 'L&T Construction',       'organic',   'Civil Eng Walkin',       'contacted',  78, 'warm', 'Site engineers Hyderabad metro'),
  ('HDFC HR',            'recruit@hdfc.com',      '9876502008', 'HDFC Bank',              'linkedin',  'Banking Jobs March',     'qualified',  82, 'hot',  'Relationship managers 20 positions'),
  ('Wipro HR',           'hr@wipro.com',           '9876502009', 'Wipro',                  'linkedin',  'IT Walkin Drive',        'new',        55, 'cold', 'Testing engineers freshers'),
  ('City Hospital HR',   'hr@cityhospital.in',    '9876502010', 'City Hospital',          'whatsapp',  'Medical Staff Drive',    'converted',  95, 'hot',  'Contract signed â€” placed 8 nurses'),
  ('D-Mart HR',          'hr@dmart.in',           '9876502011', 'D-Mart',                 'facebook',  'Retail Staff Drive',     'contacted',  58, 'warm', 'Cashiers and floor staff 50+'),
  ('Accenture HR',       'jobs@accenture.com',    '9876502012', 'Accenture',              'linkedin',  'IT Walkin Drive',        'qualified',  80, 'hot',  'Python developers 15 positions')
) AS v(name, email, phone, company, source, campaign, status, score, label, notes)
ON CONFLICT DO NOTHING;

-- ============================================================
-- DIGITAL ADS DEMO LEADS
-- ============================================================
WITH ads AS (SELECT id FROM tenants WHERE slug = 'bunty-ads')
INSERT INTO leads (tenant_id, name, email, phone, company, source, campaign, status, ai_score, ai_label, notes)
SELECT
  ads.id,
  v.name, v.email, v.phone, v.company, v.source, v.campaign, v.status::leadstatus, v.score, v.label, v.notes
FROM ads, (VALUES
  ('Raj Electronics',   'raj@rajelectronics.in',  '9876503001', 'Raj Electronics',     'facebook',   'FB Ads Lead Gen Q1',    'qualified',  86, 'hot',  'Wants 200 leads/month electronics shop'),
  ('Swathi Jewellery',  'swathi@jewels.in',       '9876503002', 'Swathi Jewels',        'instagram',  'Gold Offer Campaign',   'new',        70, 'warm', 'Seasonal gold campaign Diwali'),
  ('Mega Motors',       'sales@megamotors.in',    '9876503003', 'Mega Motors',          'google_ads', 'Car Lead Gen',          'contacted',  79, 'warm', 'Two-wheeler sales lead generation'),
  ('TechCourse Pro',    'info@techcourse.in',     '9876503004', 'TechCourse.in',        'linkedin',   'Online Course Ads',     'qualified',  88, 'hot',  'Ed-tech course promotion budget'),
  ('Sai Real Estate',   'sai@properties.in',      '9876503005', 'Sai Properties',       'facebook',   'Real Estate Lead Gen',  'qualified',  93, 'hot',  'Apartment project launch â‚¹2L budget'),
  ('Priya Boutique',    'priya@boutique.in',      '9876503006', 'Priya Boutique',       'instagram',  'Fashion Campaign',      'new',        52, 'cold', 'Instagram campaign for clothing'),
  ('Sri Sai Hospital',  'info@srisaihospital.in', '9876503007', 'Sri Sai Hospital',     'google_ads', 'Hospital Lead Gen',     'qualified',  87, 'hot',  'Patient acquisition Google Ads'),
  ('EduSpark Academy',  'admin@eduspark.in',      '9876503008', 'EduSpark',             'facebook',   'Admissions Campaign',   'converted',  96, 'hot',  'Contract signed 1.2L/quarter'),
  ('Quick Bite Foods',  'info@quickbite.in',      '9876503009', 'Quick Bite',           'instagram',  'Food Delivery Ads',     'contacted',  65, 'warm', 'Swiggy/Zomato ad campaign'),
  ('Lakshmi Travels',   'bk@lakshmitravels.in',   '9876503010', 'Lakshmi Travels',      'google_ads', 'Travel Ads',            'new',        48, 'cold', 'Tour package ads South India'),
  ('Surya Fitness',     'surya@gym.in',           '9876503011', 'Surya Fitness Studio',  'facebook',  'Gym Membership Ads',    'contacted',  72, 'warm', 'New gym membership drive Jan-Mar'),
  ('Diamond Builders',  'info@diamondbuilders.in','9876503012', 'Diamond Builders',      'google_ads', 'Construction Leads',   'qualified',  84, 'hot',  'Villa project Hyderabad outskirts')
) AS v(name, email, phone, company, source, campaign, status, score, label, notes)
ON CONFLICT DO NOTHING;

-- ============================================================
-- RESTAURANT DEMO LEADS
-- ============================================================
WITH rest AS (SELECT id FROM tenants WHERE slug = 'bunty-restaurant')
INSERT INTO leads (tenant_id, name, email, phone, company, source, campaign, status, ai_score, ai_label, notes)
SELECT
  rest.id,
  v.name, v.email, v.phone, v.company, v.source, v.campaign, v.status::leadstatus, v.score, v.label, v.notes
FROM rest, (VALUES
  ('Ravi Shankar',      'ravi.s@corp.com',    '9876504001', 'TCS Kothagudem',      'instagram',  'Lunch Combo April',    'new',        70, 'warm', 'Daily corporate lunch order 25 people'),
  ('Priya Events',      'priya@events.in',    '9876504002', 'Priya Event Mgmt',    'whatsapp',   'Bulk Catering',        'qualified',  88, 'hot',  'Birthday party 80 pax catering'),
  ('Srinivas Office',   'srin@firm.in',       '9876504003', 'Advocate Office',     'facebook',   'Office Tiffin',        'contacted',  62, 'warm', 'Morning tiffin 15 people daily'),
  ('College Canteen',   'prin@college.edu',   '9876504004', 'LT Engineering',      'organic',    'College Bulk Order',   'qualified',  85, 'hot',  'Monthly canteen contract 200+ students'),
  ('Marriage Hall',     'book@goldenhall.in', '9876504005', 'Golden Marriage Hall', 'referral',  'Wedding Catering',     'qualified',  92, 'hot',  'South Indian wedding feast 500 pax'),
  ('Durga Puja Comm',   'org@durgapuja.in',   '9876504006', 'Community Trust',     'whatsapp',   'Festival Catering',    'converted',  97, 'hot',  'Festival feast contracted 85000'),
  ('Hotel Sunrise',     'mgr@sunrise.in',     '9876504007', 'Hotel Sunrise',       'linkedin',   'Cloud Kitchen',        'new',        55, 'cold', 'Supply samosas & sweets hotel'),
  ('School PTA',        'pta@school.edu',     '9876504008', 'DAV Public School',   'organic',    'School Event Catg',    'contacted',  68, 'warm', 'Annual day snacks 300 students')
) AS v(name, email, phone, company, source, campaign, status, score, label, notes)
ON CONFLICT DO NOTHING;

-- ============================================================
-- SRP DEMO LEADS
-- ============================================================
WITH srp AS (SELECT id FROM tenants WHERE slug = 'srp-demo')
INSERT INTO leads (tenant_id, name, email, phone, company, source, campaign, status, ai_score, ai_label, notes)
SELECT
  srp.id,
  v.name, v.email, v.phone, v.company, v.source, v.campaign, v.status::leadstatus, v.score, v.label, v.notes
FROM srp, (VALUES
  ('Kiran Patel',       'kiran.p@startup.in',  '9876500001', 'FinTech Startup',    'linkedin',  'AI Tools Demo',        'qualified',  90, 'hot',  'Wants AI email automation for 10k leads'),
  ('Nandita Sharma',    'nandita@agency.in',   '9876500002', 'Growth Agency',      'referral',  'Agency Plan',          'qualified',  85, 'hot',  'White-label for their clients'),
  ('Akhil Reddy',       'akhil@ecommerce.in',  '9876500003', 'E-commerce Brand',   'google_ads','E-comm Lead Gen',      'contacted',  72, 'warm', 'Product marketing automation'),
  ('Shalini Menon',     'shalini@clinic.in',   '9876500004', 'Multi-city Clinic',  'organic',   'Healthcare Demo',      'new',        68, 'warm', 'Patient follow-up automation'),
  ('Tech Mahindra BD',  'bd@techmahindra.com', '9876500005', 'Tech Mahindra',      'linkedin',  'Enterprise Plan',      'qualified',  95, 'hot',  'Enterprise 50-seat license discussion')
) AS v(name, email, phone, company, source, campaign, status, score, label, notes)
ON CONFLICT DO NOTHING;

-- ============================================================
-- CRM PIPELINES for each tenant
-- ============================================================
-- Hospital pipelines
WITH hosp AS (SELECT id FROM tenants WHERE slug = 'bunty-hospital')
INSERT INTO crm_pipelines (tenant_id, title, stage, value, currency, assigned_to, notes)
SELECT hosp.id, v.title, v.stage::crmstage, v.value, 'INR', v.assigned_to, v.notes
FROM hosp, (VALUES
  ('Ravi Teja â€” Spine Surgery L4-L5',         'proposal',   85000, 'Dr. Reddy',   'Patient consulted, surgery date being finalized'),
  ('Vijay Rao â€” Endocrinology Package',        'qualified',  45000, 'Dr. Sharma',  'Referred for 3-month diabetes management plan'),
  ('Lakshmi Bai â€” Admitted Patient',           'won',        120000,'Admin',       'Admitted for full treatment, insurance approved'),
  ('Anitha Reddy â€” Maternity Package',         'proposal',   95000, 'Dr. Priya',   'Silver package â‚¹95k discussed'),
  ('Meena Sharma â€” Cataract Surgery',          'qualified',  38000, 'Dr. Rao',     'Both eyes, scheduling in April'),
  ('Suresh Patil â€” Appendix Surgery',          'proposal',   42000, 'Billing',     'Insurance query pending')
) AS v(title, stage, value, assigned_to, notes)
ON CONFLICT DO NOTHING;

-- Recruitment pipelines
WITH rec AS (SELECT id FROM tenants WHERE slug = 'bunty-recruitment')
INSERT INTO crm_pipelines (tenant_id, title, stage, value, currency, assigned_to, notes)
SELECT rec.id, v.title, v.stage::crmstage, v.value, 'INR', v.assigned_to, v.notes
FROM rec, (VALUES
  ('Apollo Hospitals â€” ICU Nurses x15',        'qualified',  225000,'Bunty',       'â‚¹15k commission per placement Ã— 15'),
  ('KIMS â€” Medical Staff Bulk',                 'proposal',   180000,'Team A',      'Pharmacists + Lab techs, offer letter stage'),
  ('City Hospital â€” Contract Signed',          'won',         120000,'Admin',      'Commission received, 8 nurses placed'),
  ('Amazon Warehouse â€” Associates',             'qualified',  150000,'Team B',      'Background check in progress'),
  ('HDFC Bank â€” Relationship Managers',        'proposal',    100000,'Bunty',      'Final round underway'),
  ('Accenture â€” Python Devs x15',              'proposal',   225000,'Team A',      'JD finalized, profiles shortlisted')
) AS v(title, stage, value, assigned_to, notes)
ON CONFLICT DO NOTHING;

-- Ads agency pipelines
WITH ads AS (SELECT id FROM tenants WHERE slug = 'bunty-ads')
INSERT INTO crm_pipelines (tenant_id, title, stage, value, currency, assigned_to, notes)
SELECT ads.id, v.title, v.stage::crmstage, v.value, 'INR', v.assigned_to, v.notes
FROM ads, (VALUES
  ('Sai Real Estate â€” Project Launch Campaign','qualified',   200000,'Bunty',       'Q1 budget â‚¹2L confirmed, starting April'),
  ('EduSpark Academy â€” Quarterly Contract',    'won',         120000,'Admin',       'Onboarded, first invoice raised'),
  ('Sri Sai Hospital â€” Google Ads',           'proposal',     60000,'Team',        'Proposal sent â‚¹60k/month retainer'),
  ('TechCourse Pro â€” Course Ads',             'proposal',     50000, 'Bunty',       'Discussing budget split across platforms'),
  ('Mega Motors â€” Lead Gen',                  'qualified',    40000, 'Team',        'Test campaign results positive'),
  ('Diamond Builders â€” Villa Project',        'proposal',     180000,'Bunty',       'Big project, site visit done')
) AS v(title, stage, value, assigned_to, notes)
ON CONFLICT DO NOTHING;

-- Restaurant pipelines
WITH rest AS (SELECT id FROM tenants WHERE slug = 'bunty-restaurant')
INSERT INTO crm_pipelines (tenant_id, title, stage, value, currency, assigned_to, notes)
SELECT rest.id, v.title, v.stage::crmstage, v.value, 'INR', v.assigned_to, v.notes
FROM rest, (VALUES
  ('Durga Puja Committee â€” Festival Feast',   'won',          85000, 'Manager',     'Advance â‚¹25k received, event April 5'),
  ('Marriage Hall â€” Wedding Catering',        'proposal',     150000,'Bunty',       '500 pax quote sent, waiting for confirmation'),
  ('College Canteen â€” Monthly Contract',      'proposal',     60000, 'Admin',       '60k/month for 6 months, finalizing menu'),
  ('TCS Corporate Lunch',                     'qualified',    30000, 'Team',        '25 people Ã— â‚¹120/plate daily, trial week'),
  ('Priya Events â€” Birthday Party',           'qualified',    24000, 'Kitchen',     '80 pax birthday, menu finalized')
) AS v(title, stage, value, assigned_to, notes)
ON CONFLICT DO NOTHING;

-- ============================================================
-- BRAND PROFILES for campaign builder demo
-- ============================================================
WITH hosp AS (SELECT id FROM tenants WHERE slug = 'bunty-hospital')
INSERT INTO brand_profiles (id, tenant_id, brand_name, tagline, primary_color, secondary_color, accent_color, font_family, regional_font_family, industry, city, state, address, phone_numbers, default_languages, footer_text)
SELECT gen_random_uuid(), hosp.id, 'Kothagudem General Hospital', 'Your Health, Our Priority', '#1E3A8A', '#FFFFFF', '#F59E0B', 'Inter', 'Noto Sans Telugu', 'hospital', 'Kothagudem', 'Telangana', 'Main Road, Kothagudem - 507101', '["9876543210", "040-12345678"]'::jsonb, '["english","telugu"]'::jsonb, 'NABH Accredited | 24x7 Emergency | 200+ Beds'
FROM hosp ON CONFLICT (tenant_id) DO UPDATE SET brand_name = EXCLUDED.brand_name;

WITH rec AS (SELECT id FROM tenants WHERE slug = 'bunty-recruitment')
INSERT INTO brand_profiles (id, tenant_id, brand_name, tagline, primary_color, secondary_color, accent_color, font_family, regional_font_family, industry, city, state, address, phone_numbers, default_languages, footer_text)
SELECT gen_random_uuid(), rec.id, 'BuntyHire', 'Connecting Talent with Opportunity', '#7C3AED', '#FFFFFF', '#F59E0B', 'Inter', 'Noto Sans', 'recruitment_agency', 'Hyderabad', 'Telangana', 'Begumpet, Hyderabad - 500016', '["9876502000","040-99887766"]'::jsonb, '["english","telugu","hindi"]'::jsonb, 'Pan India Placement | 10,000+ Placed | ISO Certified'
FROM rec ON CONFLICT (tenant_id) DO UPDATE SET brand_name = EXCLUDED.brand_name;

WITH ads AS (SELECT id FROM tenants WHERE slug = 'bunty-ads')
INSERT INTO brand_profiles (id, tenant_id, brand_name, tagline, primary_color, secondary_color, accent_color, font_family, regional_font_family, industry, city, state, address, phone_numbers, default_languages, footer_text)
SELECT gen_random_uuid(), ads.id, 'BuntyAds Digital', 'Leads That Convert', '#DC2626', '#FFFFFF', '#F59E0B', 'Poppins', 'Noto Sans', 'marketing_agency', 'Hyderabad', 'Telangana', 'Jubilee Hills, Hyderabad - 500033', '["9876503000"]'::jsonb, '["english","hindi"]'::jsonb, 'Google Partner | Meta Business Partner | 500+ Clients'
FROM ads ON CONFLICT (tenant_id) DO UPDATE SET brand_name = EXCLUDED.brand_name;

WITH rest AS (SELECT id FROM tenants WHERE slug = 'bunty-restaurant')
INSERT INTO brand_profiles (id, tenant_id, brand_name, tagline, primary_color, secondary_color, accent_color, font_family, regional_font_family, industry, city, state, address, phone_numbers, default_languages, footer_text)
SELECT gen_random_uuid(), rest.id, 'Bunty''s Kitchen', 'Ghar Ka Khana, Restaurant Ka Maza', '#B45309', '#FFFBEB', '#EF4444', 'Poppins', 'Noto Sans', 'restaurant', 'Kothagudem', 'Telangana', 'Bus Stand Road, Kothagudem - 507101', '["9876504000","9876504001"]'::jsonb, '["english","telugu","hindi"]'::jsonb, 'Pure Veg & Non-Veg | Home Delivery | Catering Available'
FROM rest ON CONFLICT (tenant_id) DO UPDATE SET brand_name = EXCLUDED.brand_name;

-- ============================================================
-- SOCIAL POSTS (sample scheduled posts)
-- ============================================================
WITH hosp AS (SELECT id FROM tenants WHERE slug = 'bunty-hospital')
INSERT INTO social_posts (tenant_id, platform, content, status)
SELECT hosp.id, v.platform::socialplatform, v.content, v.status::poststatus
FROM hosp, (VALUES
  ('instagram', 'ðŸ¦´ Free Orthopaedic Camp â€” March 15-20 at Kothagudem General Hospital. FREE Consultation, X-Ray & Physiotherapy. Book: 9876543210 #FreeOrthoCamp #Kothagudem', 'scheduled'),
  ('facebook',  'ðŸ’‰ Diabetes Free Checkup Camp this Saturday! HbA1c test, Blood Sugar, Specialist Consultation â€” completely FREE. Limited slots. Call: 9876543210', 'draft'),
  ('linkedin',  'ðŸ¥ Kothagudem General Hospital â€” Free Orthopaedic & Diabetes Health Camps. NABH Accredited | 24x7. Book: 9876543210', 'draft')
) AS v(platform, content, status)
ON CONFLICT DO NOTHING;

WITH rec AS (SELECT id FROM tenants WHERE slug = 'bunty-recruitment')
INSERT INTO social_posts (tenant_id, platform, content, status)
SELECT rec.id, v.platform::socialplatform, v.content, v.status::poststatus
FROM rec, (VALUES
  ('linkedin',  'ðŸš¨ URGENT HIRING â€” Staff Nurses (ICU/PICU) @Apollo Hospitals Hyderabad. 2+ yrs exp. Salary 30k-50k. Apply: bunty@recruitment.demo or call 9876502000', 'published'),
  ('facebook',  'ðŸ‘” WALK-IN DRIVE â€” Java Developers & Python Engineers. Saturday 10AM-4PM. Begumpet, Hyderabad. Bring updated resume. #WalkinDrive #ITJobs', 'scheduled'),
  ('instagram', 'ðŸ“¢ 1000+ Jobs This Week! Nurses | Engineers | Bankers | Retail. Register FREE at BuntyHire. DM or call 9876502000. #Hiring #Jobs', 'draft')
) AS v(platform, content, status)
ON CONFLICT DO NOTHING;

-- ============================================================
-- EMAIL CAMPAIGNS (sample)
-- ============================================================
WITH hosp AS (SELECT id FROM tenants WHERE slug = 'bunty-hospital')
INSERT INTO email_campaigns (tenant_id, name, subject, body_html, status, from_email, from_name)
SELECT hosp.id, v.name, v.subject, v.body, v.status, 'noreply@kghospital.in', 'KGH Patient Care'
FROM hosp, (VALUES
  ('Ortho Camp Invitation March',
   'Free Orthopaedic Camp â€” Kothagudem General Hospital',
   '<h2>Free Orthopaedic Health Camp</h2><p>Dear Patient,</p><p>We are conducting a <strong>FREE Orthopaedic Health Camp</strong> from <strong>March 15-20, 2026</strong>.</p><p>Services offered FREE of cost:</p><ul><li>Orthopaedic Consultation</li><li>X-Ray</li><li>Physiotherapy Session</li></ul><p>Call us: <strong>9876543210</strong></p>',
   'draft'),
  ('Diabetes Awareness April',
   'Free Diabetes Screening Camp â€” Are You at Risk?',
   '<h2>Free Diabetes Checkup Camp</h2><p>1 in 11 adults in India has diabetes. Know your numbers â€” FREE checkup this Saturday at KGH.</p><p>HbA1c Test + Blood Sugar + Specialist Consultation â€” All FREE.</p><p>Book your slot: 9876543210</p>',
   'draft')
) AS v(name, subject, body, status)
ON CONFLICT DO NOTHING;

-- ============================================================
-- FINAL STATUS REPORT
-- ============================================================
SELECT
  t.slug,
  t.email,
  COUNT(DISTINCT l.id) AS leads,
  COUNT(DISTINCT c.id) AS crm_deals,
  COUNT(DISTINCT b.id) AS brand_profile,
  COUNT(DISTINCT s.id) AS social_posts,
  COUNT(DISTINCT ec.id) AS email_campaigns
FROM tenants t
LEFT JOIN leads           l ON l.tenant_id = t.id
LEFT JOIN crm_pipelines   c ON c.tenant_id = t.id
LEFT JOIN brand_profiles  b ON b.tenant_id = t.id
LEFT JOIN social_posts    s  ON s.tenant_id  = t.id
LEFT JOIN email_campaigns ec ON ec.tenant_id = t.id
GROUP BY t.slug, t.email
ORDER BY t.slug;
