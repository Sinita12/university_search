import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="UK CS & Maths Research Tool", layout="wide")

# ----------------------------------
# Hardcoded Official Course Pages
# ----------------------------------

course_pages = {
    "Computer Science": {
        "University of Oxford":
            "https://www.ox.ac.uk/admissions/undergraduate/courses/course-listing/computer-science",
        "University of Cambridge":
            "https://www.undergraduate.study.cam.ac.uk/courses/computer-science",
        "Imperial College London":
            "https://www.imperial.ac.uk/study/courses/undergraduate/computing-beng/",
        "UCL":
            "https://www.ucl.ac.uk/prospective-students/undergraduate/degrees/computer-science-bsc",
        "University of Edinburgh":
            "https://www.ed.ac.uk/studying/undergraduate/degrees/index.php?action=view&code=G400",
        "King's College London":
            "https://www.kcl.ac.uk/study/undergraduate/courses/computer-science-bsc"
    },
    "Mathematics": {
        "University of Oxford":
            "https://www.ox.ac.uk/admissions/undergraduate/courses/course-listing/mathematics",
        "University of Cambridge":
            "https://www.undergraduate.study.cam.ac.uk/courses/mathematics",
        "Imperial College London":
            "https://www.imperial.ac.uk/study/courses/undergraduate/mathematics-bsc/",
        "UCL":
            "https://www.ucl.ac.uk/prospective-students/undergraduate/degrees/mathematics-bsc",
        "University of Edinburgh":
            "https://www.ed.ac.uk/studying/undergraduate/degrees/index.php?action=view&code=G100",
        "King's College London":
            "https://www.kcl.ac.uk/study/undergraduate/courses/mathematics-bsc"
    }
}

# ----------------------------------
# Helper Functions
# ----------------------------------

def fetch_page(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return BeautifulSoup(response.text, "html.parser")
    except:
        return None
    return None


def extract_section(soup, keywords):
    if soup is None:
        return "Could not retrieve information."

    text = soup.get_text(separator="\n")
    lines = text.split("\n")

    results = []
    for line in lines:
        for kw in keywords:
            if kw.lower() in line.lower():
                clean = line.strip()
                if len(clean) > 50:
                    results.append(clean)
                break

    if not results:
        return "Not clearly listed on page."

    return "\n".join(results[:6])


def get_course_info(course, university):
    url = course_pages[course][university]
    soup = fetch_page(url)

    entry_keywords = ["AAA", "A*AA", "A level", "entry requirements", "IB", "requirement"]
    content_keywords = ["course content", "what you will study", "modules", "curriculum"]
    career_keywords = ["career", "graduate", "employment", "job", "destination"]

    return {
        "Entry Requirements": extract_section(soup, entry_keywords),
        "Course Content": extract_section(soup, content_keywords),
        "Career Outcomes": extract_section(soup, career_keywords)
    }


# ----------------------------------
# UI
# ----------------------------------

st.title("🇬🇧 UK Computer Science & Mathematics Research Tool")
st.write("Structured, official course information from leading UK universities.")

course_choice = st.selectbox(
    "Select Course",
    ["Computer Science", "Mathematics"]
)

selected_unis = st.multiselect(
    "Select Universities",
    list(course_pages[course_choice].keys()),
    default=list(course_pages[course_choice].keys())[:3]
)

if st.button("Research Courses"):

    if not selected_unis:
        st.warning("Please select at least one university.")
        st.stop()

    st.info("Gathering official course information...")

    records = []
    progress = st.progress(0)

    for i, uni in enumerate(selected_unis):

        st.write(f"Processing {uni}...")

        info = get_course_info(course_choice, uni)

        records.append({
            "University": uni,
            "Entry Requirements": info["Entry Requirements"],
            "Course Content": info["Course Content"],
            "Career Outcomes": info["Career Outcomes"]
        })

        progress.progress((i + 1) / len(selected_unis))

    df = pd.DataFrame(records)

    st.success("Research Complete.")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"UK_{course_choice}_research.csv",
        mime="text/csv"
    )
