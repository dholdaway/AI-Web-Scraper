import json
import requests

# Load the CVE summary report generated earlier
with open("cve_summary_report.json", "r", encoding="utf-8") as f:
    cve_summary_data = json.load(f)

# Function to extract best solution for each CVE using Ollama
def get_best_solution(cve_id, summary):
    prompt = f"""
    The following is a summarized report of vulnerability {cve_id} including solutions, mitigations, technical insights, and affected versions:
    
    Solutions: {summary.get('solutions', 'N/A')}
    Mitigations: {summary.get('mitigations', 'N/A')}
    Technical Insights: {summary.get('technical_insights', 'N/A')}
    Affected Versions: {summary.get('affected_versions', 'N/A')}
    
    Based on the provided information, give the best solution to resolve the vulnerability in a clear and concise manner.
    """
    
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
        response_data = response.json()
        return response_data.get("message", {}).get("content", "Error: No completion found in response.").strip()
    except Exception as e:
        return f"Error while processing {cve_id}: {str(e)}"

# Iterate through CVEs and generate the best solution
final_solutions = {}
for cve_id, summary in cve_summary_data.items():
    best_solution = get_best_solution(cve_id, summary)
    final_solutions[cve_id] = {
        "best_solution": best_solution,
        "original_summary": summary
    }

# Save the final summarized best solutions
with open("final_cve_solutions.json", "w", encoding="utf-8") as f:
    json.dump(final_solutions, f, indent=2)

print("Final best solutions generated and saved to final_cve_solutions.json.")
