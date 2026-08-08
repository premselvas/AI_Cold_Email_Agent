import re
import json
import os
from groq import Groq
from config import Config

class ATSMatcher:
    """Agent that calculates ATS match score between resume and job description."""
    
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.model = Config.GROQ_MODEL
        if self.api_key and self.api_key != 'your_groq_api_key_here':
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None

    def calculate_match(self, resume_text: str, jd_text: str) -> dict:
        """Calculate match percentage, matched skills, missing skills, and keywords."""
        if not resume_text or not jd_text:
            return {
                "match_percentage": 0,
                "matched_skills": [],
                "missing_skills": [],
                "suggested_keywords": []
            }
            
        if self.client:
            try:
                prompt = f"""
Compare the following Resume and Job Description.
Return a JSON object ONLY with the following exact keys:
"match_percentage": (integer between 0 and 100),
"matched_skills": (list of skills present in both),
"missing_skills": (list of important skills required in JD but missing in Resume),
"suggested_keywords": (list of keywords to add to resume)

Resume:
{resume_text[:2000]}

Job Description:
{jd_text[:2000]}
"""
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert ATS screening system. Respond only in valid JSON format."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                
                result = json.loads(response.choices[0].message.content)
                return {
                    "match_percentage": int(result.get("match_percentage", 70)),
                    "matched_skills": list(result.get("matched_skills", [])),
                    "missing_skills": list(result.get("missing_skills", [])),
                    "suggested_keywords": list(result.get("suggested_keywords", []))
                }
            except Exception:
                pass
                
        # Rule-based fallback if LLM unavailable
        return self._heuristic_match(resume_text, jd_text)

    def _heuristic_match(self, resume_text: str, jd_text: str) -> dict:
        resume_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', resume_text.lower()))
        jd_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', jd_text.lower()))
        
        stopwords = {'and', 'the', 'for', 'with', 'that', 'this', 'you', 'are', 'have', 'from', 'will', 'your', 'our', 'team', 'work', 'experience'}
        jd_keywords = jd_words - stopwords
        matched = resume_words.intersection(jd_keywords)
        missing = jd_keywords - resume_words
        
        match_pct = int((len(matched) / max(len(jd_keywords), 1)) * 100)
        match_pct = min(max(match_pct, 40), 95)
        
        return {
            "match_percentage": match_pct,
            "matched_skills": [w.capitalize() for w in list(matched)[:8]],
            "missing_skills": [w.capitalize() for w in list(missing)[:8]],
            "suggested_keywords": [w.capitalize() for w in list(missing)[8:16]]
        }
