#
# Attempt to use Claude 3.7 to do analysis as a substitute of Gemini
# Problems: Claude 3.7 max tokesn is 128K vs Gemini which is really large
# Claude does take attachments through the api like Gemini does
# I got the error: Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'messages.0.attachments: Extra inputs are not permitted'}}
#
# When I changed it to include the text of the csv files in the prompt, I got the error:
# Streaming is strongly recommended for operations that may take longer than 10 minutes. See https://github.com/anthropics/anthropic-sdk-python#long-requests for more details
#
# Currently giving up for now
#
import os
import glob
import anthropic
from pathlib import Path
import time
import pandas as pd
import tiktoken

# Initialize the Anthropic client
client = anthropic.Anthropic(
    api_key=os.getenv('ANTHROPIC_API_KEY')
)

# Initialize tokenizer
encoding = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    return len(encoding.encode(text))

def chunk_dataframe(df, max_rows_per_chunk=1000):
    """Split dataframe into chunks of approximately equal size"""
    num_chunks = (len(df) + max_rows_per_chunk - 1) // max_rows_per_chunk
    return [df[i:i + max_rows_per_chunk] for i in range(0, len(df), max_rows_per_chunk)]

# Create output directory for analysis results if it doesn't exist
os.makedirs('./large_analysis', exist_ok=True)

# Get all CSV files from the users directory
user_files = glob.glob('./large_users/*.csv')

for file_path in user_files:
    # Extract the user ID from the filename
    user_id = os.path.basename(file_path).replace('.csv', '')
    print(f"Processing user: {user_id}")
    
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Split data into chunks if needed
        chunks = chunk_dataframe(df)
        all_analyses = []
        
        for i, chunk_df in enumerate(chunks):
            # Convert DataFrame chunk to string representation
            data_str = chunk_df.to_string()
            
            # Calculate number of chunks (assuming 100KB chunks)
            file_size = os.path.getsize(file_path)
            num_chunks = (file_size + 102400 - 1) // 102400  # Round up division
            
            # Prepare the prompt with the data included
            prompt = f"""In the following data, find all the rows associated with the user identified by '{user_id}' and construct a timeline based on the data. Describe what they're doing and what kind of personas this user might fit in. Note that this file was processed in {num_chunks} parts due to its size.

Here is the data:
{data_str}"""
            
            # Check token count
            token_count = count_tokens(prompt)
            if token_count > 96000:  # Leave some room for the response
                print(f"Warning: Chunk {i+1} is too large ({token_count} tokens). Skipping...")
                continue
            
            # Create the message with Claude
            message = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=128000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            all_analyses.append(message.content[0].text)
            
            # Add a small delay to avoid rate limiting
            time.sleep(1)
        
        # Combine all analyses and save to file
        if all_analyses:
            output_path = f'./large_analysis/{user_id}_analysis.txt'
            with open(output_path, 'w') as f:
                f.write("\n\n---\n\n".join(all_analyses))
            print(f"Analysis saved for user {user_id}")
        else:
            print(f"No analysis generated for user {user_id} due to size constraints")
        
    except Exception as e:
        print(f"Error processing user {user_id}: {str(e)}")
        continue

print("Analysis complete!") 