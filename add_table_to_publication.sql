-- SQL script to add cdc_test table to existing cdc_publication
-- Run this on the PostgreSQL VM server (72.61.241.193)

-- Connect to openmetadata_db
\c openmetadata_db

-- Add table to existing publication
ALTER PUBLICATION cdc_publication ADD TABLE public.cdc_test;

-- Verify the table is in the publication
SELECT 
    pubname,
    schemaname,
    tablename
FROM pg_publication_tables
WHERE pubname = 'cdc_publication'
ORDER BY tablename;



