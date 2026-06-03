import sys
import os
import logging
from datetime import datetime


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#logging
os.makedirs("data/logs", exist_ok=True)

logging.basicConfig(
    filename='data/logs/pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from src.extract.extract import extract_data
from src.transform.transform import transform_data
from src.quality.quality import run_quality_checks
from src.load.load import load_data

def run_pipeline():
    print("Pipeline Started...\n")

    print(" Running Extract Step...")

    batch_id = extract_data()

    print("\n Started Transform Step...")
    data = transform_data(batch_id)

    for name, df in data.items():
        print(f"\n{name.upper()} TABLE")
        print(df.head())

    print("\nchecking quality")

    data = run_quality_checks(data)

    print("loading into sql")

    data = load_data(data, batch_id)

    print("successful laoding")
    

if __name__ == "__main__":
    run_pipeline()                                       

      
      