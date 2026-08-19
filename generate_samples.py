"""
Utility to generate 3 realistic sample PDF resumes for testing ResumeIQ.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def create_resume_pdf(filename, name, contact, summary, experience, skills, education):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        fontName='Helvetica-Bold'
    )
    contact_style = ParagraphStyle(
        'ContactInfo',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569'),
        fontName='Helvetica'
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#4338ca'),
        fontName='Helvetica-Bold',
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1e293b'),
        fontName='Helvetica'
    )
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        fontName='Helvetica',
        leftIndent=12
    )

    # Name and Contact Header
    story.append(Paragraph(name, title_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph(contact, contact_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=8))

    # Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", section_heading))
    story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 6))

    # Experience
    story.append(Paragraph("WORK EXPERIENCE", section_heading))
    for job in experience:
        job_header = f"<b>{job['title']}</b> | {job['company']} <i>({job['dates']})</i>"
        story.append(Paragraph(job_header, body_style))
        for bullet in job['bullets']:
            story.append(Paragraph(f"• {bullet}", bullet_style))
        story.append(Spacer(1, 4))

    # Skills
    story.append(Paragraph("TECHNICAL & CORE SKILLS", section_heading))
    for skill_cat, skill_list in skills.items():
        story.append(Paragraph(f"<b>{skill_cat}:</b> {', '.join(skill_list)}", body_style))
    story.append(Spacer(1, 6))

    # Education
    story.append(Paragraph("EDUCATION", section_heading))
    for edu in education:
        story.append(Paragraph(f"<b>{edu['degree']}</b> — {edu['school']} ({edu['year']})", body_style))

    doc.build(story)
    print(f"Generated sample PDF: {filename}")

if __name__ == "__main__":
    out_dir = "sample_resumes"

    # 1. Backend Dev
    create_resume_pdf(
        os.path.join(out_dir, "Alex_Morgan_Backend_Developer.pdf"),
        name="Alex Morgan",
        contact="alex.morgan@email.com • (555) 349-2810 • San Francisco, CA • github.com/alexmorgan",
        summary="Results-driven Backend Engineer with 4+ years of experience designing scalable microservices, RESTful APIs, and distributed database systems. Proven track record of reducing query latency by 42% and deploying cloud-native architectures on AWS.",
        experience=[
            {
                "title": "Senior Backend Engineer",
                "company": "CloudScale Tech (San Francisco, CA)",
                "dates": "June 2022 - Present",
                "bullets": [
                    "Architected and deployed 14+ high-throughput microservices using Python (FastAPI) and Golang, handling 45M+ daily requests with 99.98% uptime.",
                    "Redesigned relational PostgreSQL schema and implemented Redis caching layer, decreasing average query response time by 42%.",
                    "Built automated CI/CD deployment pipelines using Docker, Kubernetes, and GitHub Actions, slashing release deployment cycles from 4 days to 25 minutes.",
                    "Integrated Kafka event streams for asynchronous payment processing, preventing duplicate transactions and processing $12M+ in monthly transaction volume."
                ]
            },
            {
                "title": "Software Engineer",
                "company": "FinFlow Systems (Austin, TX)",
                "dates": "July 2020 - May 2022",
                "bullets": [
                    "Developed REST and GraphQL APIs using Node.js, Express, and MongoDB for a core fintech banking dashboard with 85,000 active users.",
                    "Implemented OAuth2 / JWT authentication protocol with role-based access control (RBAC), securing sensitive financial client data.",
                    "Authored 300+ unit and integration test cases using PyTest and Jest, boosting code coverage from 62% to 91%."
                ]
            }
        ],
        skills={
            "Languages": ["Python", "Go", "JavaScript", "TypeScript", "SQL", "Bash"],
            "Frameworks": ["FastAPI", "Django", "Flask", "Express", "Node.js"],
            "Databases & Queues": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Apache Kafka", "RabbitMQ"],
            "Cloud & DevOps": ["AWS (ECS, S3, RDS, Lambda)", "Docker", "Kubernetes", "Terraform", "CI/CD", "Git"]
        },
        education=[
            {"degree": "Bachelor of Science in Computer Science", "school": "University of California, Berkeley", "year": "2016 - 2020"}
        ]
    )

    # 2. Frontend Dev
    create_resume_pdf(
        os.path.join(out_dir, "Samantha_Lee_Frontend_Developer.pdf"),
        name="Samantha Lee",
        contact="samantha.lee@email.com • (555) 782-9012 • New York, NY • portfolio.samanthalee.dev",
        summary="Creative and user-centric Frontend Developer with 3+ years of experience crafting responsive, performant web applications using React, TypeScript, and Next.js. Passionate about design systems and WCAG accessibility.",
        experience=[
            {
                "title": "Frontend Engineer",
                "company": "PixelCraft Studios (New York, NY)",
                "dates": "August 2022 - Present",
                "bullets": [
                    "Built modern client-facing applications using React 18, Next.js, and TypeScript, serving 300,000+ monthly active users.",
                    "Redesigned core checkout funnel with Tailwind CSS and Zustand state management, improving conversion rates by 18%.",
                    "Optimized Core Web Vitals, improving Google Lighthouse performance score from 64 to 96 across all landing pages.",
                    "Created reusable UI component library following WCAG 2.1 AA accessibility standards, adopted by 4 distinct cross-functional product teams."
                ]
            },
            {
                "title": "Junior Web Developer",
                "company": "Digital Horizon (Brooklyn, NY)",
                "dates": "Sept 2021 - July 2022",
                "bullets": [
                    "Developed interactive responsive web pages using HTML5, CSS3, JavaScript (ES6+), and Vue.js.",
                    "Collaborated closely with UI/UX designers in Figma to translate mockups into pixel-perfect interactive prototypes.",
                    "Implemented end-to-end testing with Cypress and Jest, reducing client-side bug reports by 35%."
                ]
            }
        ],
        skills={
            "Core": ["JavaScript (ES6+)", "TypeScript", "HTML5", "CSS3", "Sass"],
            "Frameworks": ["React", "Next.js", "Vue.js", "Tailwind CSS", "Styled Components"],
            "State & Tools": ["Redux Toolkit", "Zustand", "Vite", "Webpack", "Git", "Jest", "Cypress", "Figma"]
        },
        education=[
            {"degree": "B.S. in Interactive Media & Web Design", "school": "New York University", "year": "2017 - 2021"}
        ]
    )

    # 3. HR Specialist
    create_resume_pdf(
        os.path.join(out_dir, "Elena_Vance_HR_Manager.pdf"),
        name="Elena Vance",
        contact="elena.vance@email.com • (555) 492-1830 • Chicago, IL • linkedin.com/in/elenavance-hr",
        summary="Dynamic Human Resources Specialist with 5+ years of experience managing full-cycle talent acquisition, employee relations, DE&I initiatives, and HR compliance for high-growth tech organizations.",
        experience=[
            {
                "title": "Human Resources Manager",
                "company": "Apex Innovations (Chicago, IL)",
                "dates": "January 2022 - Present",
                "bullets": [
                    "Spearheaded end-to-end recruitment for engineering, sales, and executive roles, hiring 65+ top-tier candidates and reducing time-to-hire by 28%.",
                    "Implemented modern HRIS & ATS platform (Workday & Greenhouse), automating onboarding workflows and achieving a 96% new hire satisfaction rating.",
                    "Designed comprehensive performance management framework, facilitating biannual 360-degree reviews for 220+ global employees.",
                    "Partnered with executive leadership to develop DE&I hiring strategies, increasing underrepresented group representation across senior leadership by 22%."
                ]
            }
        ],
        skills={
            "Talent Acquisition": ["Greenhouse", "Lever", "LinkedIn Recruiter", "Structured Interviewing"],
            "HRIS & Operations": ["Workday", "BambooHR", "ADP Workforce Now", "Payroll Administration"],
            "Compliance": ["FMLA", "FLSA", "EEOC", "OSHA", "Performance Management", "Conflict Resolution"]
        },
        education=[
            {"degree": "SHRM-CP Certified", "school": "Society for Human Resource Management", "year": "2021"},
            {"degree": "B.A. in Human Resources Management", "school": "University of Illinois Urbana-Champaign", "year": "2015 - 2019"}
        ]
    )
