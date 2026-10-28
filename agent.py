import requests
from fpdf import FPDF

class ResearchAgent:
    def __init__(self, name="Agent-Alpha"):
        self.name = name
        self.headers = {
            "User-Agent": "MyAIResearchAgent/1.0 (contact@example.com)"
        }
        print(f"🤖 {self.name} initialized and ready for research!")

    def clean_text(self, text):
        """
        Καθαρίζει ειδικούς χαρακτήρες (παύλες, εισαγωγικά, αλλαγές γραμμών)
        ώστε να εμφανίζονται σωστά στο PDF χωρίς '?' ή παράξενα σπασίματα.
        """
        if not text:
            return ""
        
        replacements = {
            "—": " - ",
            "–": " - ",
            "“": '"',
            "”": '"',
            "’": "'",
            "‘": "'",
            "\n": " "
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        return text.encode('latin-1', 'ignore').decode('latin-1')

    def fetch_wikipedia_data(self, topic):
        clean_topic = topic.replace("_", " ").strip()
        print(f"\n📚 [Source 1/2] Fetching Wikipedia overview for '{clean_topic}'...")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{clean_topic}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            
            return {
                "title": data.get("title", clean_topic),
                "summary": data.get("extract", "No summary available."),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
            }
        except Exception as e:
            print(f"⚠️ Wikipedia search error: {e}")
            return None

    def fetch_news_data(self, topic):
        clean_topic = topic.replace("_", " ").strip()
        print(f"📰 [Source 2/2] Fetching related web topics for '{clean_topic}'...")
        url = f"https://api.duckduckgo.com/?q={clean_topic}&format=json"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            related_topics = []
            for item in data.get("RelatedTopics", []):
                if "Text" in item and len(related_topics) < 3:
                    related_topics.append(item["Text"])
                    
            return related_topics
        except Exception as e:
            print(f"⚠️ News search error: {e}")
            return []

    def create_markdown_report(self, title, summary, url, related_topics, filename="research_report.md"):
        report_content = f"""# Research Report: {title}

---

## Executive Summary
{summary}

---

## Related Key Insights
"""
        if related_topics:
            for item in related_topics:
                report_content += f"- {item}\n"
        else:
            report_content += "No additional web insights found.\n"

        report_content += f"\n---\n\n## References\n- [Read full article on Wikipedia]({url})\n"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"✅ Markdown report saved to '{filename}'!")

    def create_pdf_report(self, title, summary, related_topics, filename="research_report.pdf"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Χρήση pdf.epw (Effective Page Width) για να μην υπάρχει ποτέ σφάλμα χώρου
        page_width = pdf.epw 

        # Τίτλος (Helvetica Sans-Serif όπως η Wikipedia)
        pdf.set_font("Helvetica", style="B", size=16)
        pdf.cell(page_width, 10, f"Research Report: {self.clean_text(title)}", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.ln(5)

        # 1. Executive Summary
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.cell(page_width, 8, "1. Executive Summary", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        
        pdf.set_font("Helvetica", size=10)
        clean_sum = self.clean_text(summary)
        pdf.multi_cell(page_width, 6, clean_sum)
        pdf.ln(6)

        # 2. Related Key Insights
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.cell(page_width, 8, "2. Related Key Insights", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        
        pdf.set_font("Helvetica", size=10)
        if related_topics:
            for item in related_topics:
                clean_item = self.clean_text(item)
                pdf.multi_cell(page_width, 6, f"- {clean_item}")
                pdf.ln(2)
        else:
            pdf.multi_cell(page_width, 6, "No additional web insights found.")

        pdf.output(filename)
        print(f"📄 PDF report successfully created: '{filename}'!")

if __name__ == "__main__":
    agent = ResearchAgent("Agent-Alpha")
    
    user_topic = input("\n👉 Enter a research topic (e.g., Global warming, Artificial intelligence, Apple Inc): ").strip()
    
    if user_topic:
        wiki_data = agent.fetch_wikipedia_data(user_topic)
        news_data = agent.fetch_news_data(user_topic)
        
        if wiki_data:
            agent.create_markdown_report(
                title=wiki_data['title'],
                summary=wiki_data['summary'],
                url=wiki_data['url'],
                related_topics=news_data
            )
            
            agent.create_pdf_report(
                title=wiki_data['title'],
                summary=wiki_data['summary'],
                related_topics=news_data
            )
        else:
            print("❌ Research failed: Could not find sufficient data for this topic.")