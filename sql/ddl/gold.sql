-- 1.Which subject contains the most works?
CREATE TABLE IF NOT EXISTS gold_subject_work_count AS
SELECT 
    subject_name,
    COUNT(DISTINCT work_key) AS total_works
FROM silver_work_subject
GROUP BY subject_name;

-- 2.Which subject has the highest author diversity?
CREATE TABLE IF NOT EXISTS gold_subject_author_diversity AS
SELECT 
    ws.subject_name,
    COUNT(DISTINCT wa.author_key) AS unique_authors
FROM silver_work_subject ws
JOIN silver_work_author wa 
    ON ws.work_key = wa.work_key
GROUP BY ws.subject_name;

-- 3.Which authors appear most often in database-related subjects?
CREATE TABLE IF NOT EXISTS gold_top_database_authors AS
SELECT 
    a.author_name,
    COUNT(*) AS work_count
FROM silver_work_subject ws
JOIN silver_work_author wa 
    ON ws.work_key = wa.work_key
JOIN silver_author a 
    ON wa.author_key = a.author_key
WHERE LOWER(ws.subject_name) LIKE '%database%'
GROUP BY a.author_name;

-- 4.Publication year distribution per subject
CREATE TABLE IF NOT EXISTS gold_publication_stats AS
SELECT 
    ws.subject_name,
    MIN(w.first_publish_year) AS min_year,
    MAX(w.first_publish_year) AS max_year,
    ROUND(AVG(w.first_publish_year), 0) AS avg_year
FROM silver_work_subject ws
JOIN silver_work w 
    ON ws.work_key = w.work_key
WHERE w.first_publish_year IS NOT NULL
GROUP BY ws.subject_name;

--5.Which subject has the newest average publication year?
CREATE TABLE IF NOT EXISTS gold_subject_recency AS
SELECT 
    ws.subject_name,
    ROUND(AVG(w.first_publish_year), 0) AS avg_year
FROM silver_work_subject ws
JOIN silver_work w 
    ON ws.work_key = w.work_key
WHERE w.first_publish_year IS NOT NULL
GROUP BY ws.subject_name;



