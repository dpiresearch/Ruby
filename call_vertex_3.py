
# from google import genai
import google.generativeai as genai
from google.genai import types
import base64
import os

# model = genai.GenerativeModel("gemini-1.5-flash")
model = genai.GenerativeModel("gemini-2.0-flash-exp")

api_key = os.getenv('GOOGLE_DPIRSRCH_API_KEY')
genai.configure(api_key=api_key)

# doc_path = "./forVertex/FFF1C3ED-DFA4-446D-A247-20582851BE28.txt" # Replace with the actual path to your local PDF
doc_path = "./forVertex/AA94FF8B-D4D3-41A4-B218-C5AD798CB8CE.txt" # Replace with the actual path to your local PDF

# Read and encode the local file
with open(doc_path, "rb") as doc_file:
    doc_data = base64.standard_b64encode(doc_file.read()).decode("utf-8")

prompt = "In the attached file, find all the rows associated with the user identified by 'AA94FF8B-D4D3-41A4-B218-C5AD798CB8CE' and construct a timeline based on the data in the file. Describe what they're doing and what kind of personas this user might fit in."

response = model.generate_content([{'mime_type': 'text/plain', 'data': doc_data}, prompt])

output_filename=doc_path.replace('txt','_response.txt')
with open(output_filename, 'w') as output_file:
    output_file.write(response.text)

print(f"====== OUTPUT WRITTEN to {output_filename}")
print(response.text)
