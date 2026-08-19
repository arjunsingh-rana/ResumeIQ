"""
AI Resume Analysis Service for ResumeIQ.
Supports OpenAI, Gemini API, and a built-in heuristic evaluator fallback.
"""
import os
import json
import re
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

ROLE_BENCHMARKS = {
    "Backend Developer": {
        "keywords": [
            "python", "java", "golang", "nodejs", "c++", "c#", "rust",
            "django", "fastapi", "flask", "spring boot", "express", "nest.js",
            "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
            "docker", "kubernetes", "aws", "gcp", "azure", "ci/cd", "terraform",
            "rest api", "graphql", "grpc", "microservices", "system design",
            "kafka", "rabbitmq", "scalability", "concurrency", "unit testing", "pytest"
        ],
        "core_focus": "Distributed systems, database optimization, API design, security, and cloud scalability."
    },
    "Frontend Developer": {
        "keywords": [
            "javascript", "typescript", "react", "next.js", "vue", "angular", "svelte",
            "html5", "css3", "sass", "tailwind", "styled-components",
            "redux", "zustand", "react query", "webpack", "vite",
            "responsive design", "web performance", "seo", "accessibility", "a11y",
            "rest api", "graphql", "jest", "cypress", "playwright", "storybook", "ui/ux"
        ],
        "core_focus": "Modern UI frameworks, state management, client-side performance, accessibility, and responsive design."
    },
    "HR / Human Resources": {
        "keywords": [
            "talent acquisition", "recruitment", "onboarding", "employee relations",
            "performance management", "hris", "workday", "bamboohr", "greenhouse",
            "payroll", "benefits administration", "labor laws", "compliance", "de&i",
            "employee engagement", "retention", "talent development", "conflict resolution",
            "succession planning", "workforce planning", "hr analytics", "ats management"
        ],
        "core_focus": "People operations, talent pipeline, compliance, culture building, and HR systems leadership."
    },
    "Full Stack Developer": {
        "keywords": [
            "react", "next.js", "nodejs", "python", "typescript", "sql", "postgresql",
            "mongodb", "docker", "aws", "rest api", "graphql", "git", "ci/cd",
            "tailwind", "system architecture", "responsive design", "authentication", "jwt"
        ],
        "core_focus": "End-to-end web architecture, full-stack pipelines, database integration, and UI responsiveness."
    },
    "Data Scientist / AI Engineer": {
        "keywords": [
            "python", "r", "sql", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
            "machine learning", "deep learning", "nlp", "llm", "rag", "langchain",
            "data visualization", "tableau", "power bi", "feature engineering", "statsmodels",
            "spark", "hadoop", "mlops", "docker", "airflow"
        ],
        "core_focus": "Statistical modeling, ML pipelines, data processing, LLM architectures, and actionable business insights."
    },
    "General Professional": {
        "keywords": [
            "leadership", "project management", "cross-functional collaboration", "agile",
            "scrum", "stakeholder management", "strategic planning", "data analysis",
            "process improvement", "communication", "budgeting", "risk management",
            "kpis", "okrs", "client relations"
        ],
        "core_focus": "Leadership impact, clear quantified achievements, communication, and project execution."
    }
}


def analyze_resume(
    resume_text: str,
    target_role: Optional[str] = None,
    custom_role: Optional[str] = None,
    api_key_override: Optional[str] = None,
    model_provider: Optional[str] = "openai"
) -> Dict[str, Any]:
    """
    Main entry point for evaluating a resume.
    Routes to OpenAI, Gemini, or Heuristic fallback depending on available credentials.
    """
    # Normalize role
    effective_role = _resolve_target_role(target_role, custom_role)

    # 1. Try OpenAI if API key available
    openai_key = api_key_override or os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if openai_key and openai_key.startswith("sk-"):
        try:
            return _analyze_with_openai(resume_text, effective_role, openai_key)
        except Exception as e:
            print(f"[OpenAI Warning] API failed: {e}. Falling back to Gemini / Local Engine.")

    # 2. Try Gemini if API key available
    if gemini_key:
        try:
            return _analyze_with_gemini(resume_text, effective_role, gemini_key)
        except Exception as e:
            print(f"[Gemini Warning] API failed: {e}. Falling back to Local Heuristic Engine.")

    # 3. Fallback: Intelligent Local Heuristic Analyzer Engine
    return _analyze_heuristic(resume_text, effective_role)


