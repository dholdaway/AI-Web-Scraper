import os
import json
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Initialize Ollama model
model = OllamaLLM(model="llama3.1:8b")

# Define directories and parsing configuration
CVE_RESULTS_DIR = "./cve_results"
PARSING_RESULTS_DIR = "./parsing_results"
os.makedirs(PARSING_RESULTS_DIR, exist_ok=True)

# Define the template for parsing task
template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully:\n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}.\n"
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response.\n"
    "3. **Empty Response:** If no information matches the description, return an empty string ('').\n"
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

# Prompt Template for LangChain
prompt = ChatPromptTemplate.from_template(template)

# Function to parse content with Ollama
def parse_with_ollama(content_file, parse_description):
    with open(content_file, "r") as f:
        content = f.read()

    # Split content into manageable chunks (3,000 characters each for processing)
    chunks = [content[i:i + 3000] for i in range(0, len(content), 3000)]
    chain = prompt | model
    parsed_results = []

    for i, chunk in enumerate(chunks, start=1):
        try:
            # Process each chunk
            response = chain.invoke({"dom_content": chunk, "parse_description": parse_description})
            print(f"Processed chunk {i}/{len(chunks)}")  # Optional: verbose logging
            parsed_results.append(response)
        except Exception as e:
            print(f"Error processing chunk {i}: {e}")
            parsed_results.append("")

    # Combine results and clean up empty responses
    final_output = "\n".join(parsed_results).strip()
    return final_output if final_output else "No matching content found."

# Process all content files for a specific CVE
def process_cve_content(cve_id, parse_description):
    content_dir = os.path.join(CVE_RESULTS_DIR, cve_id, "content")
    output_file = os.path.join(PARSING_RESULTS_DIR, f"{cve_id}_parsed.json")
    parsed_data = {}

    # Process each file in the content directory
    for file_name in os.listdir(content_dir):
        file_path = os.path.join(content_dir, file_name)
        if os.path.isfile(file_path):
            # Parse content and add it to structured results
            parsed_content = parse_with_ollama(file_path, parse_description)
            parsed_data[file_name] = parsed_content

    # Save structured results to JSON
    with open(output_file, "w") as f:
        json.dump(parsed_data, f, indent=2)

    print(f"Parsed data saved to {output_file}")

# Example usage
if __name__ == "__main__":
    cve_id = "CVE-2024-10487"  # Example CVE ID
    parse_description = "solutions, mitigations, and technical insights"
    process_cve_content(cve_id, parse_description)
