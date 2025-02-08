

import google.generativeai as genai
from google.genai import types
import base64
import os
import time

model = genai.GenerativeModel("gemini-2.0-flash-exp")

api_key = os.getenv('GOOGLE_DPIRSRCH_API_KEY')
genai.configure(api_key=api_key)

doc_directory = "./wcp_1"  # Directory containing the files
total_time = 0
# Iterate over each file in the directory
for filename in os.listdir(doc_directory):
    if filename.endswith('.txt'):  # Process only .txt files
        start_time = time.time()  # Start timing for this iteration

        doc_path = os.path.join(doc_directory, filename)  # Full path to the file

        # Read and encode the local file
        with open(doc_path, "rb") as doc_file:
            doc_data = base64.standard_b64encode(doc_file.read()).decode("utf-8")

        prompt = f"In the attached file, find all the rows associated with the user identified by '{filename[:-4]}' and construct a timeline based on the data in the file. Describe what they're doing and what kind of personas this user might fit in."

        response = model.generate_content([{'mime_type': 'text/plain', 'data': doc_data}, prompt])

        output_filename = doc_path.replace('.txt', '_response.txt')
        with open(output_filename, 'w') as output_file:
            output_file.write(response.text)

        print(f"====== OUTPUT WRITTEN to {output_filename}")
        print(response.text)

        end_time = time.time()  # End timing for this iteration
        iteration_time = end_time - start_time  # Calculate time taken for this iteration
        total_time += iteration_time  # Accumulate total time
        print(f"Time taken for {filename}: {iteration_time:.2f} seconds")  # Print time for this iteration

# Print total time taken after processing all files
print(f"Total time taken: {total_time:.2f} seconds")

