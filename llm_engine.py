"""
LLM Engine for ATS Bot
Uses Groq API for fast, free AI-powered analysis
"""

import os
import re
from groq import Groq
from config import Config
from typing import Dict, Optional

class LLMEngine:
    """Groq-powered LLM for resume analysis"""
    
    def __init__(self):
        """Initialize Groq client"""
        api_key = Config.GROQ_API_KEY
        if not api_key:
            raise ValueError("GROQ_API_KEY not configured")
        
        self.client = Groq(api_key=api_key)
        self.model = Config.GROQ_MODEL
    
    def _call_groq(self, prompt: str, max_tokens: int = 2000) -> str:
        """Call Groq API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2
            )
            content = response.choices[0].message.content or "No response generated"
            return self._clean_response(content)
        except Exception as e:
            return f"❌ Error calling Groq API: {str(e)}"

    @staticmethod
    def _clean_response(text: str) -> str:
        """Remove markdown-like formatting that does not render well in chat."""
        cleaned = text.replace("*", "")
        return "\n".join(line.rstrip() for line in cleaned.splitlines()).strip()

    @staticmethod
    def _compact_text(text: str, max_chars: int) -> str:
        """Collapse whitespace and trim text to reduce token usage."""
        compact = re.sub(r"\s+", " ", text).strip()
        if len(compact) <= max_chars:
            return compact
        return compact[: max(0, max_chars - 3)].rstrip() + "..."

    def _format_resumes(self, resumes: Dict[str, str], max_chars_per_resume: int) -> str:
        """Build a compact resume bundle for prompts."""
        return "\n\n".join(
            f"--- RESUME: {name} --- {self._compact_text(content, max_chars_per_resume)}"
            for name, content in resumes.items()
        )
    
    def analyze_resumes(self, jd_text: str, resumes: Dict[str, str]) -> str:
        """
        Analyze resumes against JD
        Returns comprehensive analysis
        """
        resumes_formatted = self._format_resumes(resumes, 450)
        
        prompt = f"""You are an expert ATS (Applicant Tracking System) and recruitment consultant.

    Return a concise plain-text answer only. Do not use markdown, bullets, or asterisks.
    Keep the response short and easy to scan.

ANALYZE THE FOLLOWING RESUMES AGAINST THE JOB DESCRIPTION:

JOB DESCRIPTION:
{self._compact_text(jd_text, 800)}

RESUMES:
{resumes_formatted}

PROVIDE A COMPREHENSIVE ANALYSIS:
1. **Overall Assessment** - Summary of how candidates match the JD
2. **Skill Match Analysis** - Which candidates have required/preferred skills
3. **Experience Alignment** - How well experience matches JD requirements
4. **Ranking** - Rank candidates (Best to Worst)
5. **Key Strengths** - Highlight strong points for each candidate
6. **Missing Elements** - What's lacking in each resume

Format response with short labeled sections only."""

        return self._call_groq(prompt, max_tokens=1200)
    
    def get_improvements(self, jd_text: str, resumes: Dict[str, str]) -> str:
        """
        Get specific improvement suggestions for each resume
        """
        resumes_formatted = self._format_resumes(resumes, 350)
        
        prompt = f"""You are an expert resume writer and career coach.

    Return a concise plain-text answer only. Do not use markdown, bullets, or asterisks.
    Keep each resume summary short and actionable.

ANALYZE THESE RESUMES AGAINST THE JOB DESCRIPTION AND SUGGEST IMPROVEMENTS:

JOB DESCRIPTION (Key Requirements):
{self._compact_text(jd_text, 600)}

RESUMES TO IMPROVE:
{resumes_formatted}

FOR EACH RESUME, PROVIDE:

1. **Specific Keywords to Add** - Keywords from JD missing in resume
2. **Skills to Highlight** - How to better present existing skills
3. **Experience Reframing** - How to reword experience to match JD
4. **Formatting Suggestions** - Structure/layout improvements
5. **Content Improvements** - What to add or expand
6. **Action Items** - Top 3 prioritized improvements

Be specific and actionable with examples, but keep it brief."""

        return self._call_groq(prompt, max_tokens=1000)
    
    def compare_resumes(self, jd_text: str, resumes: Dict[str, str]) -> str:
        """
        Compare resumes and rank them
        """
        resumes_formatted = self._format_resumes(resumes, 300)

        prompt = f"""You are an expert recruiter evaluating candidates.

Return STRICT JSON only. Do not use markdown, bullets, code fences, or asterisks.
Do not include any extra text outside the JSON.

