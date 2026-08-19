"""
Email Service for ResumeIQ.
Generates responsive, high-converting HTML resume analysis reports and sends them via Gmail SMTP.
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


def generate_email_html(report_data: Dict[str, Any], candidate_email: str) -> str:
    """Generates a responsive modern HTML email template for the resume review."""
    score = report_data.get("overall_score", 0)
    score_grade = report_data.get("score_grade", "Strong")
    target_role = report_data.get("target_role", "General Professional")
    summary = report_data.get("summary", "")
    ats_score = report_data.get("ats_score", 0)
    sub_scores = report_data.get("sub_scores", {})
    strengths = report_data.get("strengths", [])
    missing_skills = report_data.get("missing_skills", [])
    improvement_suggestions = report_data.get("improvement_suggestions", [])
    bullet_rewrites = report_data.get("bullet_rewrites", [])
    ats_feedback = report_data.get("ats_feedback", {})
    final_recommendation = report_data.get("final_recommendation", "")

    # Score theme color
    if score >= 85:
        score_color = "#10b981"  # Emerald
        grade_badge = "background-color: #d1fae5; color: #065f46;"
    elif score >= 70:
        score_color = "#3b82f6"  # Blue
        grade_badge = "background-color: #dbeafe; color: #1e40af;"
    elif score >= 55:
        score_color = "#f59e0b"  # Amber
        grade_badge = "background-color: #fef3c7; color: #92400e;"
    else:
        score_color = "#ef4444"  # Red
        grade_badge = "background-color: #fee2e2; color: #991b1b;"

    # Format Strengths HTML
    strengths_html = ""
    for s in strengths:
        strengths_html += f"""
        <div style="background-color: #f8fafc; border-left: 4px solid #10b981; padding: 12px 16px; margin-bottom: 12px; border-radius: 0 8px 8px 0;">
            <strong style="color: #0f172a; font-size: 14px;">✓ {s.get('title', '')}</strong>
            <p style="margin: 4px 0 0 0; color: #475569; font-size: 13px; line-height: 1.5;">{s.get('description', '')}</p>
        </div>
        """

    # Format Missing Skills Badges
    skills_badges = ""
    for skill in missing_skills:
        skills_badges += f"""<span style="display: inline-block; background-color: #fee2e2; color: #991b1b; padding: 4px 10px; margin: 3px; border-radius: 20px; font-size: 12px; font-weight: 600;">+ {skill}</span>"""

    # Format Actionable Improvements
    improvements_html = ""
    for imp in improvement_suggestions:
        improvements_html += f"""
        <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; margin-bottom: 12px; background: #ffffff;">
            <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #6366f1; letter-spacing: 0.5px;">{imp.get('category', 'Category')}</div>
            <div style="font-size: 13px; color: #334155; margin-top: 4px; font-weight: 500;"><strong>Gap:</strong> {imp.get('issue', '')}</div>
            <div style="font-size: 13px; color: #047857; margin-top: 6px; background-color: #ecfdf5; padding: 8px 12px; border-radius: 6px;"><strong>Action:</strong> {imp.get('action', '')}</div>
        </div>
        """

    # Format Bullet Rewrites
    rewrites_html = ""
    for rw in bullet_rewrites:
        rewrites_html += f"""
        <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 14px; margin-bottom: 14px;">
            <div style="font-size: 12px; color: #dc2626; text-decoration: line-through; margin-bottom: 6px;">❌ {rw.get('original', '')}</div>
            <div style="font-size: 13px; color: #15803d; font-weight: 600; margin-bottom: 6px;">✨ {rw.get('improved', '')}</div>
            <div style="font-size: 11px; color: #64748b; font-style: italic;">Why: {rw.get('reason', '')}</div>
        </div>
        """

    # Tips list
    ats_tips_html = ""
    for tip in ats_feedback.get("tips", []):
        ats_tips_html += f"""<li style="margin-bottom: 6px; font-size: 13px; color: #334155;">{tip}</li>"""

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ResumeIQ Analysis Report</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; margin: 0; padding: 24px 12px; color: #1e293b;">
    <table align="center" width="100%" cellpadding="0" cellspacing="0" style="max-width: 650px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;">
        <!-- Header Banner -->
        <tr>
            <td style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); padding: 32px 24px; text-align: center; color: #ffffff;">
                <div style="display: inline-block; background: rgba(99, 102, 241, 0.2); border: 1px solid rgba(129, 140, 248, 0.3); border-radius: 20px; padding: 4px 14px; font-size: 12px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: #818cf8; margin-bottom: 12px;">
                    AI Resume Evaluation
                </div>
                <h1 style="margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -0.5px;">Resume<span style="color: #6366f1;">IQ</span></h1>
                <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 14px;">Comprehensive Audit & ATS Optimization Report</p>
                <div style="margin-top: 14px; display: inline-block; background: rgba(255,255,255,0.1); padding: 6px 16px; border-radius: 8px; font-size: 13px; color: #f8fafc;">
                    Target Role: <strong style="color: #38bdf8;">{target_role}</strong>
                </div>
            </td>
        </tr>

        <!-- Main Body -->
        <tr>
            <td style="padding: 28px 24px;">

                <!-- Score Highlight Box -->
                <table width="100%" cellpadding="0" cellspacing="0" style="background: #f8fafc; border-radius: 12px; padding: 20px; border: 1px solid #e2e8f0; margin-bottom: 24px;">
                    <tr>
                        <td align="center" style="width: 45%; border-right: 1px solid #e2e8f0; padding-right: 16px;">
                            <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #64748b; letter-spacing: 0.5px;">Overall Score</div>
                            <div style="font-size: 52px; font-weight: 900; color: {score_color}; line-height: 1; margin: 6px 0;">{score}<span style="font-size: 20px; color: #94a3b8; font-weight: 600;">/100</span></div>
                            <span style="display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; {grade_badge}">{score_grade} Match</span>
                        </td>
                        <td style="padding-left: 20px; width: 55%;">
                            <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #64748b; margin-bottom: 8px;">Sub-Score Breakdown</div>
                            <table width="100%" style="font-size: 12px; color: #334155;">
                                <tr>
                                    <td>ATS Compatibility</td>
                                    <td align="right"><strong>{ats_score}%</strong></td>
                                </tr>
                                <tr>
                                    <td>Technical Alignment</td>
                                    <td align="right"><strong>{sub_scores.get('technical_skills', 0)}%</strong></td>
                                </tr>
                                <tr>
                                    <td>Impact & Metrics</td>
                                    <td align="right"><strong>{sub_scores.get('experience_impact', 0)}%</strong></td>
                                </tr>
                                <tr>
                                    <td>Structure & Flow</td>
                                    <td align="right"><strong>{sub_scores.get('formatting_structure', 0)}%</strong></td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>

                <!-- Executive Summary -->
                <div style="margin-bottom: 24px;">
                    <h3 style="margin: 0 0 8px 0; font-size: 16px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px;">Executive Evaluation</h3>
                    <p style="margin: 0; color: #334155; font-size: 14px; line-height: 1.6; background-color: #f1f5f9; padding: 14px; border-radius: 8px;">
                        {summary}
                    </p>
                </div>

                <!-- Strengths -->
                <div style="margin-bottom: 24px;">
                    <h3 style="margin: 0 0 12px 0; font-size: 16px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px;">Key Strengths</h3>
                    {strengths_html}
                </div>

                <!-- Missing Keywords -->
                <div style="margin-bottom: 24px; background: #fff5f5; border: 1px solid #fecaca; border-radius: 10px; padding: 16px;">
                    <h3 style="margin: 0 0 6px 0; font-size: 15px; color: #991b1b;">High-Value Keywords Missing</h3>
                    <p style="margin: 0 0 10px 0; font-size: 12px; color: #7f1d1d;">Include these industry terms in your work experience bullet points to boost ATS visibility:</p>
                    <div>
                        {skills_badges}
                    </div>
                </div>

                <!-- Actionable Suggestions -->
                <div style="margin-bottom: 24px;">
                    <h3 style="margin: 0 0 12px 0; font-size: 16px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px;">Actionable Improvements</h3>
                    {improvements_html}
                </div>

                <!-- Bullet Rewrites -->
                <div style="margin-bottom: 24px;">
                    <h3 style="margin: 0 0 12px 0; font-size: 16px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px;">Recommended Bullet Point Rewrites</h3>
                    {rewrites_html}
                </div>

                <!-- ATS Check -->
                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin-bottom: 24px;">
                    <h3 style="margin: 0 0 8px 0; font-size: 15px; color: #0f172a;">ATS Readability Verdict: <span style="color: #6366f1;">{ats_feedback.get('verdict', 'Pass')}</span></h3>
                    <p style="margin: 0 0 10px 0; font-size: 13px; color: #475569;">{ats_feedback.get('file_formatting_check', '')}</p>
                    <ul style="margin: 0; padding-left: 20px;">
                        {ats_tips_html}
                    </ul>
                </div>

                <!-- Recommendation Box -->
                <div style="background: linear-gradient(135deg, #e0e7ff 0%, #ede9fe 100%); border-left: 4px solid #6366f1; border-radius: 0 10px 10px 0; padding: 16px; margin-bottom: 12px;">
                    <strong style="color: #3730a3; font-size: 14px; display: block; margin-bottom: 4px;">🚀 Final Recommendation</strong>
                    <p style="margin: 0; color: #312e81; font-size: 13px; line-height: 1.5;">{final_recommendation}</p>
                </div>

            </td>
        </tr>

        <!-- Footer -->
        <tr>
            <td style="background-color: #f8fafc; border-top: 1px solid #e2e8f0; padding: 20px 24px; text-align: center; color: #64748b; font-size: 12px;">
                <p style="margin: 0 0 6px 0;">This automated AI audit was generated by <strong>ResumeIQ</strong> for <strong>{candidate_email}</strong>.</p>
                <p style="margin: 0; color: #94a3b8;">Good luck with your job search and interview preparations!</p>
            </td>
        </tr>
    </table>
</body>
</html>
    """
    return html


