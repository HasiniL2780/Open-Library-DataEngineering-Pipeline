CREATE DATABASE IF NOT EXISTS openlibrary;
USE openlibrary;

-- 1. INGESTION BATCH TABLE
CREATE TABLE IF NOT EXISTS silver_ingestion_batch (
    batch_id VARCHAR(50) PRIMARY KEY,
    source_name VARCHAR(100),
    load_start_ts DATETIME,
    load_end_ts DATETIME,
    status VARCHAR(50),
    records_fetched INT,
    records_loaded INT
);


-- 2. SUBJECT TABLE
CREATE TABLE IF NOT EXISTS silver_subject (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(255),
    subject_slug VARCHAR(255) UNIQUE,
    first_seen_batch_id VARCHAR(50)
);


-- 3. WORK TABLE
CREATE TABLE IF NOT EXISTS silver_work (
    work_key VARCHAR(50) PRIMARY KEY,
    title TEXT,
    first_publish_year INT,
    edition_count INT,
    has_fulltext TINYINT(1),
    language_count INT,
    subject_text TEXT,
    source_batch_id VARCHAR(50)
);

-- 4. AUTHOR TABLE
CREATE TABLE IF NOT EXISTS silver_author (
    author_key VARCHAR(50) PRIMARY KEY,        
    author_name VARCHAR(255),
    birth_date VARCHAR(50),
    top_work TEXT,
    work_count INT,
    source_batch_id VARCHAR(50)
);


-- 5. WORK-AUTHOR TABLE
CREATE TABLE IF NOT EXISTS silver_work_author (
    work_key VARCHAR(50),
    author_key VARCHAR(50),
    source_batch_id VARCHAR(50),
    PRIMARY KEY (work_key, author_key),
    FOREIGN KEY (work_key) REFERENCES silver_work(work_key),
    FOREIGN KEY (author_key) REFERENCES silver_author(author_key)
);


-- 6. WORK-SUBJECT TABLE
CREATE TABLE IF NOT EXISTS silver_work_subject (
    work_key VARCHAR(50),
    subject_name VARCHAR(255),
    source_batch_id VARCHAR(50),
    PRIMARY KEY (work_key, subject_name),
    FOREIGN KEY (work_key) REFERENCES silver_work(work_key)
);


-- 7. SNAPSHOT TABLE
CREATE TABLE IF NOT EXISTS silver_work_search_snapshot (
    batch_id VARCHAR(50),
    subject_name VARCHAR(255),
    work_key VARCHAR(50),
    search_rank INT,
    api_page INT,
    raw_title TEXT,
    raw_author_text TEXT,
    PRIMARY KEY (batch_id, subject_name, work_key),
    FOREIGN KEY (work_key) REFERENCES silver_work(work_key)
);
