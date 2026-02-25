import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from googlesearch import search
import time

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
    except Exception:
        return ""
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

    keywords = ["requirement", "eligibility", "admission", "career", "job", "placement"]

    for key, q in queries.items():
        try:
            results = list(search(q, num_results=3))
        except:
            results = []

        combined_text = ""
        for url in results:
            combined_text += fetch_page_text(url) + "\n"
            time.sleep(1)  # avoid rate limiting

        found = find_key_sentences(combined_text, keywords)
        info[key] = "\n".join(found[:8])

    return info


# ----------------------------------
# Top Universities (Sample List)
# ----------------------------------
top_unis = [
    "Massachusetts Institute of Technology",
    "Stanford University",
    "University of Oxford",
    "Harvard University",
    "California Institute of Technology",
    "University of Cambridge",
    "ETH Zurich",
    "National University of Singapore",
    "UCL",
    "Imperial College London"
]

# ----------------------------------
# Streamlit UI
# ----------------------------------
st.set_page_config(page_title="University Research Tool", layout="wide")

st.title("🌍 Undergraduate Degree University Research Tool")
st.write("Search top universities and gather admission + career information.")

degree = st.text_input("Enter Undergraduate Degree (e.g., Computer Science BSc)")
num_unis = st.slider("Number of universities to search", 1, len(top_unis), 5)

if st.button("Start Research"):
    if degree.strip() == "":
        st.warning("Please enter a degree name.")
    else:
        st.info("Researching universities... This may take a few minutes.")
        
        records = []
        progress = st.progress(0)

        selected_unis = top_unis[:num_unis]

        for i, uni in enumerate(selected_unis):
            st.write(f"Processing {uni}...")
            info = search_university_info(degree, uni)
            records.append({
                "University": uni,
                "Prerequisites": info["prerequisites"],
                "Admission Criteria": info["admission_criteria"],
                "Career Outcomes": info["career_outcomes"]
            })
            progress.progress((i + 1) / num_unis)

        df = pd.DataFrame(records)

        st.success("Research Complete!")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV",
            csv,
            "universities_info.csv",
            "text/csv"
        )
