from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Define template for parsing task
template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully:\n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}.\n"
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response.\n"
    "3. **Empty Response:** If no information matches the description, return an empty string ('').\n"
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

model = OllamaLLM(model="llama3")

def parse_with_ollama(dom_chunks, parse_description, verbose=False):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    parsed_results = []

    for i, chunk in enumerate(dom_chunks, start=1):
        try:
            # Invoke the model on the current chunk
            response = chain.invoke(
                {"dom_content": chunk, "parse_description": parse_description}
            )
            if verbose:
                print(f"Parsed batch {i}/{len(dom_chunks)} - Result length: {len(response)}")
            parsed_results.append(response)
        except Exception as e:
            print(f"Error processing chunk {i}: {e}")
            parsed_results.append("")  # Append empty result in case of error

    # Join results, ensuring an empty string if all results are empty
    final_output = "\n".join(parsed_results).strip()
    return final_output if final_output else "No matching content found."
