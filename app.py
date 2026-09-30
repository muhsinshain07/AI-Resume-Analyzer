import streamlit as st
from analyzer import AnalysisError, analyze_resume
from resume_parser import ResumeParseError, extract_resume_text

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")
st.title("📄 AI Resume Analyzer")
st.caption("Compare a resume with a job description using structured AI analysis.")

with st.sidebar:
    st.header("Instructions")
    st.write("Upload a PDF or DOCX resume, paste the complete job description, then click Analyze.")
    st.info("Do not add skills to your resume unless you genuinely have them.")

resume_file = st.file_uploader("Upload resume", type=["pdf", "docx"])
job_description = st.text_area("Paste job description", height=300, placeholder="Paste the complete job description here...")

if st.button("Analyze resume", type="primary", disabled=not resume_file or not job_description.strip()):
    try:
        with st.spinner("Extracting resume and generating analysis..."):
            resume_text = extract_resume_text(resume_file.name, resume_file.getvalue())
            result = analyze_resume(resume_text, job_description.strip())
        st.session_state["analysis"] = result
    except (ResumeParseError, AnalysisError, ValueError) as exc:
        st.error(str(exc))
    except Exception:
        st.error("Unexpected error. Check your configuration and try again.")

result = st.session_state.get("analysis")
if result:
    st.divider()
    score = result["overall_match_score"]
    st.metric("Overall match score", f"{score}/100")
    st.write(result["final_result"])

    left, right = st.columns(2)
    with left:
        st.subheader("Matching skills")
        st.write(result["matching_skills"] or ["None identified"])
        st.subheader("Missing skills")
        st.write(result["missing_skills"] or ["None identified"])
        st.subheader("ATS keywords")
        st.write(result["ats_keywords"] or ["None identified"])
    with right:
        st.subheader("Problems")
        st.write(result["problems"] or ["None identified"])
        st.subheader("Recommendations")
        for index, recommendation in enumerate(result["recommendations"], 1):
            st.write(f"{index}. {recommendation}")

    with st.expander("Structured JSON"):
        st.json(result)
