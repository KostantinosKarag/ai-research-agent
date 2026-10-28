import requests

class ResearchAgent:
    def __init__(self, name="Agent-Alpha"):
        # Ορίζουμε το όνομα του Agent
        self.name = name
        # Τα headers χρειάζονται για να μας επιτρέψει η Wikipedia να πάρουμε δεδομένα
        self.headers = {
            "User-Agent": "MyAIResearchAgent/1.0 (contact@example.com)"
        }
        print(f"🤖 {self.name} initialized and ready for research!")

    def search_topic(self, topic):
        """
        Εργαλείο 1: Αναζήτηση στη Wikipedia
        """
        print(f"\n🔍 Agent is researching topic: '{topic}'...")
        
        # Κατασκευάζουμε το URL για το API της Wikipedia με βάση το θέμα
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
        
        try:
            # Στέλνουμε το αίτημα στο ίντερνετ (HTTP GET request)
            response = requests.get(url, headers=self.headers)
            
            # Αν το θέμα δεν υπάρχει στη Wikipedia (σφάλμα 404)
            if response.status_code == 404:
                print(f"❌ Article for '{topic}' not found.")
                return None
                
            # Μετατρέπουμε την απάντηση από τη Wikipedia σε μορφή λεξικού (JSON -> Python dict)
            data = response.json()
            
            # Επιστρέφουμε τα στοιχεία που μας ενδιαφέρουν
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
        Εργαλείο 2: Δημιουργία αρχείου Markdown
        """
        if not research_data:
            print("❌ Cannot generate report. No research data available.")
            return

        # Φτιάχνουμε το κείμενο του Report
        report_content = f"""# 📑 Research Report: {research_data['title']}

*Generated automatically by {self.name}*

---

## 📌 Executive Summary
{research_data['summary']}

---

## 🔗 Source & References
- [Read full article on Wikipedia]({research_data['url']})
"""

        # Ανοίγουμε/Δημιουργούμε το αρχείο και γράφουμε το κείμενο μέσα
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"✅ Report successfully saved to '{filename}'!")

if __name__ == "__main__":
    agent = ResearchAgent("Agent-Alpha")
    
    # 🌟 ΝΕΑ ΔΥΝΑΤΟΤΗΤΑ: Ο χρήστης πληκτρολογεί όποιο θέμα θέλει!
    user_topic = input("\n👉 Enter a research topic (e.g., Quantum_computing, Artificial_intelligence, Apple_Inc): ").strip()
    
    if user_topic:
        # 1. Εκτέλεση εργαλείου αναζήτησης
        data = agent.search_topic(user_topic)
        
        if data:
            print("\n--- Research Results ---")
            print(f"Title: {data['title']}")
            print(f"\nSummary:\n{data['summary']}\n")
            
            # 2. Εκτέλεση εργαλείου δημιουργίας report
            agent.create_markdown_report(data)