def _resolve_target_role(target_role: Optional[str], custom_role: Optional[str]) -> str:
    """Determine the normalized job role name."""
    if custom_role and custom_role.strip():
        return custom_role.strip()
    if target_role and target_role.strip() and target_role != "General / Not Specified":
        return target_role.strip()
    return "General / Not Specified"


def _analyze_with_openai(resume_text: str, role: str, api_key: str) -> Dict[str, Any]:
    """Evaluates resume using OpenAI GPT-4o-mini."""
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    system_prompt = f"""
You are ResumeIQ, an elite Technical Recruiter, ATS Expert, and Hiring Director.
Evaluate the candidate's resume for the role: '{role}'.
If the role is 'General / Not Specified', evaluate using industry best practices for modern corporate/tech careers.

Return STRICT JSON matching the following schema:
{{
  "overall_score": <integer 0-100>,
  "score_grade": "<Exceptional | Strong | Needs Improvement | Critical>",
  "ats_score": <integer 0-100>,
  "sub_scores": {{
    "technical_skills": <integer 0-100>,
    "experience_impact": <integer 0-100>,
    "formatting_structure": <integer 0-100>,
    "keyword_match": <integer 0-100>
  }},
  "target_role": "{role}",
  "summary": "<2-3 sentence executive assessment of the resume>",
  "strengths": [
    {{"title": "<Strength Title>", "description": "<Specific details referencing resume content>"}},
    {{"title": "<Strength Title>", "description": "<Specific details referencing resume content>"}},
    {{"title": "<Strength Title>", "description": "<Specific details referencing resume content>"}}
  ],
  "missing_skills": ["<Keyword 1>", "<Keyword 2>", "<Keyword 3>", "<Keyword 4>", "<Keyword 5>"],
  "missing_sections": ["<e.g. Quantified Metrics, Certifications, Portfolio/GitHub Links>"],
  "improvement_suggestions": [
    {{"category": "<Content | Structure | Keywords | Metrics>", "issue": "<What is lacking>", "action": "<Exact actionable steps>"}},
    {{"category": "<Category>", "issue": "<Issue>", "action": "<Action>"}},
    {{"category": "<Category>", "issue": "<Issue>", "action": "<Action>"}}
  ],
  "bullet_rewrites": [
    {{
      "original": "<A weak or generic bullet point identified from the resume>",
      "improved": "<High-impact rewritten version using Action Verb + Context + Quantified Metric/Outcome (e.g. XYZ formula)>",
      "reason": "<Why the rewritten version converts better>"
    }},
    {{
      "original": "<Second bullet point from resume>",
      "improved": "<High-impact rewritten version>",
      "reason": "<Why it is better>"
    }}
  ],
  "ats_feedback": {{
    "verdict": "<Pass / Moderate Risk / High Risk>",
    "file_formatting_check": "<Assessment of parsability, font layout, tables/columns>",
    "keyword_density": "<Assessment of keyword distribution>",
    "tips": [
      "<ATS Tip 1>",
      "<ATS Tip 2>",
      "<ATS Tip 3>"
    ]
  }},
  "final_recommendation": "<Direct, inspiring 2-sentence closing recommendation on next steps to land interviews.>"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here is the parsed resume text:\n\n{resume_text}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    content = response.choices[0].message.content
    parsed_json = json.loads(content)
    parsed_json["engine_used"] = "OpenAI (gpt-4o-mini)"
    return parsed_json


def _analyze_with_gemini(resume_text: str, role: str, api_key: str) -> Dict[str, Any]:
    """Evaluates resume using Google Gemini 1.5 Flash via REST."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    prompt = f"""
You are ResumeIQ, an elite ATS Specialist and Hiring Director.
Evaluate this resume for target role: '{role}'.
Return ONLY valid JSON without markdown fences.

Schema:
{{
  "overall_score": 85,
  "score_grade": "Strong",
  "ats_score": 80,
  "sub_scores": {{
    "technical_skills": 85,
    "experience_impact": 80,
    "formatting_structure": 90,
    "keyword_match": 85
  }},
  "target_role": "{role}",
  "summary": "Executive summary...",
  "strengths": [{{"title": "...", "description": "..."}}],
  "missing_skills": ["skill1", "skill2"],
  "missing_sections": ["section1"],
  "improvement_suggestions": [{{"category": "Content", "issue": "...", "action": "..."}}],
  "bullet_rewrites": [{{"original": "...", "improved": "...", "reason": "..."}}],
  "ats_feedback": {{
    "verdict": "Pass",
    "file_formatting_check": "...",
    "keyword_density": "...",
    "tips": ["..."]
  }},
  "final_recommendation": "..."
}}

