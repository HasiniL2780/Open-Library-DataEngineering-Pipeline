import os
import json
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def transform_data(batch_id):
    logger.info("Starting transformation")
    bronze_path = f"data/bronze/openlibrary/{batch_id}"


    # AUTHOR TABLE
    def silver_author():
        folder_path = f"{bronze_path}/author"
        rows = []

        for file in os.listdir(folder_path):
            with open(f"{folder_path}/{file}", 'r') as f:
                data = json.load(f)
                          
            rows.append({
                "author_key": data.get("key", "").split("/")[-1],
                "author_name": data.get("name"),
                "birth_date": data.get("birth_date"),
                "top_work": data.get("top_work"),
                "work_count": data.get("work_count"),
                "source_batch_id": batch_id
            })

        return pd.DataFrame(rows).drop_duplicates()

    # SUBJECT TABLE
    def silver_subject():
        subjects_path = f"{bronze_path}/subjects"
        subject_set = set()

        for file in os.listdir(subjects_path):
            subject_name = file.split("_page")[0].replace("_", " ")
            subject_set.add(subject_name)

        rows = []
        for idx, sub in enumerate(subject_set):
            rows.append({
                "subject_id": idx + 1,
                "subject_name": sub,
                "subject_slug": sub.lower().replace(" ", "_"),
                "first_seen_batch_id": batch_id
            })

        return pd.DataFrame(rows)

    # WORK TABLE
    def silver_work():
        subjects_path = f"{bronze_path}/subjects"
        rows = []

        for file in os.listdir(subjects_path):
            with open(f"{subjects_path}/{file}", 'r') as f:
                data = json.load(f)

            for doc in data.get("docs", []):
                rows.append({
                    "work_key": doc.get("key", "").split("/")[-1],
                    "title": doc.get("title"),
                    "first_publish_year": doc.get("first_publish_year"),
                    "edition_count": doc.get("edition_count"),
                    "has_fulltext": doc.get("has_fulltext"),
                    "language_count": len(doc.get("language", [])) if doc.get("language") else 0,
                    "subject_text": ",".join(doc.get("subject", [])) if doc.get("subject") else None,
                    "source_batch_id": batch_id
                })

        return pd.DataFrame(rows).drop_duplicates()

    # WORK-AUTHOR TABLE
    def silver_work_author():
        subjects_path = f"{bronze_path}/subjects"
        rows = []

        for file in os.listdir(subjects_path):
            with open(f"{subjects_path}/{file}", 'r') as f:
                data = json.load(f)

            for doc in data.get("docs", []):
                work_key = doc.get("key", "").split("/")[-1]

                if "author_key" in doc:
                    for a in doc["author_key"]:      
                        rows.append({
                            "work_key": work_key,
                            "author_key": a,
                            "source_batch_id": batch_id
                        })

        return pd.DataFrame(rows).drop_duplicates()

    # WORK-SUBJECT TABLE
    def silver_work_subject():
        subjects_path = f"{bronze_path}/subjects"
        rows = []

        for file in os.listdir(subjects_path):

        #Extract subject from filename (RELIABLE)
            subject_name = file.split("_page")[0]
            subject_name = subject_name.replace("_", " ").strip()

            with open(f"{subjects_path}/{file}", 'r') as f:
                data = json.load(f)

            for doc in data.get("docs", []):
                work_key = doc.get("key", "").split("/")[-1]

                if not work_key:
                    continue

                rows.append({
                    "work_key": work_key,
                    "subject_name": subject_name,
                    "source_batch_id": batch_id
                })

        return pd.DataFrame(rows).drop_duplicates()
      
    # SNAPSHOT TABLE
    def silver_snapshot():
        
        subjects_path = f"{bronze_path}/subjects"
        rows = []

        for file in os.listdir(subjects_path):
            subject_name = file.split("_page")[0].replace("_", " ")

            with open(f"{subjects_path}/{file}", 'r') as f:
                data = json.load(f)

            for idx, doc in enumerate(data.get("docs", [])):
                rows.append({
                    "batch_id": batch_id,
                    "subject_name": subject_name,
                    "work_key": doc.get("key", "").split("/")[-1],
                    "search_rank": idx + 1,
                    "api_page": 1,
                    "raw_title": doc.get("title"),
                    "raw_author_text": str(doc.get("author_name"))
                })

        return pd.DataFrame(rows)
    
    return {
        "author": silver_author(),
        "subject": silver_subject(),
        "work": silver_work(),
        "work_author": silver_work_author(),
        "work_subject": silver_work_subject(),
        "snapshot": silver_snapshot()
    }





