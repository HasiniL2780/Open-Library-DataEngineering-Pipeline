import logging

logger = logging.getLogger(__name__)


def run_quality_checks(data_dict):

    logging.info("\nRunning Data Quality Checks...\n")

    work_df = data_dict["work"]
    author_df = data_dict["author"]
    work_author_df = data_dict["work_author"]

 
    # 1. work_key must not be null
    if work_df["work_key"].isnull().any():
        logging.info("Removing rows with NULL work_key")
        work_df = work_df[work_df["work_key"].notnull()]

    logging.info("work_key null check passed")


    # 2. author_key must not be null
    if author_df["author_key"].isnull().any():
        logging.info(" Removing rows with NULL author_key")
        author_df = author_df[author_df["author_key"].notnull()]

    logging.info("author_key null check passed")

  
    # 3. Remove duplicates in work_author
    before = len(work_author_df)
    work_author_df = work_author_df.drop_duplicates(subset=["work_key", "author_key"])
    after = len(work_author_df)

    if before != after:
        logging.info(f"Removed {before - after} duplicate rows from work_author")

    logging.info("work_author duplicate check passed")


    # 4. first_publish_year valid range
    if "first_publish_year" in work_df.columns:
        before = len(work_df)

        work_df = work_df[
            (work_df["first_publish_year"].isnull()) |
            ((work_df["first_publish_year"] >= 1000) &
             (work_df["first_publish_year"] <= 2025))
        ]

        after = len(work_df)

        if before != after:
            logging.info(f"Removed {before - after} invalid publish year rows")

    logging.info(" publish year check passed")


    # 5. work_key in work_author must exist in work
    valid_work_keys = set(work_df["work_key"])
    before = len(work_author_df)

    work_author_df = work_author_df[
        work_author_df["work_key"].isin(valid_work_keys)
    ]

    after = len(work_author_df)

    if before != after:
        logging.info(f" Removed {before - after} invalid work_key references")

    logging.info("work_key foreign key check passed")


    # 6. author_key in work_author must exist in author
    valid_author_keys = set(author_df["author_key"])
    before = len(work_author_df)

    work_author_df = work_author_df[
        work_author_df["author_key"].isin(valid_author_keys)
    ]

    after = len(work_author_df)

    if before != after:
        logging.info(f" Removed {before - after} invalid author_key references")

    logging.info(" author_key foreign key check passed")

    # UPDATE CLEANED DATA BACK
    data_dict["work"] = work_df
    data_dict["author"] = author_df
    data_dict["work_author"] = work_author_df

    logging.info("\n Data Quality Checks Completed (Cleaned Data Ready)\n")

    return data_dict