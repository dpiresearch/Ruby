import os
import time
import pandas as pd
import glob

# Create last_month directory if it doesn't exist
os.makedirs('./last_month', exist_ok=True)

# Get all CSV files from the users directory
user_files = glob.glob('./users/*.txt')

for file_path in user_files:
    # Extract the user ID from the filename
    user_id = os.path.basename(file_path).replace('.txt', '')
    
    # Load the CSV file
    data = pd.read_csv(file_path)
    
    # Convert the 'to_date' column to datetime format
    data['to_date'] = pd.to_datetime(data['to_date'])
    
    # Find the maximum date, which is the most recent activity
    max_date = data['to_date'].max()
    
    # Calculate the first date of the last month of activity
    first_date_of_last_month = max_date - pd.DateOffset(months=1)
    
    # Filter the data to keep only the records from the last month
    last_month_data = data[data['to_date'] >= first_date_of_last_month]
    
    # Save the filtered data to the last_month directory
    output_path = f'./last_month/{user_id}_month.txt'
    last_month_data.to_csv(output_path, index=False)
    print(f"Processed {user_id}: {len(last_month_data)} records from last month")
