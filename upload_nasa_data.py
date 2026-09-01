import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in .env")
        print("Please add your SUPABASE_SERVICE_ROLE_KEY to your .env file to bypass RLS.")
        return

    supabase: Client = create_client(url, key)

    file_path = "data/HPC_Degradation/train_FD001.txt"
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return

    print("Reading NASA CMAPSS Data (train_FD001)...")
    
    # CMAPSS text files are space-separated with 26 columns
    columns = ["unit", "cycle", "setting1", "setting2", "setting3"] + [f"sensor_{i}" for i in range(1, 22)]
    df = pd.read_csv(file_path, sep=r'\s+', header=None, names=columns)
    
    # Add a dataset identifier
    df['dataset_id'] = 'FD001_train'

    print(f"Total rows to upload: {len(df)}")
    records = df.to_dict('records')

    # Upload in chunks of 500 to avoid payload size limits in PostgREST
    batch_size = 500
    success = True
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        print(f"Uploading batch {i} to {i + len(batch)}...")
        try:
            response = supabase.table("nasa_cmapss_telemetry").insert(batch).execute()
        except Exception as e:
            print(f"Failed to upload batch {i}: {e}")
            success = False
            break
        
    if success:
        print("✅ NASA Data Upload Complete!")
    else:
        print("❌ Upload failed before completion.")

if __name__ == "__main__":
    main()
