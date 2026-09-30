# AI Resume Analyzer

A modular Streamlit app that extracts text from PDF/DOCX resumes and compares it with a job description using the Groq API. It returns validated, structured JSON containing a match score, score breakdown, matching skills, missing skills, ATS keywords, problems, recommendations, and a final result.

## Requirements

- Python 3.10 or newer
- A Groq API key
- A resume in PDF or DOCX format

## Setup

1. Create and enter a project directory.
2. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate it:

   Windows PowerShell:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   macOS/Linux:

   ```bash
   source .venv/bin/activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Copy `.env.example` to `.env` and add your Groq key:

   Windows PowerShell:

   ```powershell
   Copy-Item .env.example .env
   ```

   macOS/Linux:

   ```bash
   cp .env.example .env
   ```

6. Export environment variables before running. Streamlit does not automatically load `.env` in every setup, so use one of these options:

   Windows PowerShell:

   ```powershell
   $env:GROQ_API_KEY="your_key_here"
   $env:GROQ_MODEL="llama-3.3-70b-versatile"
   ```

   macOS/Linux:

   ```bash
   export GROQ_API_KEY="your_key_here"
   export GROQ_MODEL="llama-3.3-70b-versatile"
   ```

   Alternatively, add `load_dotenv()` near the imports in `analyzer.py` and call it before reading the key.

## Run

```bash
streamlit run app.py
```

Open the local URL shown by Streamlit, upload a PDF/DOCX resume, paste a job description, and click **Analyze resume**.

## Architecture

- `app.py`: UI, input handling, and result presentation.
- `resume_parser.py`: PDF/DOCX text extraction only.
- `analyzer.py`: Groq request, prompt, JSON schema, and response validation.
- `requirements.txt`: Python dependencies.
- `.env.example`: configuration template.
- `.gitignore`: files that should not be committed.

The app follows separation of concerns: parsing, analysis, and presentation are independently replaceable. The current parser handles text-based PDFs; image-only scanned PDFs require an OCR component in a later version.

## Security notes

- Never commit `.env` or expose your API key in frontend code.
- Resume contents are sent to Groq for analysis; tell users how their data is handled.
- Add authentication, rate limiting, file-size limits, deletion policies, and audit logging before production deployment.
- Review AI output before relying on it for employment decisions.
