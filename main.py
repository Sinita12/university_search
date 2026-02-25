import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# ----------------------------------
# Page Config
# ----------------------------------
st.set_page_config(page_title="University Research Tool", layout="wide")

# ----------------------------------
# Official Admissions Pages
# ----------------------------------
official_pages = {
    "Massachusetts Institute of Technology":
        "https://mitadmissions.org/apply/process/",
    "Stanford University":
        "https://admission.stanford.edu/apply/",
    "University of Oxford":
        "https://www.ox.ac.uk/admissions/undergraduate",
    "Harvard University":
        "https://college.harvard.edu/admissions/apply",
    "California Institute of Technology":
        "https://www.admissions.caltech.edu/apply",
    "University of Cambridge":
        "https://www.undergraduate.study.cam.ac.uk/applying",
    "ETH Zurich":
        "https://ethz.ch/en/studies/bachelor/application.html",
    "National University of Singapore":
        "https://nus.edu.sg/oam/apply-to-nus",
    "UCL":
        "https://www.ucl.ac.uk/prospective-students/undergraduate/apply",
    "Imperial College London":
        "https://www.imperial.ac.uk/study/apply/undergraduate/"
}

top_unis = list(official_pages.keys())

# ----------------------------------
# Helper Functions
# ----------------------------------
def fetch_page_text(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            return soup.get_text(separator="\n")
    except Exception:
        return ""
    return ""


def find_key_sentences(text, keywords):
    lines = text.split("\n")
    found = []
    for line in lines:
        for kw in keywords:
            if kw.lower() in line.lower():
                cleaned = line.strip()
                if len(cleaned) > 40:  # avoid very short junk lines
                    found.append(cleaned)
                break
    return found


def search_university_info(degree_name, uni_name):
    info = {
        "prerequisites": "",
        "admission_criteria": "",
        "career_outcomes": ""
    }

    url = official_pages.get(uni_name)

    if not url:
        return info

    page_text = fetch_page_text(url)

    if page_text == "":
        return info

    prereq_keywords = ["requirement", "eligibility", "qualification", "subjects"]
    admission_keywords = ["admission", "selection", "criteria", "apply", "application"]
    career_keywords = ["career", "employment", "job", "graduate", "placement"]

    info["prerequisites"] = "\n".join(
        find_key_sentences(page_text, prereq_keywords)[:6]
    )

    info["admission_criteria"] = "\n".join(
        find_key_sentences(page_text, admission_keywords)[:6]
    )

    info["career_outcomes"] = "\n".join(
        find_key_sentences(page_text, career_keywords)[:6]
    )

    return info


# ----------------------------------
# Streamlit UI
# ----------------------------------
st.title("🌍 Undergraduate Degree University Research Tool")
st.write("Gather official undergraduate admission information directly from university websites.")

degree = st.text_input("Enter Undergraduate Degree (e.g., Computer Science BSc)")
num_unis = st.slider("Number of universities to search", 1, len(top_unis), 5)

if st.button("Start Research"):

    if degree.strip() == "":
        st.warning("Please enter a degree name.")
        st.stop()

    st.info("Researching official university pages...")

    records = []
    progress = st.progress(0)

    selected_unis = top_unis[:num_unis]

    for i, uni in enumerate(selected_unis):
        st.write(f"Processing {uni}...")

        info = search_university_info(degree, uni)

        records.append({
            "University": uni,
            "Prerequisites": info["prerequisites"] if info["prerequisites"] else "Not found on main admissions page.",
            "Admission Criteria": info["admission_criteria"] if info["admission_criteria"] else "Not found on main admissions page.",
            "Career Outcomes": info["career_outcomes"] if info["career_outcomes"] else "Not typically listed on admissions page."
        })

        progress.progress((i + 1) / num_unis)

    df = pd.DataFrame(records)

    st.success("Research Complete!")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="universities_info.csv",
        mime="text/csv"
    )
