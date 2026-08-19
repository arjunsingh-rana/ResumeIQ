"""
PDF extraction service for ResumeIQ.
Extracts raw text, structural sections, contact info, and metrics from PDF resumes.
"""
import io
import re
from typing import Dict, Any, List, Optional
from pypdf import PdfReader


COMMON_SECTIONS = [
    "experience", "work experience", "employment history", "professional experience",
    "education", "academic background", "qualifications",
    "skills", "technical skills", "core competencies", "technologies",
    "projects", "personal projects", "key projects",
    "certifications", "licenses", "courses",
    "summary", "professional summary", "about me", "objective",
    "achievements", "awards", "honors",
    "publications", "volunteer", "languages"
]


def extract_text_from_pdf(file_source: Any) -> Dict[str, Any]:
    """
    Extracts text and key resume metadata from a PDF file (stream, bytes, or file path).
    
    Returns:
        Dict containing:
            - text: Full raw text extracted
            - page_count: Number of pages
            - word_count: Total word count
            - detected_sections: List of sections found
            - detected_email: Extracted candidate email if present
            - detected_phone: Extracted candidate phone if present
            - preview_snippet: First 300 characters
    """
    try:
        if isinstance(file_source, bytes):
            reader = PdfReader(io.BytesIO(file_source))
        elif hasattr(file_source, "read"):
            # File-like object (e.g. from Flask request.files['file'])
            content = file_source.read()
            # Reset seek if possible
            if hasattr(file_source, "seek"):
                file_source.seek(0)
            reader = PdfReader(io.BytesIO(content))
        elif isinstance(file_source, str):
            reader = PdfReader(file_source)
        else:
            raise ValueError("Unsupported file source format for PDF extraction.")

        page_texts = []
        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            page_texts.append(page_text)

        full_text = "\n\n".join(page_texts).strip()

        # Clean text
        cleaned_text = re.sub(r'[ \t]+', ' ', full_text)
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)

        word_count = len(cleaned_text.split())
        page_count = len(reader.pages)

        # Detect Sections
        detected_sections = _detect_sections(cleaned_text)

        # Detect Email
        email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', cleaned_text)
        detected_email = email_match.group(0) if email_match else None

        # Detect Phone
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', cleaned_text)
        detected_phone = phone_match.group(0) if phone_match else None

        return {
            "success": True,
            "text": cleaned_text,
            "page_count": page_count,
            "word_count": word_count,
            "detected_sections": detected_sections,
            "detected_email": detected_email,
            "detected_phone": detected_phone,
            "preview_snippet": cleaned_text[:300].strip() + ("..." if len(cleaned_text) > 300 else ""),
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "text": "",
            "page_count": 0,
            "word_count": 0,
            "detected_sections": [],
            "detected_email": None,
            "detected_phone": None,
            "preview_snippet": "",
            "error": f"Failed to extract PDF content: {str(e)}"
        }


def _detect_sections(text: str) -> List[str]:
    """Identifies standard resume section headers present in the text."""
    lower_text = text.lower()
    found = []
    for section in COMMON_SECTIONS:
        # Check for section header patterns (e.g., at line start or surrounded by newlines/colons)
        pattern = rf'(?:^|\n)\s*{re.escape(section)}\s*(?::|\n|$)'
        if re.search(pattern, lower_text):
            found.append(section.title())
        elif section in lower_text and section.title() not in found:
            # Secondary check for prominent keyword
            if len(section) > 5 and f"\n{section}" in lower_text:
                found.append(section.title())
    return list(dict.fromkeys(found))[:8]
