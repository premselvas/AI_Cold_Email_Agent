import os
import json
from groq import Groq
from config import Config
from parser.resume_info import ResumeInfoExtractor

class EmailWriter:
    """Agent for generating personalized cold emails based on user template."""

    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.model = Config.GROQ_MODEL
        if self.api_key and self.api_key != 'your_groq_api_key_here':
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None

    def generate_email(self, resume_text, jd_text, company_name="the company", role="Target Role", company_info=None, ats_result=None, resume_info=None):
        """
        Generate cold email following candidate's exact template.
        Returns a dict with {"subject": "...", "body": "..."}.
        """
        if not resume_info and resume_text:
            resume_info = ResumeInfoExtractor().extract_info(resume_text)
        elif not resume_info:
            resume_info = {}

        candidate_name = resume_info.get('name', 'Candidate')
        candidate_email = resume_info.get('email', 'email@example.com')
        candidate_phone = resume_info.get('phone', 'N/A')
        candidate_skills = ", ".join(resume_info.get('skills', ['Python', 'SQL', 'Data Analysis']))
        education_list = resume_info.get('education', [])
        candidate_degree = education_list[0] if education_list else "Artificial Intelligence and Data Science"

        if not self.client:
            return self._fallback_email(company_name, role, candidate_name, candidate_email, candidate_phone, candidate_degree, candidate_skills)

        matched_skills = ""
        if ats_result and isinstance(ats_result, dict):
            skills = ats_result.get('matched_skills', [])
            if skills:
                matched_skills = ", ".join(skills[:5])

        prompt = f"""
You are an expert cold email copywriter. Write a personalized email using the EXACT format provided below.

Inputs:
- Job Title: {role}
- Company Name: {company_name}
- Candidate Name: {candidate_name}
- Candidate Email: {candidate_email}
- Candidate Phone: {candidate_phone}
- Candidate Degree/Background: {candidate_degree}
- Top Skills & Matched Skills: {matched_skills or candidate_skills}

Resume Snippet:
{resume_text[:1500]}

Job Description Snippet:
{jd_text[:1500]}

REQUIRED OUTPUT FORMAT (JSON OBJECT ONLY):
{{
    "subject": "Application for {role} - {candidate_name}",
    "body": "Dear Hiring Manager,\\n\\nI hope you are doing well.\\n\\nI recently came across the opening for the {role} at {company_name} and would like to express my interest in the position.\\n\\n[Write 1 paragraph detailing background degree, hands-on experience with matched skills from JD, and real-world project accomplishments].\\n\\nI am eager to contribute to your team, learn from experienced professionals, and add value to your organization. I have attached my resume for your review.\\n\\nI would greatly appreciate the opportunity to discuss how my skills and enthusiasm align with your requirements.\\n\\nThank you for your time and consideration. I look forward to hearing from you.\\n\\nKind regards,\\n\\n{candidate_name}\\n📞 {candidate_phone}\\n📧 {candidate_email}\\n📄 Resume: Attached"
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a master cold email copywriter. Strictly follow the template format and output valid JSON ONLY."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            return {
                "subject": result.get("subject", f"Application for {role} - {candidate_name}"),
                "body": result.get("body", "")
            }
        except Exception as e:
            return self._fallback_email(company_name, role, candidate_name, candidate_email, candidate_phone, candidate_degree, candidate_skills)

    def _fallback_email(self, company_name, role, name, email, phone, degree, skills):
        body = f"""Dear Hiring Manager,

I hope you are doing well.

I recently came across the opening for the {role} at {company_name} and would like to express my interest in the position.

I am a graduate with a background in {degree} and hands-on experience in {skills}. During my academic journey, I have built multiple real-world projects and continuously worked on strengthening my technical and problem-solving skills.

I am eager to contribute to your team, learn from experienced professionals, and add value to your organization. I have attached my resume for your review.

I would greatly appreciate the opportunity to discuss how my skills and enthusiasm align with your requirements.

Thank you for your time and consideration. I look forward to hearing from you.

Kind regards,

{name}
📞 {phone}
📧 {email}
📄 Resume: Attached"""

        return {
            "subject": f"Application for {role} - {name}",
            "body": body
        }

def generate_email(resume, job_description):
    """Backward compatibility function."""
    writer = EmailWriter()
    res = writer.generate_email(resume, job_description)
    return f"Subject: {res['subject']}\n\n{res['body']}"