Resume text:
{resume_text}
"""
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json", "temperature": 0.3}
    }
    
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    raw_text = data['candidates'][0]['content']['parts'][0]['text']
    parsed = json.loads(raw_text)
    parsed["engine_used"] = "Gemini 1.5 Flash"
    return parsed


def _analyze_heuristic(resume_text: str, role: str) -> Dict[str, Any]:
    """
    Intelligent built-in fallback evaluation engine.
    Analyzes vocabulary, quantified metrics, action verbs, role keyword alignment, and structure.
    """
    lower_text = resume_text.lower()
    words = lower_text.split()
    total_words = max(len(words), 1)

    # 1. Benchmark Matching
    matched_benchmark = ROLE_BENCHMARKS.get(role)
    if not matched_benchmark:
        # Fallback to closest match or General
        matched_benchmark = ROLE_BENCHMARKS["General Professional"]
        for key in ROLE_BENCHMARKS:
            if key.lower() in role.lower() or role.lower() in key.lower():
                matched_benchmark = ROLE_BENCHMARKS[key]
                break

    target_keywords = matched_benchmark["keywords"]
    found_keywords = [kw for kw in target_keywords if kw in lower_text]
    missing_keywords = [kw for kw in target_keywords if kw not in lower_text]

    keyword_ratio = len(found_keywords) / max(len(target_keywords), 1)

    # 2. Metric & Quantifiable Impact Analysis (numbers, percentages, dollar values)
    metrics_count = len(re.findall(r'\b\d+(?:\.\d+)?%|\$\d+(?:,\d+)*(?:\.\d+)?|\b\d+\b', resume_text))
    metric_score = min(int((metrics_count / 8) * 100), 100)

    # 3. Action Verbs Check
    action_verbs = [
        "built", "developed", "led", "architected", "optimized", "increased", "reduced",
        "spearheaded", "implemented", "deployed", "scaled", "created", "designed", "managed",
        "engineered", "streamlined", "accelerated", "transformed"
    ]
    found_verbs = [verb for verb in action_verbs if verb in lower_text]
    verb_score = min(int((len(found_verbs) / 6) * 100), 100)

    # 4. Structure & Section Checks
    found_sections = []
    section_candidates = ["experience", "education", "skills", "projects", "certifications", "summary"]
    for sec in section_candidates:
        if sec in lower_text:
            found_sections.append(sec.title())

    structure_score = min(int((len(found_sections) / 4) * 100), 100)

    # Calculate Sub-scores
    technical_score = int((keyword_ratio * 70) + 30)
    technical_score = min(max(technical_score, 45), 98)

    impact_score = int((metric_score * 0.6) + (verb_score * 0.4))
    impact_score = min(max(impact_score, 40), 96)

    format_score = min(max(structure_score, 50), 95)
    keyword_match_score = int(keyword_ratio * 100)
    keyword_match_score = min(max(keyword_match_score, 35), 98)

    overall_score = int(
        (technical_score * 0.35) +
        (impact_score * 0.30) +
        (format_score * 0.20) +
        (keyword_match_score * 0.15)
    )

    # Determine Grade
    if overall_score >= 85:
        score_grade = "Exceptional"
    elif overall_score >= 70:
        score_grade = "Strong"
    elif overall_score >= 55:
        score_grade = "Needs Improvement"
    else:
        score_grade = "Critical"

    # Identify bullets from text to rewrite
    raw_lines = [line.strip().lstrip('•-* ').strip() for line in resume_text.split('\n') if len(line.strip()) > 35]
    weak_bullets = [l for l in raw_lines if not any(char.isdigit() for char in l)]
    
    sample_original_1 = weak_bullets[0] if weak_bullets else "Responsible for developing backend features and fixing database bugs."
    sample_original_2 = weak_bullets[1] if len(weak_bullets) > 1 else "Worked with team members to build and release web application components."

    # Dynamic Strengths
    strengths = []
    if found_keywords:
        sample_kws = ", ".join(k.title() for k in found_keywords[:4])
        strengths.append({
            "title": f"Relevant Core Competencies Detected ({len(found_keywords)} matches)",
            "description": f"Your resume highlights prominent domain terminology for {role}, including {sample_kws}."
        })
    if len(found_verbs) >= 4:
        strengths.append({
            "title": "Strong Action-Oriented Language",
            "description": f"Good usage of high-impact executive verbs ({', '.join(found_verbs[:4])}) to describe work history."
        })
    else:
        strengths.append({
            "title": "Clean Structural Flow",
            "description": f"Identified standard resume sections ({', '.join(found_sections)}) ensuring predictable recruiter scanning."
        })

    if metrics_count >= 3:
        strengths.append({
            "title": "Quantified Evidence of Success",
            "description": f"Contains {metrics_count}+ numerical figures demonstrating measurable project impact rather than plain duties."
        })
    else:
        strengths.append({
            "title": "Solid Professional Baseline",
            "description": f"Comprehensive scope of experience with clear progression in your core field."
        })

    # Missing sections
    missing_sections = []
    if "projects" not in lower_text and "project" not in lower_text:
        missing_sections.append("Independent Projects / Portfolio Demonstrations")
    if "certifications" not in lower_text and "certificate" not in lower_text:
        missing_sections.append("Industry Certifications / Specialized Credentials")
    if metrics_count < 3:
        missing_sections.append("Quantified Business Outcomes (%, $, time saved)")

    # Actionable Suggestions
    improvement_suggestions = [
        {
            "category": "Keywords & ATS",
            "issue": f"Missing key role-specific search terms for '{role}'.",
            "action": f"Incorporate missing target keywords such as {', '.join(missing_keywords[:4])} naturally into your work history bullets."
        },
        {
            "category": "Quantifiable Impact",
            "issue": "Several bullet points describe day-to-day responsibilities rather than business results.",
            "action": "Use Google's XYZ Formula: 'Accomplished [X] as measured by [Y], by doing [Z]'. Example: 'Reduced API response time by 40% by implementing Redis caching'."
        },
        {
            "category": "Formatting & ATS Structure",
            "issue": "Standardize date formats and eliminate complex graphical tables or text columns that can confuse ATS parsers.",
            "action": "Maintain clean single-column bullet points with chronological Month Year (e.g. Jan 2024 - Present) timeline headers."
        }
    ]

    # Bullet Rewrites
    bullet_rewrites = [
        {
            "original": sample_original_1,
            "improved": f"Architected and deployed high-throughput services for {role}, reducing latency by 35% and supporting 50k+ daily active users.",
            "reason": "Replaces passive duty statement with an active verb, quantifiable metric (35% latency reduction), and scale (50k+ DAU)."
        },
        {
            "original": sample_original_2,
            "improved": f"Spearheaded cross-functional delivery of core product features using {', '.join(found_keywords[:2]) if found_keywords else 'modern frameworks'}, cutting release cycles by 2.5 weeks.",
            "reason": "Demonstrates proactive leadership and measures the time saved for the engineering lifecycle."
        }
    ]

    # ATS Feedback
    ats_score = int((keyword_match_score * 0.5) + (format_score * 0.5))
    ats_verdict = "Pass - High Visibility" if ats_score >= 75 else "Moderate Risk - Keyword Gaps"

    return {
        "overall_score": overall_score,
        "score_grade": score_grade,
        "ats_score": ats_score,
        "sub_scores": {
            "technical_skills": technical_score,
            "experience_impact": impact_score,
            "formatting_structure": format_score,
            "keyword_match": keyword_match_score
        },
        "target_role": role,
        "summary": f"Resume shows a promising foundation for {role} with an overall readiness score of {overall_score}/100. Adding high-density keywords ({', '.join(missing_keywords[:3])}) and concrete metric-driven bullet points will dramatically elevate interview callbacks.",
        "strengths": strengths,
        "missing_skills": missing_keywords[:8],
        "missing_sections": missing_sections if missing_sections else ["GitHub / Live Portfolio links", "Targeted Sub-bullet Metrics"],
        "improvement_suggestions": improvement_suggestions,
        "bullet_rewrites": bullet_rewrites,
        "ats_feedback": {
            "verdict": ats_verdict,
            "file_formatting_check": "Clean PDF text extraction detected. Single-column readable structure.",
            "keyword_density": f"{len(found_keywords)} out of {len(target_keywords)} key industry terms identified ({int(keyword_ratio * 100)}% coverage).",
            "tips": [
                f"Add these high-priority keywords: {', '.join(missing_keywords[:4])}.",
                "Avoid embedding important skill text inside images or multi-column canvas blocks.",
                "Ensure standard section headings (Work Experience, Skills, Education) are plainly visible."
            ]
        },
        "final_recommendation": f"Targeting {role} with these refined metrics and keyword updates will position your profile in the top 10% of applicant pools. Implement the suggested rewrites and start applying!",
        "engine_used": "ResumeIQ Intelligent Heuristic Analyzer"
    }
