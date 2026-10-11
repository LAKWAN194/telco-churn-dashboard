import shutil
from pathlib import Path

import kagglehub

DATASET = "blastchar/telco-customer-churn"
SOURCE_FILE = "WA_Fn-UseC_-Telco-Customer-Churn.csv"
RAW_DATA_PATH = Path("data/raw/telco_churn.csv")


def download_raw_data(destination: Path = RAW_DATA_PATH) -> Path:
    """
    Download the IBM Telco churn CSV from Kaggle and copy it into the project.

    kagglehub caches the file outside the repo in a machine-specific folder,
    so the copy is what gives every other script one fixed path to read from.

    Args:
        destination (Path): Where the CSV should end up inside the project.

    Returns:
        Path: The path the CSV was copied to.
    """
    cache_dir = Path(kagglehub.dataset_download(DATASET))

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(cache_dir / SOURCE_FILE, destination)

    return destination


if __name__ == "__main__":

    print("Downloading the Telco churn dataset...")
    path = download_raw_data()
    print(f"Saved raw data to {path}")
