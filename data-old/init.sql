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
    sector, VARCHAR NOT NULL,
    unit, VARCHAR NOT NULL,
    unit_exp, VARCHAR NOT NULL
)

-- Create indexes
CREATE INDEX IF NOT EXISTS ix_curriculum_id ON curriculum (id);

-- Copy data from the CSV file into the curriculum table
COPY curriculum(grade, subject, main_chap_num, main_chap, mid_chap_num, mid_chap, small_chap_num, small_chap)
FROM '/docker-entrypoint-initdb.d/curriculum.csv'
DELIMITER ','
CSV HEADER
NULL 'nan';

-- Copy data from the csv file into the subject_unit table
COPY subject_unit(sector, unit, unit_exp)
FROM '/docker-entrypoint-initdb.d/subject_unit.csv'
DELIMITER ','
CSV HEADER
NULL 'nan';
