import pandas as pd
import os 
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

def load_raw_data(file_path: str) -> pd.DataFrame:
    """
    Load raw data from a CSV file into a pandas DataFrame.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: The loaded data as a pandas DataFrame.
    """
    return pd.read_csv(file_path)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the raw data by handling missing values and duplicates and
    renaming columns to follow snake_case convention.
    Cast boolean columns to True/False and convert total_charges to numeric.

    Args:
        df (pd.DataFrame): The raw data as a pandas DataFrame.

    Returns:
        pd.DataFrame: The cleaned data as a pandas DataFrame.
    """
    df = df.drop_duplicates()
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df = df.dropna(subset=["TotalCharges"])
    
    # Rename columns to follow snake_case convention
    df = df.rename(columns={
    "customerID": "customer_id",
    "SeniorCitizen": "senior_citizen",
    "Partner": "partner",
    "Dependents": "dependents",
    "PhoneService": "phone_service",
    "MultipleLines": "multiple_lines",
    "InternetService": "internet_service",
    "OnlineSecurity": "online_security",
    "OnlineBackup": "online_backup",
    "DeviceProtection": "device_protection",
    "TechSupport": "tech_support",
    "StreamingTV": "streaming_tv",
    "StreamingMovies": "streaming_movies",
    "Contract": "contract_type",
    "PaperlessBilling": "paperless_billing",
    "PaymentMethod": "payment_method",
    "MonthlyCharges": "monthly_charges",
    "TotalCharges": "total_charges",
    "Churn": "churn_label"
    })
    
    # boolean casts
    df["senior_citizen"] = df["senior_citizen"].astype(bool)
    
    yes_no_columns = [
        "partner",
        "dependents",
        "phone_service",
        "paperless_billing", 
        "churn_label"
    ]
    
    for col in yes_no_columns:  
        df[col] = df[col].map({"Yes": True, "No": False})
    
    return df


def load_to_db(df: pd.DataFrame) -> None:
        
    DATABASE_URL = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}")
    
    engine = create_engine(DATABASE_URL)
    
    df.to_sql(
        name="customers",
        con=engine,
        if_exists="append",
        index=False
    )
    
    print(f"Loaded {len(df)} records into the 'customers' table in the database.")
    
    
if __name__ == "__main__":
    
    print("Starting data ingestion...")
    raw_data_path = "data/raw/telco_churn.csv"
    raw_df = load_raw_data(raw_data_path)
    print(f"Loaded {len(raw_df)} records from the raw data file.")
    cleaned_df = clean_data(raw_df)
    load_to_db(cleaned_df)
    
    print("Data ingestion completed successfully.")
        
        

        