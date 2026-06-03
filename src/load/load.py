import mysql.connector
from datetime import datetime
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Hasini@2780",
        database="openlibrary"
    )


#  Convert NaN -> None
def clean_dataframe(df):
    return df.astype(object).where(pd.notnull(df), None)


def load_data(data_dict, batch_id):

    logger.info("\nLoading Data into MySQL...\n")

    conn = get_connection()
    cursor = conn.cursor()

    total_rows = 0
    start_time = datetime.now()

    #  Clean ALL dataframes
    for key in data_dict:
        data_dict[key] = clean_dataframe(data_dict[key])

    # 1. INSERT BATCH TABLE
    cursor.execute("""
        INSERT INTO silver_ingestion_batch 
        (batch_id, source_name, load_start_ts, status, records_fetched, records_loaded)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (batch_id, "openlibrary", start_time, "STARTED", 0, 0))

    # 2. SUBJECT TABLE
    for _, row in data_dict["subject"].iterrows():
        cursor.execute("""
            INSERT IGNORE INTO silver_subject VALUES (%s, %s, %s, %s)
        """, tuple(row.values))
        total_rows += 1

    logger.info("Subject table loaded")

    # 3. WORK TABLE
    for _, row in data_dict["work"].iterrows():
        cursor.execute("""
            INSERT IGNORE INTO silver_work VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, tuple(row.values))
        total_rows += 1

    logger.info("Work table loaded")


    # 4. AUTHOR TABLE
    for _, row in data_dict["author"].iterrows():
        cursor.execute("""
            INSERT IGNORE INTO silver_author VALUES (%s, %s, %s, %s, %s, %s)
        """, tuple(row.values))
        total_rows += 1

    logger.info("Author table loaded")


    # 5. WORK-AUTHOR TABLE
    for _, row in data_dict["work_author"].iterrows():
        cursor.execute("""
            INSERT IGNORE INTO silver_work_author VALUES (%s, %s, %s)
        """, tuple(row.values))
        total_rows += 1

    logger.info("Work-Author table loaded")


    # 6. WORK-SUBJECT TABLE
    for _, row in data_dict["work_subject"].iterrows():
        cursor.execute("""
            INSERT IGNORE INTO silver_work_subject VALUES (%s, %s, %s)
        """, tuple(row.values))
        total_rows += 1

    logger.info("Work-Subject table loaded")


    # 7. SNAPSHOT TABLE
    for _, row in data_dict["snapshot"].iterrows():
        cursor.execute("""
            INSERT IGNORE INTO silver_work_search_snapshot 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, tuple(row.values))
        total_rows += 1

    logger.info("Snapshot table loaded")

  
    # 8. UPDATE BATCH TABLE
    end_time = datetime.now()

    cursor.execute("""
        UPDATE silver_ingestion_batch
        SET load_end_ts = %s,
            status = %s,
            records_loaded = %s
        WHERE batch_id = %s
    """, (end_time, "COMPLETED", total_rows, batch_id))

    conn.commit()

    cursor.close()
    conn.close()

    logger.info(f"\nLoad Completed Successfully! Rows inserted: {total_rows}\n")