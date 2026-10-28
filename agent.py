import os
import requests
from dotenv import load_dotenv
from fpdf import FPDF
from groq import Groq

# Φόρτωση του API Token
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class ResearchAgent:
    def __init__(self, name="Agent-Alpha"):
        self.name = name
        self.headers = {
            "User-Agent": "StudentResearchAgentApp/1.0 (contact_student@example.org)"
        }
        
        if GROQ_API_KEY:
            self.llm_client = Groq(api_key=GROQ_API_KEY)
            print(f"🤖 {self.name} initialized with LLM Brain (Qwen via Groq)!")
        else:
            self.llm_client = None
            print(f"🤖 {self.name} initialized without LLM (Missing GROQ_API_KEY)")

    def clean_text(self, text):
        if not text:
            return ""
        replacements = {
            "—": " - ", "–": " - ", "“": '"', "”": '"',
            "’": "'", "‘": "'"
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text.encode('latin-1', 'ignore').decode('latin-1')

    def fetch_wikipedia_data(self, topic):
        clean_topic = topic.replace("_", " ").strip()
        print(f"\n📚 [Source 1/2] Fetching Wikipedia overview for '{clean_topic}'...")
        
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{clean_topic}"
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                image_url = data.get("thumbnail", {}).get("source", "")
                return {
                    "title": data.get("title", clean_topic),
                    "summary": data.get("extract", "No summary available."),
                    "image_url": image_url
                }
        except Exception as e:
            print(f"⚠️ Primary Wikipedia API failed: {e}")

        print("🔄 Trying alternative Wikipedia query method...")
        fallback_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query", "format": "json", "prop": "extracts",
            "exintro": True, "explaintext": True, "titles": clean_topic, "redirects": 1
        }
        try:
            res = requests.get(fallback_url, headers=self.headers, params=params, timeout=5)
            pages = res.json().get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if page_id != "-1":
                    return {
                        "title": page_data.get("title", clean_topic),
                        "summary": page_data.get("extract", "No summary available.")[:1000],
                        "image_url": ""
                    }
        except Exception as e:
            print(f"⚠️ Fallback Wikipedia API failed: {e}")

        return None

    def analyze_with_llm(self, topic, raw_summary):
        if not self.llm_client:
            return raw_summary

        print(f"🧠 [LLM Processing] Conducting deep technical analysis...")
        
        # Ζητάμε συνδυασμό παραγράφων ΚΑΙ bullets, με αυστηρή αρίθμηση στις ενότητες.
        system_instructions = (
            "You are a Lead AI Research Analyst. Transform raw text into a detailed executive report. "
            "CRITICAL: Do NOT use Markdown (no asterisks **, no hashes ###). "
            "Use a mix of descriptive paragraphs and bullet points (using simple dashes '-') for lists. "
            "You MUST start the three main sections exactly with '1. ', '2. ', and '3. ' so the parser can catch them."
        )
        
        user_prompt = f"""Analyze the following text about '{topic}':\n\n{raw_summary}\n\nProvide a structured breakdown with:
1. Core Concept & Mechanism
2. Real-World Applications & Importance
3. Key Technical Challenges & Limitations"""

        try:
            response = self.llm_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": user_prompt}
                ],
                model="qwen/qwen3.8-27b",
                max_tokens=600,
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ LLM Error: {e}. Falling back to raw summary.")
            return raw_summary

    def create_pdf_report(self, title, summary, image_url, filename="research_report.pdf"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        page_width = pdf.epw 

        # 1. Κεντρικός Τίτλος
        pdf.set_font("Helvetica", style="B", size=18)
        pdf.cell(page_width, 10, f"AI Research Report: {self.clean_text(title)}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(5)
        
        # 2. Ενσωμάτωση Εικόνας (πιο κομψό μέγεθος)
        if image_url:
            if image_url.endswith('.svg'):
                print("⚠️ Skipping image: SVG format is not supported by FPDF.")
            else:
                try:
                    img_response = requests.get(image_url, headers=self.headers)
                    if img_response.status_code == 200:
                        with open("temp_image.jpg", "wb") as f:
                            f.write(img_response.content)
                        
                        # Μικρύναμε το πλάτος (w=60) για να μην είναι τεράστια
                        pdf.image("temp_image.jpg", x=(210 - 60) / 2, w=60)
                        pdf.ln(5) 
                        os.remove("temp_image.jpg")
                except Exception as e:
                    print(f"⚠️ Could not load image into PDF: {e}")

        # 3. Έξυπνη Μορφοποίηση Κειμένου
        clean_sum = self.clean_text(summary).replace("**", "").replace("###", "")
        lines = clean_sum.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Υπότιτλοι (1., 2., 3.)
            if line.startswith(("1.", "2.", "3.", "4.")):
                pdf.set_font("Helvetica", style="B", size=13)
                pdf.ln(4)
                pdf.multi_cell(page_width, 8, line)
                pdf.ln(1)
            # Bullets (-)
            elif line.startswith("-"):
                pdf.set_font("Helvetica", size=10)
                # Προσθέτουμε 4 κενά (εσοχή) για να ξεχωρίζουν όμορφα
                pdf.multi_cell(page_width, 6, "    " + line)
                pdf.ln(1)
            # Κανονικό κείμενο (Παράγραφοι)
            else:
                pdf.set_font("Helvetica", size=10)
                pdf.multi_cell(page_width, 6, line)
                pdf.ln(2)

        # 4. Υπογραφή (Footer στο τέλος)
        pdf.ln(10)
        pdf.set_font("Helvetica", style="I", size=9)
        pdf.cell(page_width, 6, "Report generated automatically by Agent-Alpha", align="C")

        pdf.output(filename)
        print(f"📄 PDF report created successfully: '{filename}'!")

if __name__ == "__main__":
    agent = ResearchAgent("Agent-Alpha")
    user_topic = input("\n👉 Enter a research topic (e.g., Quantum computing, Black hole): ").strip()
    
    if user_topic:
        wiki_data = agent.fetch_wikipedia_data(user_topic)
        if wiki_data:
            llm_analysis = agent.analyze_with_llm(wiki_data['title'], wiki_data['summary'])
            agent.create_pdf_report(wiki_data['title'], llm_analysis, wiki_data['image_url'])
        else:
            print("❌ Research failed: Could not find data for this topic.")