#
# Take all the persona files and compile a persona.csv and user_persona.csv
# Persona.csv file holds all the personas identified in the _response.txt files
# Each persona has a persona_id
#
# User_persona.csv holds all the user/device_ids and their associations/membership with'
# a persona_id
#
import os
import json
import csv
import hashlib
import boto3
import os
import time

aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
aws_secret_access_key = os.getenv('AWS_SECRET_KEY')

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
persona_filenames = [file['Key'] for file in sorted_files if file['Key'].endswith('_persona.txt')]

# Define file paths for output
PERSONAS_CSV = "personas.csv"
USER_PERSONAS_CSV = "user_personas.csv"

# Initialize data structures
persona_id_map = {}  # Maps (name, description) to a unique ID
user_persona_mapping = []  # Stores (user_id, persona_id) tuples
next_persona_id = 1  # Auto-incrementing ID for personas

# Directory where persona files are stored
INPUT_DIR = "./"  # Change this if files are in another directory

# Function to generate a consistent hash-based unique ID for a persona
def generate_persona_id(name, description):
    return hashlib.md5(f"{name}-{description}".encode()).hexdigest()[:8]  # Short hash

# Process each _persona.txt file in the directory
for filename in persona_filenames:
    if filename.endswith("_persona.txt"):
        print(f"Processing {filename}")
        s3_response = s3.get_object(Bucket=bucket_name, Key=filename)
        #doc_data = s3_response['Body'].read().decode('utf-8') # Full path to the file
        user_id = filename.split("/")[1].split("_")[0]  # Extract user ID from filename
        try:

            doc_data = s3_response['Body'].read().decode('utf-8').strip()

            # Strip everything before the first '['
            if "[" in doc_data:
                doc_data = doc_data[doc_data.index("["):]  # Keep everything from the first '[' onwards
            # Strip everything after the last ']'
            if "]" in doc_data:
                doc_data = doc_data[:doc_data.rindex("]") + 1]  # Keep everything up to the last ']'

            print(f"Raw Data (First 500 chars): {doc_data}")
           # Load into a JSON object (Python dictionary)
            try:
                data = json.loads(doc_data)
            except json.JSONDecodeError as jsone:
                print(f"Error decoding JSON in {filename}, skipping")
                print(jsone.msg)
                continue

            # Ensure JSON data is a list
            if not isinstance(data, list):
                print(f"Invalid data format in {filename}, expected a list, skipping...")
                continue  # Skip to next file

            for persona in data:
                try:
                    name = persona.get("Persona", "Unknown")
                    description = persona.get("Description", "No description available")
                                    # Generate a unique ID for this persona
                    persona_id = generate_persona_id(name, '')

                    # Store persona if not already in the map
                    if persona_id not in persona_id_map:
                        persona_id_map[persona_id] = (name, description)

                    # Store user-to-persona mapping
                    user_persona_mapping.append((user_id, persona_id))
                except Exception as loop_error:
                    print(f"Error processing persona in {filename}: {loop_error} - Skipping persona...")
        except Exception as e:
            print(f"Unexpected error processing {filename}: {e} - Skipping...")

# Write personas.csv
with open(PERSONAS_CSV, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["persona_id", "name", "description"])  # Header
    for persona_id, (name, description) in persona_id_map.items():
        writer.writerow([persona_id, name, description])

# Write user_personas.csv
with open(USER_PERSONAS_CSV, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["user_id", "persona_id"])  # Header
    for user_id, persona_id in user_persona_mapping:
        writer.writerow([user_id, persona_id])

print(f"Successfully wrote {len(persona_id_map)} unique personas to {PERSONAS_CSV}")
print(f"Successfully wrote {len(user_persona_mapping)} user-persona mappings to {USER_PERSONAS_CSV}")
