import requests
import yaml
import os
from tqdm import tqdm
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def extract_data():

    logger.info("Calling API")

    # Load config
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    base_url = config['api']['base_url']
    search_endpoint = config['api']['search_endpoint']
    author_details = config['api']['authors']['author_details']
    author_works = config['api']['authors']['author_works']
    work_details = config['api']['authors']['work_details']
    max_pages = config['max_pages']
    subjects = config['subjects']

    # Create batch folder
    batch_id = datetime.now().strftime("%d%m%Y_%H%M%S")
    base_path = f"data/bronze/openlibrary/{batch_id}"

    os.makedirs(f"{base_path}/subjects", exist_ok=True)
    os.makedirs(f"{base_path}/author", exist_ok=True)
    os.makedirs(f"{base_path}/author-works", exist_ok=True)
    os.makedirs(f"{base_path}/work-details", exist_ok=True)

    list_author_keys = []
    list_work_keys = []

    # SUBJECT DATA
    for subject in tqdm(subjects, desc='Subjects'):

        clean_subject = subject.replace(" ", "_")

        for page in tqdm(range(1, max_pages + 1), desc='Pages', leave=False):

            url = base_url + search_endpoint.format(subject=subject, page=page)

            try:
                response = requests.get(url)
                if response.status_code != 200:
                    continue
                data = response.json()
            except:
                continue

            if "docs" not in data:
                continue

            for doc in data["docs"]:

                if 'author_key' in doc:
                    for key in doc['author_key']:
                        list_author_keys.append(key)

                if 'key' in doc:
                    work_key = doc['key'].split('/')[-1]
                    list_work_keys.append(work_key)

            file_path = f"{base_path}/subjects/{clean_subject}_page{page}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)

    list_author_keys = list(set(list_author_keys))
    list_work_keys = list(set(list_work_keys))

    # AUTHOR DETAILS
    for auth in tqdm(list_author_keys, desc='Author Details'):

        url = base_url + author_details.format(author_key=auth)

        try:
            response = requests.get(url)
            if response.status_code != 200:
                continue
            data = response.json()
        except:
            continue

        file_path = f"{base_path}/author/{auth}.json"
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    # AUTHOR WORKS
    for auth in tqdm(list_author_keys, desc='Author Works'):

        url = base_url + author_works.format(author_key=auth)

        try:
            response = requests.get(url)
            if response.status_code != 200:
                continue
            data = response.json()
        except:
            continue

        file_path = f"{base_path}/author-works/work_of_{auth}.json"
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    # WORK DETAILS
    for work in tqdm(list_work_keys, desc='Work Details'):

        url = base_url + work_details.format(work_key=work)

        try:
            response = requests.get(url)
            if response.status_code != 200:
                continue
            data = response.json()
        except:
            continue

        file_path = f"{base_path}/work-details/{work}.json"
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    logger.info("Bronze Layer Completed")

    return batch_id         