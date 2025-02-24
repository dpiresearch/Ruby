#
# Grab all the txt files from doc_directory
# Call LLM to characterize the txt
# output to <filename>_response.txt
# Track timings


import google.generativeai as genai
from google.genai import types
import base64
import boto3
import os
import time

aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
aws_secret_access_key = os.getenv('AWS_SECRET_KEY')


print(f"Got access { aws_access_key_id}, got secrete {aws_secret_access_key}")

# Create a session using provided credentials
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
#    aws_session_token=aws_session_token
)
s3 = session.client('s3')

bucket_name = 'rubybucket1'
prefix = 'wcp'
response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

model = genai.GenerativeModel("gemini-2.0-flash-exp")

api_key = os.getenv('GOOGLE_DPIRSRCH_API_KEY')
genai.configure(api_key=api_key)

total_time = 0

# Extract file details and sort by size
files = []
if 'Contents' in response:
    for obj in response['Contents']:
        files.append({
            'Key': obj['Key'],
            'Size': obj['Size']
        })

# Sort files by size in ascending order
sorted_files = sorted(files, key=lambda x: x['Size'])
response_files = [file for file in sorted_files if file['Key'].endswith('_response.txt')]
response_filenames = [file['Key'] for file in sorted_files if file['Key'].endswith('_response.txt')]

# Print the sorted list of files
for file in sorted_files:
    print(f"=== Processing File: {file['Key']}, Size: {file['Size']} bytes")
    filename = file['Key']
    if filename in response_filenames: # This gets rid of the _response.txt files
        print(f"Skipping {filename}")
        continue
    if filename.endswith('.txt'):  # Process only .txt files
        output_filename = filename.replace('.txt', '_response.txt') 
        if output_filename in response_filenames: # Output file already generated, skipping 
            print(f"Skipping {filename}")
            continue
        start_time = time.time()  # Start timing for this iteration

        s3_response = s3.get_object(Bucket=bucket_name, Key=filename)
        doc_data = s3_response['Body'].read() # Full path to the file

        encoded_data = base64.standard_b64encode(doc_data).decode("utf-8")

        prompt = f"In the attached file, find all the rows associated with the user identified by '{filename[:-4]}' and construct a timeline based on the data in the file. Describe what they're doing and what kind of personas this user might fit in."

        response = model.generate_content([{'mime_type': 'text/plain', 'data': encoded_data}, prompt])


        s3.put_object(Bucket=bucket_name, Key=output_filename, Body=response.text)

        print(f"====== OUTPUT WRITTEN to {output_filename}")
        print(response.text)

        end_time = time.time()  # End timing for this iteration
        iteration_time = end_time - start_time  # Calculate time taken for this iteration
        total_time += iteration_time  # Accumulate total time
        print(f"Time taken for {filename}: {iteration_time:.2f} seconds")  # Print time for this iteration

# Print total time taken after processing all files
print(f"Total time taken: {total_time:.2f} seconds")