def send_resume_report_email(
    recipient_email: str,
    report_data: Dict[str, Any],
    smtp_user: Optional[str] = None,
    smtp_pass: Optional[str] = None,
    smtp_server: Optional[str] = None,
    smtp_port: Optional[int] = None
) -> Dict[str, Any]:
    """
    Sends the resume report via Gmail SMTP or custom SMTP server.
    
    Returns:
        Dict with status, message, and rendered_html for UI preview.
    """
    html_content = generate_email_html(report_data, recipient_email)
    
    user = smtp_user or os.getenv("SMTP_EMAIL")
    password = smtp_pass or os.getenv("SMTP_PASSWORD")
    server_host = smtp_server or os.getenv("SMTP_SERVER", "smtp.gmail.com")
    server_port = int(smtp_port or os.getenv("SMTP_PORT", 587))

    # If no SMTP credentials, return preview ready with informative status
    if not user or not password:
        return {
            "sent": False,
            "simulated": True,
            "recipient": recipient_email,
            "message": "SMTP credentials not provided. An in-app email preview has been generated for you.",
            "rendered_html": html_content,
            "instructions": "To enable real email delivery, set SMTP_EMAIL and SMTP_PASSWORD (a 16-character Gmail App Password) in your .env file or Settings modal."
        }

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🎯 ResumeIQ Report: {report_data.get('overall_score', 0)}/100 for {report_data.get('target_role', 'Your Role')}"
        msg["From"] = f"ResumeIQ AI Analyzer <{user}>"
        msg["To"] = recipient_email

        # Plain text fallback
        plain_text = f"ResumeIQ Analysis Report\nRole: {report_data.get('target_role')}\nScore: {report_data.get('overall_score')}/100\nGrade: {report_data.get('score_grade')}\nSummary: {report_data.get('summary')}"
        msg.attach(MIMEText(plain_text, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        # Connect and send
        if server_port == 465:
            server = smtplib.SMTP_SSL(server_host, server_port, timeout=15)
        else:
            server = smtplib.SMTP(server_host, server_port, timeout=15)
            server.starttls()

        server.login(user, password)
        server.sendmail(user, [recipient_email], msg.as_string())
        server.quit()

        return {
            "sent": True,
            "simulated": False,
            "recipient": recipient_email,
            "message": f"📩 Your detailed resume report has been sent to {recipient_email} successfully.",
            "rendered_html": html_content,
            "instructions": None
        }

    except Exception as e:
        print(f"[Email Error] Failed to send email via SMTP: {e}")
        return {
            "sent": False,
            "simulated": False,
            "recipient": recipient_email,
            "message": f"Failed to send email via SMTP: {str(e)}",
            "rendered_html": html_content,
            "instructions": "Check your Gmail App Password. Regular Gmail passwords do not work with SMTP; create an App Password under Google Account -> Security -> 2-Step Verification."
        }