Use this schema:
{{
    "rows": [
        {{
            "rank": 1,
            "candidate": "Name",
            "skill_match": "9/10",
            "experience_match": "8/10",
            "overall_fit": "9/10",
            "notes": "one short sentence"
        }}
    ],
    "summary": "short summary",
    "recommendation": "one line recommendation"
}}

Keep notes short and direct.

COMPARE AND RANK THESE RESUMES FOR THE FOLLOWING POSITION:

JOB DESCRIPTION:
{self._compact_text(jd_text, 550)}

CANDIDATES:
{resumes_formatted}

Be concise and data-driven."""

        return self._call_groq(prompt, max_tokens=1100)
    
    def extract_info(self, resumes: Dict[str, str]) -> str:
        """
        Extract structured information from resumes
        """
        resumes_formatted = self._format_resumes(resumes, 350)

        prompt = f"""Extract and organize key information from these resumes:

Return STRICT JSON only. Do not use markdown, bullets, code fences, or asterisks.
Do not include any extra text outside the JSON.

Use this schema:
{{
    "resumes": [
        {{
            "name": "Resume name",
            "personal_info": {{
                "name": "N/A",
                "email": "N/A",
                "phone": "N/A",
                "location": "N/A"
            }},
            "summary": "short summary",
            "skills": ["skill 1", "skill 2"],
            "experience": ["short experience item"],
            "education": ["short education item"],
            "certifications": ["N/A"],
            "languages": ["N/A"]
        }}
    ]
}}

RESUMES:
{resumes_formatted}

Keep entries short and readable."""

        return self._call_groq(prompt, max_tokens=1000)
    
    def custom_query(self, jd_text: str, resumes: Dict[str, str], query: str) -> str:
        """
        Handle custom user queries about resumes and JD
        """
        resumes_formatted = self._format_resumes(resumes, 300)
        
        prompt = f"""You are an ATS expert and recruitment consultant.

USER QUESTION: {query}

CONTEXT:

JOB DESCRIPTION:
{self._compact_text(jd_text, 550)}

CANDIDATE RESUMES:
{resumes_formatted}

ANSWER THE USER'S QUESTION:
- Be specific and reference the resumes/JD where applicable
- Provide actionable insights
- Use data from the documents to support your answer
- If the question is about specific candidates, mention them by name"""

        return self._call_groq(prompt, max_tokens=900)
    
    def score_resume(self, jd_text: str, resume_text: str, resume_name: str) -> str:
        """
        Score a single resume against JD
        """
        prompt = f"""Score this resume against the job description:

JOB DESCRIPTION:
{self._compact_text(jd_text, 550)}

RESUME: {resume_name}
{self._compact_text(resume_text, 700)}

PROVIDE:
1. **Overall Match Score** (1-100)
2. **Score Breakdown**:
   - Skills Match: 1-10
   - Experience Match: 1-10
   - Education Match: 1-10
   - Overall Fit: 1-10
3. **Key Matches** - Best matching aspects
4. **Gaps** - Missing skills/experience
5. **Recommendation** - Pass/Review/Strong consideration
"""

        return self._call_groq(prompt, max_tokens=700)
    
    def generate_cover_letter_tips(self, jd_text: str, resume_text: str) -> str:
        """
        Generate cover letter suggestions based on resume and JD
        """
        prompt = f"""Based on this resume and job description, suggest cover letter content:

JOB DESCRIPTION:
{self._compact_text(jd_text, 550)}

RESUME:
{self._compact_text(resume_text, 550)}

SUGGEST:
1. **Opening Hook** - Attention-grabbing opening
2. **Key Points to Highlight** - Top 3 selling points
3. **Experience Examples** - Specific examples to mention
4. **Skills Connection** - How to connect skills to JD
5. **Closing Statement** - Strong closing

Be specific and compelling."""

        return self._call_groq(prompt, max_tokens=700)
    
    def check_ats_compatibility(self, resume_text: str) -> str:
        """
        Check if resume is ATS-friendly
        """
        prompt = f"""Analyze this resume for ATS (Applicant Tracking System) compatibility:

RESUME:
{self._compact_text(resume_text, 800)}

CHECK FOR:
1. **Format Issues** - Complex formatting that might confuse ATS
2. **Keyword Density** - Important keywords presence
3. **Structure** - Logical section organization
4. **Readability** - Clear, parseable content
5. **Issues Found** - Specific ATS compatibility problems
6. **Recommendations** - How to fix issues

Rate ATS Compatibility: Poor / Fair / Good / Excellent"""

        return self._call_groq(prompt, max_tokens=700)


# Test function
if __name__ == "__main__":
    try:
        llm = LLMEngine()
        print("✅ Groq API connected successfully!")
        print(f"Model: {llm.model}")
    except Exception as e:
        print(f"❌ Error initializing LLM: {str(e)}")
