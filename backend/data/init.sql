-- Create the curriculum table
CREATE TABLE IF NOT EXISTS curriculum (
    id SERIAL PRIMARY KEY,
    grade VARCHAR NOT NULL,
    subject VARCHAR NOT NULL,
    no_main_chapter INTEGER NOT NULL,
    main_chapter VARCHAR NOT NULL,
    no_sub_chapter INTEGER,
    sub_chapter VARCHAR,
    no_lesson_chapter INTEGER,
    lesson_chapter VARCHAR
);

-- Create the criteria table
CREATE TABLE IF NOT EXISTS subject_unit (
    id SERIAL PRIMARY KEY,
    sector VARCHAR NOT NULL,
    criteria VARCHAR NOT NULL,
    criteria_exp VARCHAR NOT NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS ix_curriculum_id ON curriculum (id);

-- Copy data from the CSV file into the curriculum table
-- NULL 'nan'을 추가하여 'nan' 문자열을 NULL로 변환
COPY curriculum(grade, subject, no_main_chapter, main_chapter, no_sub_chapter, sub_chapter, no_lesson_chapter, lesson_chapter)
FROM '/docker-entrypoint-initdb.d/curriculum.csv'
DELIMITER ','
CSV HEADER
NULL 'nan';

-- Copy data from the csv file into the subject_unit table
COPY subject_unit(sector, criteria, criteria_exp)
FROM '/docker-entrypoint-initdb.d/교육과정성취기준.csv'
DELIMITER ','
CSV HEADER
NULL 'nan';
