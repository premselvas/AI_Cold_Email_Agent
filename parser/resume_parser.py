import io
import pdfplumber

class ResumeParser:
    """Class to handle parsing PDF resumes into text."""
    
    @staticmethod
    def parse(file_or_path) -> str:
        """
        Extract text from a PDF resume.
        Supports file paths, BytesIO objects, or Streamlit UploadedFile objects.
        """
        text = ""
        try:
            if isinstance(file_or_path, str):
                with pdfplumber.open(file_or_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            else:
                # BytesIO or Streamlit UploadedFile
                if hasattr(file_or_path, 'read'):
                    file_bytes = io.BytesIO(file_or_path.read())
                    # Reset pointer for future reads if needed
                    if hasattr(file_or_path, 'seek'):
                        file_or_path.seek(0)
                else:
                    file_bytes = file_or_path

                with pdfplumber.open(file_bytes) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                            
            return text.strip()
        except Exception as e:
            raise RuntimeError(f"Error parsing PDF resume: {str(e)}")

def extract_resume_text(pdf_path):
    """Backward compatibility function."""
    return ResumeParser.parse(pdf_path)