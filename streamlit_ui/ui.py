import streamlit as st
import requests
from pathlib import Path
import tempfile

API_URL = "http://localhost:8000/resume/parse"

st.set_page_config(
    page_title="Resume Parser",
    layout="wide",
)

st.title("📄 Resume Parser")
st.write("Upload a resume PDF to extract structured candidate information.")

uploaded_file = st.file_uploader(
    "Upload Resume (PDF only)",
    type=["pdf"],
)

if uploaded_file:
    st.success(f"Uploaded: {uploaded_file.name}")

    if st.button("Parse Resume"):
        with st.spinner("Parsing resume..."):
            with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp.flush()

                files = {
                    "file": (
                        uploaded_file.name,
                        open(tmp.name, "rb"),
                        "application/pdf",
                    )
                }

                response = requests.post(API_URL, files=files)

        if response.status_code != 200:
            st.error(response.json().get("detail", "Parsing failed"))
        else:
            resume = response.json()
            st.success("Resume parsed successfully!")

            # =====================
            # HEADER
            # =====================
            st.header(resume.get("full_name", "Unknown Candidate"))
            cols = st.columns(4)

            cols[0].metric("Experience (yrs)", resume.get("years_of_experience", "N/A"))
            
            cols[1].markdown(
                f"**Current Role:**<br>{resume.get('current_job_title', 'N/A')}",
                unsafe_allow_html=True,
            )
            
            cols[2].markdown(
                f"**Location:**<br>{resume.get('location', 'N/A')}",
                unsafe_allow_html=True,
            )
            
            cols[3].markdown(
                f"**Email:**<br>{resume.get('email', 'N/A')}",
                unsafe_allow_html=True,
            )


            # =====================
            # SUMMARY
            # =====================
            if resume.get("summary"):
                st.subheader("Professional Summary")
                st.write(resume["summary"])

            # =====================
            # EXPERIENCE
            # =====================
            st.subheader("Work Experience")
            for exp in resume.get("work_experience", []):
                with st.expander(f"{exp['job_title']} @ {exp['company']}"):
                    st.write(f"📍 {exp.get('location', 'N/A')}")
                    st.write(f"🗓 {exp.get('start_date')} → {exp.get('end_date')}")
                    for r in exp.get("responsibilities", []):
                        st.markdown(f"- {r}")

            # =====================
            # SKILLS
            # =====================
            st.subheader("Skills")
            skills = resume.get("skills", [])
            st.write(", ".join([s["name"] for s in skills]))

            # =====================
            # EDUCATION
            # =====================
            st.subheader("Education")
            for edu in resume.get("education", []):
                st.write(
                    f"🎓 {edu['degree']} - {edu['institution']} "
                    f"({edu.get('graduation_year', 'N/A')})"
                )

            # =====================
            # CERTIFICATIONS
            # =====================
            if resume.get("certifications"):
                st.subheader("Certifications")
                for cert in resume["certifications"]:
                    st.write(f"📜 {cert['name']}")

            # =====================
            # DOWNLOAD
            # =====================
            st.download_button(
                "⬇ Download JSON",
                data=response.text,
                file_name="parsed_resume.json",
                mime="application/json",
            )
