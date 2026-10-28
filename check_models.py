import os
from dotenv import load_dotenv
from groq import Groq

# Φορτώνουμε το κλειδί σου
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ Δεν βρέθηκε το GROQ_API_KEY στο .env")
else:
    client = Groq(api_key=api_key)
    print("✅ Τα μοντέλα που μπορείς να χρησιμοποιήσεις με το κλειδί σου είναι:\n")
    
    # Ζητάμε από το Groq τη λίστα με τα ενεργά μοντέλα του λογαριασμού σου
    models = client.models.list()
    for m in models.data:
        print(f"👉 {m.id}")