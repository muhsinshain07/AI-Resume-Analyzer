import json
import os
from typing import Any, Dict

from groq import Groq

class AnalysisError(Exception):
    """Raised when the AI analysis cannot be completed or validated."""

REQUIRED_KEYS = {
    "overall_match_score", "score_breakdown", "matching_skills", "missing_skills",
    "ats_keywords", "problems", "recommendations", "final_result"
}

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "overall_match_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "score_breakdown": {"type": "object", "additionalProperties": False, "properties": {
            "required_skills": {"type": "integer", "minimum": 0, "maximum": 100},
            "relevant_experience": {"type": "integer", "minimum": 0, "maximum": 100},
            "responsibilities": {"type": "integer", "minimum": 0, "maximum": 100},
            "ats_coverage": {"type": "integer", "minimum": 0, "maximum": 100},
            "education_certifications": {"type": "integer", "minimum": 0, "maximum": 100}
        }, "required": ["required_skills", "relevant_experience", "responsibilities", "ats_coverage", "education_certifications"]},
        "matching_skills": {"type": "array", "items": {"type": "string"}},
        "missing_skills": {"type": "array", "items": {"type": "string"}},
        "ats_keywords": {"type": "array", "items": {"type": "string"}},
        "problems": {"type": "array", "items": {"type": "string"}},
        "recommendations": {"type": "array", "items": {"type": "string"}},
        "final_result": {"type": "string"}
    },
    "required": list(REQUIRED_KEYS)
}

SYSTEM_PROMPT = """You are a careful resume-to-job-description analyst. Compare only the supplied documents. Never invent experience, skills, education, or certifications. Treat a skill as matching only when the resume explicitly states it or provides strong evidence of it. Return only valid JSON matching the supplied schema. The score is an estimate for this specific job, not an interview guarantee. Recommendations must be actionable and must not tell the user to claim skills they do not have."""

def _client() -> Groq:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise AnalysisError("GROQ_API_KEY is missing. Copy .env.example to .env and add your Groq API key.")
    return Groq(api_key=key)

def _extract_json(content: str) -> Dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AnalysisError("The model returned invalid JSON. Please try again.") from exc
    if set(data) != REQUIRED_KEYS:
        raise AnalysisError("The model returned an incomplete analysis.")
    return data

def analyze_resume(resume_text: str, job_description: str) -> Dict[str, Any]:
    if not resume_text.strip():
        raise ValueError("The resume contains no readable text.")
    if not job_description.strip():
        raise ValueError("Job description cannot be empty.")
    prompt = f"""Analyze the following resume against the job description.

RESUME:
{resume_text[:30000]}

JOB DESCRIPTION:
{job_description[:30000]}

Use this JSON schema exactly:
{json.dumps(SCHEMA)}"""
    try:
        response = _client().chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=0.1,
            max_tokens=4000,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
        )
    except Exception as exc:
        raise AnalysisError(f"Groq request failed: {exc}") from exc
    return _extract_json(response.choices[0].message.content)
