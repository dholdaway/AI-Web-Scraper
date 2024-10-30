curl -X POST http://127.0.0.1:5000/crawl -H "Content-Type: application/json" -d '{"cve_id": "CVE-2024-51304"}'  
scrapy runspider cve_spider.py -a cve_folder=./cve_results/CVE-2024-51304 -a max_depth=2  

update parser_script.py

if __name__ == "__main__":
    cve_id = "CVE-2024-51304"  # Example CVE ID
    parse_description = "solutions, mitigations, and technical insights"
    process_cve_content(cve_id, parse_description)

python parser_script.py

python cve_summary_parser.py  

python CveSummaryOllamaAnalysis.py  