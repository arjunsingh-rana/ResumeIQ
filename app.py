"""
ResumeIQ - AI Resume Analyzer
Main Flask Application Server
"""
import os
import io
import json
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

from services.pdf_service import extract_text_from_pdf
from services.ai_service import analyze_resume, ROLE_BENCHMARKS
from services.email_service import send_resume_report_email, generate_email_html

# Load environment variables
load_dotenv()

# Ensure template and static directories resolve correctly in serverless / local environments
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB Max Upload


@app.route('/')
def index():
    """Render the primary single-page application dashboard."""
    return render_template('index.html')


@app.route('/api/roles', methods=['GET'])
def get_roles():
    """Return available preset roles and benchmark highlights."""
    roles = [
        {"id": "backend", "name": "Backend Developer", "icon": "fa-server"},
        {"id": "frontend", "name": "Frontend Developer", "icon": "fa-code"},
        {"id": "hr", "name": "HR / Human Resources", "icon": "fa-users-gear"},
        {"id": "fullstack", "name": "Full Stack Developer", "icon": "fa-layer-group"},
        {"id": "datascience", "name": "Data Scientist / AI Engineer", "icon": "fa-brain"},
        {"id": "general", "name": "General / Best Practices", "icon": "fa-briefcase"},
        {"id": "custom", "name": "Other (Custom Role)", "icon": "fa-wand-magic-sparkles"}
    ]
    return jsonify({"roles": roles})


