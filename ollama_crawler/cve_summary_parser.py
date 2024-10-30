import json
import re
import spacy
import pandas as pd
import os
from collections import defaultdict
from nltk.tokenize import sent_tokenize

# Load Spacy NLP model for NER
nlp = spacy.load("en_core_web_sm")

# Define directory for parsed JSON files
PARSING_RESULTS_DIR = "./parsing_results/"

# Function to clean and normalize text
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespaces
    text = re.sub(r'\(.*?\)', '', text)  # Remove text in parentheses
    return text.strip()

# Function to extract critical information from text using NLP
def extract_key_info(text):
    doc = nlp(text)
    info = {
        "solutions": [],
        "mitigations": [],
        "technical_insights": [],
        "affected_versions": [],
        "severity": None
    }
    sentences = sent_tokenize(text)  # Break down into sentences for granularity

    # Extract entities
    for sentence in sentences:
        sent_doc = nlp(sentence)
        entities = {ent.label_: ent.text for ent in sent_doc.ents}
        
        if "solution" in sentence.lower():
            info["solutions"].append(clean_text(sentence))
        elif "mitigation" in sentence.lower() or "prevent" in sentence.lower():
            info["mitigations"].append(clean_text(sentence))
        elif "technical insight" in sentence.lower() or "exploit" in sentence.lower():
            info["technical_insights"].append(clean_text(sentence))
        
        if "CVE" in sentence:
            info["affected_versions"].append(clean_text(sentence))
        
        if "score" in entities:
            info["severity"] = entities.get("score")

    return info

# Aggregate information by CVE ID
cve_summary = defaultdict(lambda: defaultdict(list))

# Process each JSON file in the parsing results directory
for file_name in os.listdir(PARSING_RESULTS_DIR):
    if file_name.endswith("_parsed.json"):
        cve_id = file_name.split("_parsed.json")[0]  # Extract CVE ID from filename
        file_path = os.path.join(PARSING_RESULTS_DIR, file_name)
        
        # Read the parsed JSON file content
        with open(file_path, "r") as f:
            content = json.load(f)
        
        # Process content and aggregate information
        for entry in content.values():
            parsed_content = extract_key_info(entry)
            
            # Aggregate each extracted category
            cve_summary[cve_id]["solutions"].extend(parsed_content["solutions"])
            cve_summary[cve_id]["mitigations"].extend(parsed_content["mitigations"])
            cve_summary[cve_id]["technical_insights"].extend(parsed_content["technical_insights"])
            cve_summary[cve_id]["affected_versions"].extend(parsed_content["affected_versions"])
            if parsed_content["severity"]:
                cve_summary[cve_id]["severity"] = parsed_content["severity"]

# Convert to DataFrame for better visualization and reporting
summary_df = pd.DataFrame.from_dict(cve_summary, orient="index")
summary_df = summary_df.applymap(lambda x: "\n".join(set(x)) if isinstance(x, list) else x)

# Save summary report to CSV or JSON
summary_df.to_csv("cve_summary_report.csv", index=True)
summary_df.to_json("cve_summary_report.json", orient="index", indent=2)

print("Summarization complete. Report saved to cve_summary_report.csv and cve_summary_report.json.")
