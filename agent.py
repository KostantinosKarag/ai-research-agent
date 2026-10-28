import requests

class ResearchAgent:
    def __init__(self, name="Agent-Alpha"):
        self.name = name
        # Headers απαραίτητα για το Wikipedia API
        self.headers = {
            "User-Agent": "MyAIResearchAgent/1.0 (contact@example.com)"
        }
        print(f"🤖 {self.name} initialized and ready for research!")

    def search_topic(self, topic):
        """
        Εργαλείο 1: Αναζήτηση και λήψη περίληψης από το REST API της Wikipedia
        """
        print(f"\n🔍 Agent is researching topic: '{topic}'...")
        
        # URL για το REST API της Wikipedia
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_status_code == 404 if hasattr(response, 'status_status_code') else response.status_code == 404:
                print(f"❌ Article for '{topic}' not found.")
                return None
                
            response.raise_for_status()
            data = response.json()
            
            research_data = {
                "title": data.get("title", topic),
                "summary": data.get("extract", "No summary available."),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{topic}")
            }
            return research_data

        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return None

    def create_markdown_report(self, research_data, filename="research_report.md"):
        """
        Εργαλείο 2: Αυτόματη δημιουργία Markdown Report
        """
        if not research_data:
            print("❌ Cannot generate report. No research data available.")
            return

        report_content = f"""# 📑 Research Report: {research_data['title']}

*Generated automatically by {self.name}*

---

## 📌 Executive Summary
{research_data['summary']}

---

## 🔗 Source & References
- [Read full article on Wikipedia]({research_data['url']})
"""

        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"✅ Report successfully saved to '{filename}'!")

if __name__ == "__main__":
    agent = ResearchAgent("Agent-Alpha")
    
    # Θέμα έρευνας
    topic = "Nvidia"
    
    # 1. Αναζήτηση
    data = agent.search_topic(topic)
    
    if data:
        print("\n--- Research Results ---")
        print(f"Title: {data['title']}")
        print(f"\nSummary:\n{data['summary']}\n")
        
        # 2. Δημιουργία Report
        agent.create_markdown_report(data)