import csv
from langchain_ollama import OllamaLLM

def call_ollama_with_csv(model_str, csv_file, prompt):
    """Calls Ollama LLaVA with the content of a CSV file."""

    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file)
        csv_content = "\n".join([",".join(row) for row in csv_reader])

#     model = OllamaLLM(model="llava:34b-v1.6")  # Or any other LLaVA model
#    model = OllamaLLM(model="llava")  # Or any other LLaVA model
    model = OllamaLLM(model=model_str)  # Or any other LLaVA model
    response = model.invoke(f"{prompt}\n{csv_content}")
    return response

# Example usage
# csv_file_path = '/Users/dpang/Documents/Ruby2025/output_2024-03-01_to_2024-08-29.csv'
#csv_file_path = '/Users/dpang/Documents/Ruby2025/test.csv'
csv_file_path = '/Users/dpang/Documents/Ruby2025/test_100000.csv'
'''
prompts = [
    "Summarize the content of this CSV file:",
    "What are the key insights from this data?",
    "Provide a brief analysis of the trends in the CSV."
]
'''

'''
prompts = [
    "Can you list all the properties that have interesting data",
    "Of the data that is interesting, which ones are categorical and which are numerical?",
    "Can you tell me if you can distinguish one user from another in this data?",
    "Can you cluster users into specific buying groups?"
]
'''

prompts = [
    "For the file that was uploaded, how many rows are there?",
    "Each user is identifiedy through the colum 'properties_$user_id' or 'properties_distinct_id'.  From the different users you have identified here, can you identify 3 top demographics?",
    "Of the demographics that were identified, how many users are in each",
    "Take one of the demographics identified and list all the users associated with it"
]

model_str = "llava-llama3"

print(f"Using model {model_str}")
for prompt_text in prompts:
    response = call_ollama_with_csv(model_str, csv_file_path, prompt_text)
    print(f"==={prompt_text}===")
    print(response)
    print("\n")
