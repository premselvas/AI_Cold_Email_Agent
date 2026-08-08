from parser.jd_parser import JobDescriptionParser

class JobParserAgent:
    """Agent wrapper for job description extraction."""

    def __init__(self):
        self.parser = JobDescriptionParser()

    def parse_job_url(self, url: str) -> str:
        return self.parser.parse_url(url)