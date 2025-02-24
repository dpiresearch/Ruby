#
# Read the filtered and raw files from s3
# 
import boto3
import pandas as pd
from io import StringIO
import json
import os

# Set AWS credentials (these can also be set using environment variables or AWS CLI config)
aws_access_key_id = os.getenv("AWS_ACCESS_KEY")
aws_secret_access_key = os.getenv("AWS_SECRET")
#aws_session_token = 'YOUR_AWS_SESSION_TOKEN'  # If you use temporary session credentials

# Create a session using provided credentials
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
#    aws_session_token=aws_session_token
)

# S3 client
s3 = session.client('s3')

# Function to read CSV file from S3
def read_csv_from_s3(bucket, key):
    csv_obj = s3.get_object(Bucket=bucket, Key=key)
    csv_data = csv_obj['Body'].read().decode('utf-8')
    return pd.read_csv(StringIO(csv_data))

# Function to read JSONL file from S3
def read_jsonl_from_s3(bucket, key):
    jsonl_obj = s3.get_object(Bucket=bucket, Key=key)
    jsonl_data = jsonl_obj['Body'].read().decode('utf-8').splitlines()
    return [json.loads(line) for line in jsonl_data]

# Define the S3 URLs
filtered_bucket = 'ruby-mixpanel-data'
filtered_key = 'filtered_output_2024-03-01_to_2025-01-22.csv'
raw_bucket = 'ruby-mixpanel-data'
raw_key = 'output_2024-03-01_to_2025-01-22.jsonl'

# Read the files
#filtered_df = read_csv_from_s3(filtered_bucket, filtered_key)
raw_data = read_jsonl_from_s3(raw_bucket, raw_key)

filename='raw_users.csv'
with open(filename, 'w', encoding='utf-8') as file:
    for line in raw_data:
        json_line = json.dumps(line)
        file.write(json_line + '\n')

# Show the data
#print("Filtered DataFrame:")
#print(filtered_df.head())

print("\nRaw Data (first 2 lines):")
print(raw_data[:2])  # Display first two records of the raw JSONL data

# filtered_df.to_csv('filtered.csv', index=False)
raw_data.to_csv('raw_data.csv', index=False)
