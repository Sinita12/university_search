import requests
from bs4 import BeautifulSoup
import pandas as pd
from googlesearch import search

# ----------------------------------
# Helper Functions
# ----------------------------------
def fetch_page_text(url):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            texts = soup.get_text(separator="\n")
            return texts
    except Exception as e:
        print("Error fetching:", e)
    return ""

def find_key_sentences(text, keywords):
    lines = text.split("\n")
    found = []
    for line in lines:
        for kw in keywords:
            if kw.lower() in line.lower():
                found.append(line.strip())
                break
    return found

# ----------------------------------
# Main Scraping Logic
# ----------------------------------
def search_university_info(degree_name, uni_name):
    info = {
        "prerequisites": "",
        "admission_criteria": "",
        "career_outcomes": ""
    }

    queries = {
        "prerequisites": f"{uni_name} {degree_name} prerequisites",
        "admission_criteria": f"{uni_name} {degree_name} admission requirements what they look for",
        "career_outcomes": f"{uni_name} {degree_name} career outcomes jobs after degree"
    }

    for key, q in queries.items():
        print(f"Searching: {q}")
        results = list(search(q, num_results=5))
        
        combined_text = ""
        for url in results:
            txt = fetch_page_text(url)
            combined_text += txt + "\n"
        
        # Extract lines with key words
        keywords = ["requirement", "must have", "admission", "career", "job"]
        found = find_key_sentences(combined_text, keywords)
        info[key] = "\n".join(found[:10])  # take first 10 matching lines

    return info

# ----------------------------------
# Top Universities (hardcoded sample)
# ----------------------------------
top_unis = [
    "Massachusetts Institute of Technology",
    "Stanford University",
    "University of Oxford",
    "Harvard University",
    "California Institute of Technology"
    # You would need a real API or CSV for the actual top 25
]

# Enter the degree
degree = input("Enter undergraduate degree (e.g., Computer Science BSc): ")

records = []
for uni in top_unis:
    print("Processing", uni)
    info = search_university_info(degree, uni)
    records.append({
        "University": uni,
        "Prerequisites": info["prerequisites"],
        "Admission Criteria": info["admission_criteria"],
        "Career Outcomes": info["career_outcomes"]
    })

df = pd.DataFrame(records)
df.to_csv("universities_info.csv", index=False)
print("Saved as universities_info.csv")