@app.route('/api/config-status', methods=['GET'])
def config_status():
    """Return active integrations status."""
    has_openai = bool(os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY").startswith("sk-"))
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    has_smtp = bool(os.getenv("SMTP_EMAIL") and os.getenv("SMTP_PASSWORD"))

    return jsonify({
        "openai_configured": has_openai,
        "gemini_configured": has_gemini,
        "smtp_configured": has_smtp,
        "smtp_email": os.getenv("SMTP_EMAIL", "")
    })


@app.route('/api/save-config', methods=['POST'])
def save_config():
    """Update runtime configuration parameters."""
    data = request.get_json() or {}
    
    if data.get("openai_key"):
        os.environ["OPENAI_API_KEY"] = data["openai_key"].strip()
    if data.get("gemini_key"):
        os.environ["GEMINI_API_KEY"] = data["gemini_key"].strip()
    if data.get("smtp_email"):
        os.environ["SMTP_EMAIL"] = data["smtp_email"].strip()
    if data.get("smtp_password"):
        os.environ["SMTP_PASSWORD"] = data["smtp_password"].strip()

    return jsonify({
        "success": True,
        "message": "Configuration updated successfully."
    })


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint.
    Accepts PDF file, target role, candidate email, and returns structured AI report.
    """
    if 'resume' not in request.files and 'text' not in request.form:
        return jsonify({"success": False, "error": "Please upload a resume PDF file or provide text."}), 400

    target_role = request.form.get('role', 'General / Best Practices')
    custom_role = request.form.get('custom_role', '').strip()
    candidate_email = request.form.get('email', '').strip()
    api_key_override = request.form.get('api_key', '').strip() or None

    # Extract text
    if 'resume' in request.files:
        file = request.files['resume']
        if not file.filename.lower().endswith(('.pdf', '.txt')):
            return jsonify({"success": False, "error": "Only PDF or TXT files are supported."}), 400
        
        pdf_meta = extract_text_from_pdf(file)
        if not pdf_meta["success"]:
            return jsonify({"success": False, "error": pdf_meta["error"]}), 400
        resume_text = pdf_meta["text"]
    else:
        resume_text = request.form.get('text', '').strip()
        pdf_meta = {
            "page_count": 1,
            "word_count": len(resume_text.split()),
            "detected_sections": [],
            "detected_email": None,
            "detected_phone": None,
            "preview_snippet": resume_text[:300]
        }

    if len(resume_text.strip()) < 50:
        return jsonify({
            "success": False,
            "error": "The resume text is too short or could not be extracted. Please upload a clear PDF with selectable text."
        }), 400

    # Auto-detect email if not provided by user
    if not candidate_email and pdf_meta.get("detected_email"):
        candidate_email = pdf_meta["detected_email"]

    # Run AI analysis
    analysis_result = analyze_resume(
        resume_text=resume_text,
        target_role=target_role,
        custom_role=custom_role,
        api_key_override=api_key_override
    )

    # Email automation if candidate email provided
    email_delivery_result = None
    if candidate_email:
        email_delivery_result = send_resume_report_email(
            recipient_email=candidate_email,
            report_data=analysis_result
        )
    else:
        # Generate HTML preview for UI
        html_preview = generate_email_html(analysis_result, "candidate@example.com")
        email_delivery_result = {
            "sent": False,
            "simulated": True,
            "recipient": None,
            "message": "Enter your email above to have the full report automatically sent to your inbox.",
            "rendered_html": html_preview
        }

    return jsonify({
        "success": True,
        "meta": {
            "page_count": pdf_meta.get("page_count", 1),
            "word_count": pdf_meta.get("word_count", 0),
            "detected_sections": pdf_meta.get("detected_sections", []),
            "candidate_email": candidate_email
        },
        "report": analysis_result,
        "email_delivery": email_delivery_result
    })


@app.route('/api/send-email', methods=['POST'])
def send_email_endpoint():
    """Trigger or re-send email delivery for an analyzed report."""
    data = request.get_json() or {}
    recipient_email = data.get("email", "").strip()
    report_data = data.get("report")

    if not recipient_email:
        return jsonify({"success": False, "error": "Recipient email is required."}), 400
    if not report_data:
        return jsonify({"success": False, "error": "Analysis report data is required."}), 400

    result = send_resume_report_email(recipient_email, report_data)
    return jsonify({"success": True, "delivery": result})


@app.route('/api/sample-resume/<role_id>', methods=['GET'])
def get_sample_resume(role_id):
    """Provide realistic sample resume text for 1-click testing."""
    samples = {
        "backend": {
            "role": "Backend Developer",
            "text": """Alex Morgan
alex.morgan@email.com | (555) 349-2810 | San Francisco, CA | github.com/alexmorgan | linkedin.com/in/alexmorgan

PROFESSIONAL SUMMARY
Results-driven Backend Engineer with 4+ years of experience designing scalable microservices, RESTful APIs, and distributed database systems. Proven track record of optimizing database queries, reducing API latency, and deploying cloud-native architectures on AWS.

WORK EXPERIENCE
Senior Backend Engineer | CloudScale Tech | San Francisco, CA
June 2022 - Present
- Architected and deployed 14+ high-throughput microservices using Python (FastAPI) and Golang, handling 45M+ daily requests with 99.98% uptime.
- Redesigned relational PostgreSQL schema and implemented Redis caching layer, decreasing average query response time by 42%.
- Built automated CI/CD deployment pipelines using Docker, Kubernetes, and GitHub Actions, slashing release deployment cycles from 4 days to 25 minutes.
- Integrated Kafka event streams for asynchronous payment processing, preventing duplicate transactions and processing $12M+ in monthly transaction volume.

Software Engineer | FinFlow Systems | Austin, TX
July 2020 - May 2022
- Developed REST and GraphQL APIs using Node.js, Express, and MongoDB for a core fintech banking dashboard with 85,000 active users.
- Implemented OAuth2 / JWT authentication protocol with role-based access control (RBAC), securing sensitive financial client data.
- Authored 300+ unit and integration test cases using PyTest and Jest, boosting code coverage from 62% to 91%.

TECHNICAL SKILLS
- Languages: Python, Go, JavaScript, TypeScript, SQL, Bash
- Frameworks: FastAPI, Django, Flask, Express, Node.js
- Databases & Queues: PostgreSQL, MySQL, MongoDB, Redis, Apache Kafka, RabbitMQ
- Cloud & DevOps: AWS (ECS, S3, RDS, Lambda), Docker, Kubernetes, Terraform, CI/CD, Git

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley | 2016 - 2020
"""
        },
        "frontend": {
            "role": "Frontend Developer",
            "text": """Samantha Lee
samantha.lee@email.com | (555) 782-9012 | New York, NY | portfolio.samanthalee.dev | github.com/samlee

PROFESSIONAL SUMMARY
Creative and user-centric Frontend Developer with 3+ years of experience crafting responsive, performant web applications using React, TypeScript, and Next.js. Passionate about design systems, WCAG accessibility, and web performance optimization.

WORK EXPERIENCE
Frontend Engineer | PixelCraft Studios | New York, NY
August 2022 - Present
- Built modern client-facing applications using React 18, Next.js, and TypeScript, serving 300,000+ monthly active users.
- Redesigned core checkout funnel with Tailwind CSS and Zustand state management, improving desktop and mobile conversion rates by 18%.
- Optimized Core Web Vitals (LCP, FID, CLS), improving Google Lighthouse performance score from 64 to 96 across all landing pages.
- Created reusable UI component library following WCAG 2.1 AA accessibility standards, adopted by 4 distinct cross-functional product teams.

Junior Web Developer | Digital Horizon | Brooklyn, NY
Sept 2021 - July 2022
- Developed interactive responsive web pages using HTML5, CSS3, JavaScript (ES6+), and Vue.js.
- Collaborated closely with UI/UX designers in Figma to translate mockups into pixel-perfect interactive prototypes.
- Implemented end-to-end testing with Cypress and unit testing with Jest, reducing client-side bug reports by 35%.

TECHNICAL SKILLS
- Core: JavaScript (ES6+), TypeScript, HTML5, CSS3/Sass
- Frameworks: React, Next.js, Vue.js, Tailwind CSS, Styled Components
- State & Data: Redux Toolkit, Zustand, React Query, REST APIs, GraphQL
- Tools & Testing: Vite, Webpack, Git, Jest, Cypress, Storybook, Figma

EDUCATION
B.S. in Interactive Media & Web Design
New York University | 2017 - 2021
"""
        },
        "hr": {
            "role": "HR / Human Resources",
            "text": """Elena Vance
elena.vance@email.com | (555) 492-1830 | Chicago, IL | linkedin.com/in/elenavance-hr

PROFESSIONAL SUMMARY
Dynamic Human Resources Specialist with 5+ years of experience managing full-cycle talent acquisition, employee relations, DE&I initiatives, and HR compliance for high-growth tech organizations.

WORK EXPERIENCE
Human Resources Manager | Apex Innovations | Chicago, IL
January 2022 - Present
- Spearheaded end-to-end recruitment for engineering, sales, and executive roles, hiring 65+ top-tier candidates and reducing time-to-hire by 28%.
- Implemented modern HRIS & ATS platform (Workday & Greenhouse), automating onboarding workflows and achieving a 96% new hire satisfaction rating.
- Designed comprehensive performance management framework, facilitating biannual 360-degree reviews for 220+ global employees.
- Partnered with executive leadership to develop DE&I hiring strategies, increasing underrepresented group representation across senior leadership by 22%.

HR Generalist & Talent Coordinator | Vantage Global | Chicago, IL
June 2019 - Dec 2021
- Managed employee benefits administration, 401(k) plans, payroll compliance, and state/federal labor law adherence across 4 regional offices.
- Resolved sensitive employee relations matters with empathy and confidentiality, decreasing voluntary turnover by 15%.
- Organized monthly professional development workshops and wellness initiatives, elevating company-wide employee engagement score to 88%.

CORE COMPETENCIES & SKILLS
- Talent Acquisition & Sourcing (Greenhouse, Lever, LinkedIn Recruiter)
- HRIS & Payroll (Workday, BambooHR, ADP Workforce Now)
- Employee Relations, Conflict Resolution, & Performance Management
- Labor Law Compliance (FMLA, FLSA, EEOC, OSHA)
- Onboarding & Retention Strategies, Culture Building

EDUCATION & CERTIFICATIONS
- SHRM-CP Certified (Society for Human Resource Management) | 2021
- Bachelor of Arts in Human Resources Management | University of Illinois Urbana-Champaign | 2015 - 2019
"""
        }
    }

    sample = samples.get(role_id, samples["backend"])
    return jsonify(sample)


if __name__ == '__main__':
    port = int(os.getenv("PORT", 5001))
    print(f"🚀 ResumeIQ Server running on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
