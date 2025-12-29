-- HELIOS - Supabase Schema
-- Solar Leads Table

CREATE TABLE IF NOT EXISTS solar_leads (
  id BIGSERIAL PRIMARY KEY,

  -- Company Information
  company_name TEXT NOT NULL,
  vat_number TEXT,

  -- Contact Information
  contact_person TEXT,
  phone TEXT,
  email TEXT,
  pec TEXT,  -- Italian certified email
  website TEXT,

  -- Location
  address TEXT,
  city TEXT,
  region TEXT,

  -- Lead Metadata
  source TEXT DEFAULT 'GSE.it',
  industry TEXT DEFAULT 'Solar/Photovoltaic Installation',
  status TEXT DEFAULT 'new_lead',

  -- Dates
  scraped_date TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  -- Additional Data
  notes TEXT,
  metadata JSONB DEFAULT '{}'::JSONB
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_solar_leads_company ON solar_leads(company_name);
CREATE INDEX IF NOT EXISTS idx_solar_leads_region ON solar_leads(region);
CREATE INDEX IF NOT EXISTS idx_solar_leads_status ON solar_leads(status);
CREATE INDEX IF NOT EXISTS idx_solar_leads_source ON solar_leads(source);
CREATE INDEX IF NOT EXISTS idx_solar_leads_created ON solar_leads(created_at);

-- Create unique constraint to prevent exact duplicates
CREATE UNIQUE INDEX IF NOT EXISTS idx_solar_leads_unique_company ON solar_leads(LOWER(company_name));

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-update updated_at
DROP TRIGGER IF EXISTS update_solar_leads_updated_at ON solar_leads;
CREATE TRIGGER update_solar_leads_updated_at
  BEFORE UPDATE ON solar_leads
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE solar_leads IS 'Solar installation companies scraped from GSE.it and other sources';
COMMENT ON COLUMN solar_leads.company_name IS 'Name of the solar installation company';
COMMENT ON COLUMN solar_leads.pec IS 'Italian Certified Email (Posta Elettronica Certificata)';
COMMENT ON COLUMN solar_leads.status IS 'Lead status: new_lead, contacted, qualified, converted, rejected';
COMMENT ON COLUMN solar_leads.source IS 'Where the lead was scraped from (e.g., GSE.it)';
COMMENT ON COLUMN solar_leads.metadata IS 'Additional JSON data that does not fit in standard columns';

-- Create a view for active leads
CREATE OR REPLACE VIEW active_solar_leads AS
SELECT
  id,
  company_name,
  email,
  phone,
  city,
  region,
  status,
  scraped_date,
  created_at
FROM solar_leads
WHERE status NOT IN ('rejected', 'invalid')
ORDER BY created_at DESC;

-- Sample query to get recent leads by region
-- SELECT * FROM solar_leads WHERE region = 'Lombardia' ORDER BY created_at DESC LIMIT 10;

-- Sample query to count leads by status
-- SELECT status, COUNT(*) as count FROM solar_leads GROUP BY status;
