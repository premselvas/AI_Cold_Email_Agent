from parser.resume_info import ResumeInfoExtractor

class ResumeAnalyzer:
    """Agent that analyzes candidate resume content."""

    def __init__(self):
        self.extractor = ResumeInfoExtractor()

    def analyze(self, resume_text: str) -> dict:
        """Analyze resume text and extract candidate profile."""
        return self.extractor.extract_info(resume_text)
