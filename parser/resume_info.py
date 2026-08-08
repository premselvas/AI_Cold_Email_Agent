import re

class ResumeInfoExtractor:
    """Extractor for resume structured metadata."""

    COMMON_SKILLS = [
        "python", "javascript", "typescript", "java", "c++", "c#", "html", "css", "sql", "nosql",
        "react", "angular", "vue", "node.js", "express", "django", "flask", "fastapi", "streamlit",
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "machine learning", "deep learning",
        "nlp", "data analysis", "seo", "digital marketing", "google analytics", "aws", "azure", "gcp",
        "docker", "kubernetes", "git", "github", "ci/cd", "rest api", "graphql", "agile", "scrum"
    ]

    def extract_info(self, text: str) -> dict:
        """Extract structured candidate info from resume text."""
        if not text:
            return {}

        email = self._extract_email(text)
        phone = self._extract_phone(text)
        name = self._extract_name(text, email)
        skills = self._extract_skills(text)
        education = self._extract_education(text)

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "skills": skills,
            "education": education
        }

    def _extract_email(self, text: str) -> str:
        match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        return match.group(0) if match else "N/A"

    def _extract_phone(self, text: str) -> str:
        match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        return match.group(0) if match else "N/A"

    def _extract_name(self, text: str, email: str) -> str:
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            first_line = lines[0]
            if len(first_line) < 40 and not any(char.isdigit() for char in first_line):
                return first_line.title()
        if email != "N/A":
            prefix = email.split('@')[0]
            clean = re.sub(r'[^a-zA-Z]', ' ', prefix).title().strip()
            if clean:
                return clean
        return "Candidate"

    def _extract_skills(self, text: str) -> list:
        found_skills = []
        text_lower = text.lower()
        for skill in self.COMMON_SKILLS:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill.capitalize() if len(skill) <= 3 else skill.title())
        return list(dict.fromkeys(found_skills))

    def _extract_education(self, text: str) -> list:
        degrees = ["bachelor", "master", "phd", "b.tech", "m.tech", "b.e", "b.s", "m.s", "degree", "diploma"]
        found = []
        for line in text.split('\n'):
            line_lower = line.lower()
            if any(d in line_lower for d in degrees):
                found.append(line.strip())
        return found if found else ["Bachelor's Degree"]
