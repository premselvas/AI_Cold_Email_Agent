import pandas as pd
import io
import re

class ExcelParser:
    """Helper to parse and validate uploaded Excel / CSV files for bulk email outreach."""

    REQUIRED_FIELDS = ['company_name', 'role', 'hr_email', 'job_description']

    COLUMN_ALIASES = {
        'company_name': ['company_name', 'company name', 'company', 'organization', 'org'],
        'role': ['role', 'job_role', 'job role', 'title', 'job_title', 'job title', 'position'],
        'hr_email': ['hr_email', 'hr email', 'email', 'recipient', 'to_email', 'contact_email', 'hr'],
        'job_description': ['job_description', 'job description', 'jd', 'jd_text', 'description', 'job_url', 'url']
    }

    @classmethod
    def parse_file(cls, file_or_path) -> list:
        """
        Read Excel (.xlsx, .xls) or CSV file.
        Returns a list of dicts with standardized keys:
        [{'company_name': ..., 'role': ..., 'hr_email': ..., 'job_description': ...}]
        """
        try:
            df = None
            filename = ""

            if isinstance(file_or_path, str):
                filename = file_or_path.lower()
                if filename.endswith('.csv'):
                    df = pd.read_csv(file_or_path)
                else:
                    try:
                        df = pd.read_excel(file_or_path, engine='openpyxl')
                    except Exception:
                        df = pd.read_excel(file_or_path)
            else:
                # Handle Streamlit UploadedFile or BytesIO
                filename = getattr(file_or_path, 'name', '').lower()
                
                # Get bytes stream
                if hasattr(file_or_path, 'read'):
                    content = file_or_path.read()
                    stream = io.BytesIO(content)
                    if hasattr(file_or_path, 'seek'):
                        file_or_path.seek(0)
                else:
                    stream = file_or_path

                if filename.endswith('.csv'):
                    df = pd.read_csv(stream)
                else:
                    # Try openpyxl engine explicitly for excel stream
                    try:
                        df = pd.read_excel(stream, engine='openpyxl')
                    except Exception:
                        if hasattr(stream, 'seek'):
                            stream.seek(0)
                        try:
                            df = pd.read_excel(stream)
                        except Exception:
                            if hasattr(stream, 'seek'):
                                stream.seek(0)
                            df = pd.read_csv(stream)

            if df is None or df.empty:
                return []

            # Standardize column headers
            mapped_cols = {}
            for col in df.columns:
                col_clean = str(col).strip().lower()
                for target_key, aliases in cls.COLUMN_ALIASES.items():
                    if col_clean in aliases and target_key not in mapped_cols:
                        mapped_cols[target_key] = col
                        break

            # Build standardized list of rows
            records = []
            for idx, row in df.iterrows():
                company = str(row.get(mapped_cols.get('company_name'), '')).strip()
                role = str(row.get(mapped_cols.get('role'), '')).strip()
                hr_email = str(row.get(mapped_cols.get('hr_email'), '')).strip()
                jd = str(row.get(mapped_cols.get('job_description'), '')).strip()

                # Clean nan strings
                if company.lower() == 'nan': company = ''
                if role.lower() == 'nan': role = ''
                if hr_email.lower() == 'nan': hr_email = ''
                if jd.lower() == 'nan': jd = ''

                records.append({
                    'row_num': idx + 1,
                    'company_name': company,
                    'role': role,
                    'hr_email': hr_email,
                    'job_description': jd
                })

            return records
        except Exception as e:
            raise RuntimeError(f"Failed to read Excel/CSV file: {str(e)}")

    @classmethod
    def generate_sample_excel_bytes(cls) -> bytes:
        """Generate sample Excel file bytes for user download."""
        df_sample = pd.DataFrame([
            {
                "Company Name": "TechCorp Inc.",
                "Job Role": "Software Engineer Intern",
                "HR Email": "hr@techcorp.example.com",
                "Job Description": "Looking for a Python developer proficient in REST APIs, SQL, and Git."
            },
            {
                "Company Name": "DataVision Labs",
                "Job Role": "Data Analyst",
                "HR Email": "careers@datavision.example.com",
                "Job Description": "Seeking candidate with Pandas, SQL, Data Visualization, and Machine Learning skills."
            },
            {
                "Company Name": "CloudNet Solutions",
                "Job Role": "SEO & Digital Marketing Intern",
                "HR Email": "recruiting@cloudnet.example.com",
                "Job Description": "Requirements: SEO, Google Analytics, Content Optimization, Python scripting."
            }
        ])
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_sample.to_excel(writer, index=False, sheet_name='HR_Leads')
        buffer.seek(0)
        return buffer.getvalue()
