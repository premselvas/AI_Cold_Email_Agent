import streamlit as st
import os
import time
from datetime import datetime
from config import Config
from agents.email_writer import EmailWriter
from agents.ats_matcher import ATSMatcher
from agents.company_research import CompanyResearch
from parser.resume_parser import ResumeParser
from parser.resume_info import ResumeInfoExtractor
from parser.jd_parser import JobDescriptionParser
from parser.excel_parser import ExcelParser
from gmail.gmail_sender import GmailSender
from database.database import Database
from utils.logger import setup_logger
from utils.validators import Validators
from utils.helpers import Helpers
import pandas as pd

logger = setup_logger()

def init_session_state():
    """Initialize all session state variables."""
    if 'resume_text' not in st.session_state:
        st.session_state.resume_text = ""
    if 'resume_info' not in st.session_state:
        st.session_state.resume_info = {}
    if 'jd_text' not in st.session_state:
        st.session_state.jd_text = ""
    if 'ats_score' not in st.session_state:
        st.session_state.ats_score = {}
    if 'generated_email' not in st.session_state:
        st.session_state.generated_email = {}
    if 'company_info' not in st.session_state:
        st.session_state.company_info = {}
    if 'email_history' not in st.session_state:
        st.session_state.email_history = []
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'email_sent' not in st.session_state:
        st.session_state.email_sent = False
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="AI Cold Email Agent",
        page_icon="📧",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("📧 AI Cold Email Agent")
        st.markdown("---")
        
        # Navigation
        nav_option = st.radio(
            "Navigation",
            ["📝 Generate Single Email", "📁 Excel Bulk Campaign", "📊 Email History", "⚙️ Settings"],
            index=0
        )
        
        st.markdown("---")
        st.info("💡 **Tips**\n- Upload resume & job details\n- Process single or bulk Excel outreach\n- Track campaigns in History")
        
        if st.button("🔄 Reset Everything"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main content
    if nav_option == "📝 Generate Single Email":
        render_generate_email()
    elif nav_option == "📁 Excel Bulk Campaign":
        render_bulk_campaign()
    elif nav_option == "📊 Email History":
        render_email_history()
    else:
        render_settings()

def render_generate_email():
    """Render the email generation page."""
    st.title("📝 Generate Cold Email")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Step 1: Upload Resume
        st.subheader("Step 1: Upload Resume")
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF only)",
            type=['pdf'],
            help="Maximum file size: 5MB"
        )
        
        if uploaded_file:
            if st.session_state.uploaded_file != uploaded_file:
                st.session_state.uploaded_file = uploaded_file
                st.session_state.resume_text = ""
                st.session_state.resume_info = {}
                
                with st.spinner("Parsing resume..."):
                    try:
                        resume_text = ResumeParser.parse(uploaded_file)
                        st.session_state.resume_text = resume_text
                        
                        info_extractor = ResumeInfoExtractor()
                        resume_info = info_extractor.extract_info(resume_text)
                        st.session_state.resume_info = resume_info
                        
                        st.success("✅ Resume parsed successfully!")
                        logger.info("Resume parsed successfully")
                    except Exception as e:
                        st.error(f"❌ Error parsing resume: {str(e)}")
                        logger.error(f"Resume parsing error: {str(e)}")
        
        if st.session_state.resume_info:
            with st.expander("📄 Resume Information", expanded=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("**Name:**", st.session_state.resume_info.get('name', 'N/A'))
                    st.write("**Email:**", st.session_state.resume_info.get('email', 'N/A'))
                    st.write("**Phone:**", st.session_state.resume_info.get('phone', 'N/A'))
                with col_b:
                    st.write("**Skills:**", ", ".join(st.session_state.resume_info.get('skills', [])[:5]))
                    st.write("**Education:**", st.session_state.resume_info.get('education', ['N/A'])[0])
        
        # Step 2: Job Description
        st.subheader("Step 2: Job Description")
        
        jd_input_method = st.radio(
            "Choose input method:",
            ["Paste Job Description", "Enter Job URL"],
            horizontal=True
        )
        
        if jd_input_method == "Paste Job Description":
            jd_text = st.text_area(
                "Paste the job description here:",
                height=200,
                placeholder="Copy and paste the complete job description..."
            )
            if jd_text:
                st.session_state.jd_text = jd_text
        else:
            job_url = st.text_input(
                "Enter job posting URL:",
                placeholder="https://example.com/job-posting"
            )
            if job_url:
                if st.button("Fetch Job Description"):
                    with st.spinner("Fetching job description..."):
                        try:
                            jd_text = JobDescriptionParser.parse_url(job_url)
                            if jd_text:
                                st.session_state.jd_text = jd_text
                                st.success("✅ Job description fetched successfully!")
                            else:
                                st.error("❌ Could not fetch job description. Please paste it manually.")
                        except Exception as e:
                            st.error(f"❌ Error fetching job description: {str(e)}")
        
        if st.session_state.jd_text:
            with st.expander("📋 Job Description Preview"):
                st.text_area("", st.session_state.jd_text, height=150)
        
        # Step 3: Company Details
        st.subheader("Step 3: Company & Role Details")
        
        col_c, col_d = st.columns(2)
        with col_c:
            company_name = st.text_input("Company Name *", placeholder="e.g., Google", key="input_company")
            hr_email = st.text_input("HR Email *", placeholder="hr@company.com", key="input_hr_email")
        with col_d:
            role = st.text_input("Job Role *", placeholder="e.g., Data Analyst", key="input_role")
        
        # Step 4: Generate Email
        st.subheader("Step 4: Generate Email")
        
        if st.button("🚀 Generate Cold Email", type="primary"):
            if not validate_inputs(company_name, hr_email, role):
                st.warning("⚠️ Please fill in all required fields with valid email.")
            elif not st.session_state.resume_text:
                st.warning("⚠️ Please upload a resume first.")
            elif not st.session_state.jd_text:
                st.warning("⚠️ Please provide a job description.")
            else:
                with st.spinner("Generating cold email with Groq AI..."):
                    try:
                        # Research company
                        research = CompanyResearch()
                        company_info = research.research_company(company_name)
                        st.session_state.company_info = company_info
                        
                        # ATS Match
                        ats = ATSMatcher()
                        ats_result = ats.calculate_match(
                            st.session_state.resume_text,
                            st.session_state.jd_text
                        )
                        st.session_state.ats_score = ats_result
                        
                        # Generate email
                        email_writer = EmailWriter()
                        email_result = email_writer.generate_email(
                            resume_text=st.session_state.resume_text,
                            jd_text=st.session_state.jd_text,
                            company_name=company_name,
                            role=role,
                            company_info=company_info,
                            ats_result=ats_result
                        )
                        
                        st.session_state.generated_email = email_result
                        st.session_state.email_sent = False
                        
                        st.success("✅ Email generated successfully!")
                        logger.info("Email generated successfully")
                    except Exception as e:
                        st.error(f"❌ Error generating email: {str(e)}")
                        logger.error(f"Email generation error: {str(e)}")
        
        # Display ATS Score
        if st.session_state.ats_score:
            with st.expander("📊 ATS Analysis", expanded=True):
                col_score1, col_score2, col_score3 = st.columns(3)
                with col_score1:
                    st.metric("ATS Score", f"{st.session_state.ats_score.get('match_percentage', 0)}%")
                with col_score2:
                    st.metric("Matched Skills", len(st.session_state.ats_score.get('matched_skills', [])))
                with col_score3:
                    st.metric("Missing Skills", len(st.session_state.ats_score.get('missing_skills', [])))
                
                if st.session_state.ats_score.get('matched_skills'):
                    st.write("✅ **Matched Skills:**", ", ".join(st.session_state.ats_score['matched_skills'][:10]))
                if st.session_state.ats_score.get('missing_skills'):
                    st.warning("⚠️ **Missing Skills:** " + ", ".join(st.session_state.ats_score['missing_skills'][:10]))
                if st.session_state.ats_score.get('suggested_keywords'):
                    st.info("💡 **Suggested Keywords:** " + ", ".join(st.session_state.ats_score['suggested_keywords'][:10]))
    
    with col2:
        # Step 5: Email Preview
        st.subheader("Step 5: Email Preview")
        
        if st.session_state.generated_email:
            email_data = st.session_state.generated_email
            
            edited_subject = st.text_area("✏️ Subject", value=email_data.get('subject', ''), key='email_subject_edit')
            edited_body = st.text_area("✏️ Body", value=email_data.get('body', ''), key='email_body_edit', height=350)
            
            # Save edited email
            if st.button("💾 Save Edits"):
                st.session_state.generated_email['subject'] = edited_subject
                st.session_state.generated_email['body'] = edited_body
                st.success("✅ Email updated!")
            
            # Download options directly rendered
            st.markdown("##### 📥 Export Options")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                content = f"Subject: {st.session_state.generated_email.get('subject', '')}\n\n{st.session_state.generated_email.get('body', '')}"
                Helpers.download_file(content, "generated_email.txt", "text/plain")
            with col_d2:
                content = f"Subject: {st.session_state.generated_email.get('subject', '')}\n\n{st.session_state.generated_email.get('body', '')}"
                Helpers.download_docx(content, "generated_email.docx")
            
            # Send email
            st.markdown("---")
            st.subheader("📤 Send Email")
            
            target_to_email = st.text_input("To *", value=st.session_state.get('input_hr_email', ''))
            cc_email = st.text_input("CC (optional)")
            bcc_email = st.text_input("BCC (optional)")
            
            if st.button("📤 Send Email", type="primary"):
                if not target_to_email:
                    st.warning("⚠️ Please enter recipient email address.")
                elif not Validators.validate_email(target_to_email):
                    st.warning("⚠️ Invalid email address format.")
                else:
                    with st.spinner("Sending email via Gmail API..."):
                        status_saved = 'failed'
                        err_msg = None
                        try:
                            gmail = GmailSender()
                            attachments = []
                            if st.session_state.uploaded_file:
                                attachments.append(st.session_state.uploaded_file)
                            
                            success = gmail.send_email(
                                to=target_to_email,
                                cc=cc_email if cc_email else None,
                                bcc=bcc_email if bcc_email else None,
                                subject=st.session_state.generated_email.get('subject', ''),
                                body=st.session_state.generated_email.get('body', ''),
                                attachments=attachments
                            )
                            
                            if success:
                                st.session_state.email_sent = True
                                status_saved = 'sent'
                                st.success("✅ Email sent successfully!")
                                logger.info(f"Email sent to {target_to_email}")
                        except Exception as e:
                            err_msg = str(e)
                            st.error(f"❌ Error sending email: {err_msg}")
                            logger.error(f"Email send error: {err_msg}")
                        finally:
                            # Save record to Database regardless of send status
                            try:
                                db = Database()
                                db.save_email(
                                    company_name=st.session_state.get('input_company', 'N/A'),
                                    role=st.session_state.get('input_role', 'N/A'),
                                    hr_email=target_to_email,
                                    subject=st.session_state.generated_email.get('subject', ''),
                                    status=status_saved,
                                    resume_filename=st.session_state.uploaded_file.name if st.session_state.uploaded_file else None,
                                    error_message=err_msg
                                )
                            except Exception as dbe:
                                logger.error(f"DB log error: {dbe}")
        else:
            st.info("💡 Fill in the details and click 'Generate Cold Email'")
            
            # Display company info if available
            if st.session_state.company_info:
                with st.expander("🏢 Company Information"):
                    info = st.session_state.company_info
                    st.write("**Industry:**", info.get('industry', 'N/A'))
                    st.write("**About:**", info.get('about', 'N/A'))
                    st.write("**Products:**", ", ".join(info.get('products', [])[:3]))
                    st.write("**Tech Stack:**", ", ".join(info.get('technologies', [])[:5]))

def render_bulk_campaign():
    """Render the Excel Bulk Cold Email Campaign page."""
    st.title("📁 Excel Bulk Cold Email Campaign")
    st.markdown("Automate personalized cold outreach to multiple HR contacts uploaded via Excel or CSV.")
    st.markdown("---")
    
    # Download sample template
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.info("📌 **Excel Format Requirements:** Columns should include `Company Name`, `Job Role`, `HR Email`, and `Job Description`.")
    with col_t2:
        sample_bytes = ExcelParser.generate_sample_excel_bytes()
        st.download_button(
            label="📥 Download Sample Template",
            data=sample_bytes,
            file_name="sample_hr_list.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.markdown("---")
    col_b1, col_b2 = st.columns([1, 1])

    with col_b1:
        st.subheader("Step 1: Upload Resume")
        uploaded_resume = st.file_uploader(
            "Upload your resume (PDF)",
            type=['pdf'],
            key="bulk_resume_uploader"
        )

        if uploaded_resume:
            if st.session_state.uploaded_file != uploaded_resume:
                st.session_state.uploaded_file = uploaded_resume
                st.session_state.resume_text = ResumeParser.parse(uploaded_resume)
                st.session_state.resume_info = ResumeInfoExtractor().extract_info(st.session_state.resume_text)
                st.success("✅ Resume parsed successfully!")

        if st.session_state.resume_text:
            st.success(f"📄 Resume Active: **{st.session_state.resume_info.get('name', 'Candidate')}** ({len(st.session_state.resume_text)} characters parsed)")
        else:
            st.warning("⚠️ Please upload a PDF resume first.")

    with col_b2:
        st.subheader("Step 2: Upload Excel / CSV File")
        uploaded_excel = st.file_uploader(
            "Upload Excel (.xlsx, .xls) or CSV file containing HR leads",
            type=['xlsx', 'xls', 'csv'],
            key="bulk_excel_uploader"
        )

    records = []
    if uploaded_excel:
        try:
            records = ExcelParser.parse_file(uploaded_excel)
            if records:
                st.success(f"✅ Found **{len(records)}** total rows in file!")
            else:
                st.error("❌ No data rows found in uploaded file.")
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")

    if records:
        st.markdown("---")
        st.subheader("📋 Campaign Preview & Data Table")
        
        df_preview = pd.DataFrame(records)
        
        # Check validity
        valid_rows = []
        invalid_rows = []
        for r in records:
            if r['company_name'] and r['role'] and r['hr_email'] and Validators.validate_email(r['hr_email']) and r['job_description']:
                valid_rows.append(r)
            else:
                invalid_rows.append(r)

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Total Leads", len(records))
        with col_m2:
            st.metric("Valid Rows", len(valid_rows))
        with col_m3:
            st.metric("Invalid Rows", len(invalid_rows))

        st.dataframe(df_preview[['row_num', 'company_name', 'role', 'hr_email', 'job_description']], use_container_width=True)

        if invalid_rows:
            st.warning(f"⚠️ {len(invalid_rows)} row(s) contain missing or invalid required fields and will be skipped.")

        st.markdown("---")
        st.subheader("⚙️ Execution Settings")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            action_mode = st.radio(
                "Select Action:",
                ["📤 Send Emails directly via Gmail", "📝 Generate & Save Drafts to Database"],
                index=0
            )
        with col_s2:
            delay_sec = st.slider("Delay between emails (seconds):", min_value=1, max_value=10, value=2)

        st.markdown("---")
        if st.button("🚀 Launch Bulk Cold Email Campaign", type="primary", disabled=not (st.session_state.resume_text and valid_rows)):
            st.subheader("⚡ Campaign Execution Progress")
            
            progress_bar = st.progress(0.0)
            status_text = st.empty()
            
            db = Database()
            gmail = GmailSender() if "Send" in action_mode else None
            research = CompanyResearch()
            ats = ATSMatcher()
            email_writer = EmailWriter()

            results = []
            total_valid = len(valid_rows)

            for idx, row in enumerate(valid_rows):
                pct = (idx + 1) / total_valid
                progress_bar.progress(pct)
                
                c_name = row['company_name']
                c_role = row['role']
                c_email = row['hr_email']
                c_jd = row['job_description']

                status_text.markdown(f"⏳ **Processing Row {idx+1}/{total_valid}:** Generating email for **{c_role}** at **{c_name}** (`{c_email}`)...")

                try:
                    # 1. Research Company
                    c_info = research.research_company(c_name)
                    # 2. ATS Match
                    ats_res = ats.calculate_match(st.session_state.resume_text, c_jd)
                    # 3. Generate Email
                    email_obj = email_writer.generate_email(
                        resume_text=st.session_state.resume_text,
                        jd_text=c_jd,
                        company_name=c_name,
                        role=c_role,
                        company_info=c_info,
                        ats_result=ats_res
                    )

                    send_status = 'draft'
                    err_msg = None

                    if "Send" in action_mode:
                        try:
                            attachments = [st.session_state.uploaded_file] if st.session_state.uploaded_file else []
                            sent_ok = gmail.send_email(
                                to=c_email,
                                subject=email_obj.get('subject', ''),
                                body=email_obj.get('body', ''),
                                attachments=attachments
                            )
                            send_status = 'sent' if sent_ok else 'failed'
                        except Exception as se:
                            send_status = 'failed'
                            err_msg = str(se)
                    
                    # Save to DB
                    db.save_email(
                        company_name=c_name,
                        role=c_role,
                        hr_email=c_email,
                        subject=email_obj.get('subject', ''),
                        status=send_status,
                        resume_filename=st.session_state.uploaded_file.name if st.session_state.uploaded_file else None,
                        error_message=err_msg
                    )

                    results.append({
                        'Row': row['row_num'],
                        'Company': c_name,
                        'Role': c_role,
                        'HR Email': c_email,
                        'ATS Score': f"{ats_res.get('match_percentage', 0)}%",
                        'Status': '✅ Sent' if send_status == 'sent' else ('📝 Draft' if send_status == 'draft' else '❌ Failed'),
                        'Subject': email_obj.get('subject', ''),
                        'Error': err_msg or ''
                    })

                except Exception as ex:
                    results.append({
                        'Row': row['row_num'],
                        'Company': c_name,
                        'Role': c_role,
                        'HR Email': c_email,
                        'ATS Score': 'N/A',
                        'Status': '❌ Failed',
                        'Subject': 'N/A',
                        'Error': str(ex)
                    })

                time.sleep(delay_sec)

            progress_bar.progress(1.0)
            status_text.success("🎉 **Bulk Campaign Completed Successfully!**")

            # Summary metrics
            df_results = pd.DataFrame(results)
            sent_count = len(df_results[df_results['Status'].str.contains('Sent|Draft')])
            fail_count = len(df_results[df_results['Status'].str.contains('Failed')])

            col_res1, col_res2, col_res3 = st.columns(3)
            with col_res1:
                st.metric("Total Processed", len(results))
            with col_res2:
                st.metric("Successful / Drafted", sent_count)
            with col_res3:
                st.metric("Failed", fail_count)

            st.markdown("### 📊 Campaign Results Detail")
            st.dataframe(df_results, use_container_width=True)

def render_email_history():
    """Render the email history page."""
    st.title("📊 Email History")
    st.markdown("---")
    
    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        search_company = st.text_input("Search by Company")
    with col_f2:
        search_role = st.text_input("Search by Role")
    with col_f3:
        status_filter = st.selectbox("Status", ["All", "sent", "draft", "failed"])
    
    # Fetch history
    try:
        db = Database()
        history = db.get_email_history()
        
        if history:
            df = pd.DataFrame(history)
            
            # Apply filters
            if search_company:
                df = df[df['company_name'].str.contains(search_company, case=False, na=False)]
            if search_role:
                df = df[df['role'].str.contains(search_role, case=False, na=False)]
            if status_filter != "All":
                df = df[df['status'] == status_filter]
            
            if not df.empty:
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    st.metric("Total Emails", len(df))
                with col_s2:
                    st.metric("Sent", len(df[df['status'] == 'sent']))
                with col_s3:
                    st.metric("Failed", len(df[df['status'] == 'failed']))
                
                st.markdown("---")
                
                display_cols = ['company_name', 'role', 'hr_email', 'subject', 'status', 'sent_date']
                st.dataframe(
                    df[display_cols].sort_values('sent_date', ascending=False),
                    use_container_width=True
                )
                
                st.markdown("---")
                st.subheader("📄 Email Details")
                
                selected_idx = st.selectbox(
                    "Select an email to view details",
                    range(len(df)),
                    format_func=lambda x: f"{df.iloc[x]['company_name']} - {df.iloc[x]['role']} ({df.iloc[x]['sent_date']})"
                )
                
                if selected_idx is not None:
                    email = df.iloc[selected_idx]
                    with st.expander("Email Details", expanded=True):
                        st.write("**Company:**", email['company_name'])
                        st.write("**Role:**", email['role'])
                        st.write("**HR Email:**", email['hr_email'])
                        st.write("**Subject:**", email['subject'])
                        st.write("**Status:**", email['status'])
                        st.write("**Date:**", email['sent_date'])
                        if email['error_message']:
                            st.error(f"**Error:** {email['error_message']}")
            else:
                st.info("No emails found matching the filters.")
        else:
            st.info("No emails sent yet. Start generating and sending emails!")
            
    except Exception as e:
        st.error(f"❌ Error loading email history: {str(e)}")
        logger.error(f"Email history error: {str(e)}")

def render_settings():
    """Render the settings page."""
    st.title("⚙️ Settings")
    st.markdown("---")
    
    st.subheader("Configuration")
    
    # Display current config
    has_groq = bool(Config.GROQ_API_KEY and Config.GROQ_API_KEY != 'your_groq_api_key_here')
    has_gmail = os.path.exists('credentials.json') or os.path.exists('credentials.json.json')
    
    st.info(f"**GROQ API Key:** {'✅ Configured' if has_groq else '❌ Not configured'}")
    st.info(f"**Gmail Credentials:** {'✅ Configured' if has_gmail else '❌ Not configured'}")
    
    st.markdown("---")
    
    st.subheader("System Status")
    col_status1, col_status2, col_status3 = st.columns(3)
    
    with col_status1:
        if has_groq:
            st.success("✅ Groq API")
        else:
            st.error("❌ Groq API")
    
    with col_status2:
        if has_gmail:
            st.success("✅ Gmail API")
        else:
            st.error("❌ Gmail API")
    
    with col_status3:
        try:
            db = Database()
            st.success("✅ Database")
        except:
            st.error("❌ Database")
    
    st.markdown("---")
    
    st.subheader("Logs")
    if st.button("📄 View Recent Logs"):
        try:
            if os.path.exists(Config.LOG_FILE):
                with open(Config.LOG_FILE, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-50:]
                    st.code(''.join(lines))
            else:
                st.warning("No log file created yet.")
        except Exception as e:
            st.warning(f"Could not read logs: {e}")

def validate_inputs(company_name, hr_email, role):
    """Validate the input fields."""
    if not company_name or not hr_email or not role:
        return False
    if not Validators.validate_email(hr_email):
        return False
    return True

if __name__ == "__main__":
    main()