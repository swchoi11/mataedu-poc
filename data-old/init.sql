-- Create the curriculum table
CREATE TABLE IF NOT EXISTS curriculum (
    id SERIAL PRIMARY KEY,
    grade VARCHAR NOT NULL,
    subject VARCHAR NOT NULL,
    main_chap_num INTEGER NOT NULL,
    main_chap VARCHAR NOT NULL,
    mid_chap_num INTEGER,
    mid_chap VARCHAR,
    small_chap_num INTEGER,
    small_chap VARCHAR
);

-- Create indexes
CREATE INDEX IF NOT EXISTS ix_curriculum_id ON curriculum (id);

-- Copy data from the CSV file into the curriculum table
-- IMPORTANT: This assumes curriculum.csv is in the same directory as this script
-- inside the /docker-entrypoint-initdb.d/ directory of the container.
COPY curriculum(grade, subject, main_chap_num, main_chap, mid_chap_num, mid_chap, small_chap_num, small_chap)
FROM '/docker-entrypoint-initdb.d/curriculum.csv'
DELIMITER ','
CSV HEADER
NULL 'nan';
