import json
import requests
from time import sleep

# Load the CVE summary report generated earlier
with open("cve_summary_report.json", "r", encoding="utf-8") as f:
    cve_summary_data = json.load(f)

# Function to extract tailored solutions for different audiences using Ollama
def get_best_solutions_for_audiences(cve_id, summary, max_retries=3):
    # Prompts for each audience type
    prompts = {
        "junior_tech_support": f"""
        Provide a clear, step-by-step solution for vulnerability {cve_id} that a junior tech support professional, new to technology, can follow.
        Details:
        Solutions: {summary.get('solutions', 'N/A')}
        Mitigations: {summary.get('mitigations', 'N/A')}
        Technical Insights: {summary.get('technical_insights', 'N/A')}
        Affected Versions: {summary.get('affected_versions', 'N/A')}
        """,
        "c_suite": f"""
        Describe the best approach to addressing vulnerability {cve_id} in a manner understandable to a CEO or C-suite executive, without technical jargon.
        Details:
        Solutions: {summary.get('solutions', 'N/A')}
        Mitigations: {summary.get('mitigations', 'N/A')}
        Technical Insights: {summary.get('technical_insights', 'N/A')}
        Affected Versions: {summary.get('affected_versions', 'N/A')}
        """,
        "cto": f"""
        Provide an advanced solution to vulnerability {cve_id} suitable for a CTO with over 20 years of experience, covering the detailed technical solution.
        Details:
        Solutions: {summary.get('solutions', 'N/A')}
        Mitigations: {summary.get('mitigations', 'N/A')}
        Technical Insights: {summary.get('technical_insights', 'N/A')}
        Affected Versions: {summary.get('affected_versions', 'N/A')}
        """
    }
    
    solutions = {}
    for audience, prompt in prompts.items():
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "http://localhost:11434/api/chat",
                    json={
                        "model": "llama3.1:8b",
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "stream": False
                    }
                )
                response.raise_for_status()
                response_data = response.json()
                solutions[audience] = response_data.get("message", {}).get("content", "").strip() or \
                                      "Error: No completion found in response."
                break  # Exit retry loop on success
            except requests.RequestException as e:
                print(f"Attempt {attempt + 1} failed for {cve_id} ({audience}): {e}")
                if attempt < max_retries - 1:
                    sleep(2)
                else:
                    solutions[audience] = f"Error while processing {cve_id} for {audience}: {str(e)}"

    return solutions

# Iterate through CVEs and generate audience-specific solutions
final_solutions = {}
for cve_id, summary in cve_summary_data.items():
    solutions_for_audiences = get_best_solutions_for_audiences(cve_id, summary)
    final_solutions[cve_id] = {
        "solutions_for_audiences": solutions_for_audiences,
        "original_summary": summary
    }

# Save the final summarized best solutions
with open("final_cve_solutions_audience_specific.json", "w", encoding="utf-8") as f:
    json.dump(final_solutions, f, indent=2)

print("Audience-specific best solutions generated and saved to final_cve_solutions_audience_specific.json.")
