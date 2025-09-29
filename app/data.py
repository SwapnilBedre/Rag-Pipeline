"""
generate_healthcare_pdfs.py

Generates synthetic healthcare PDFs suitable for RAG projects:
- Configurable number of PDFs (default 500)
- Each PDF contains at least WORDS_PER_PDF words (default 10_000)
- Each PDF mixes: research-style sections, thesis/whitepaper text, synthetic FHIR patient records,
  case studies, methods, discussion, and references.

Dependencies:
  pip install faker reportlab tqdm

Use responsibly — this contains only synthetic data.
"""

import os
import uuid
import json
import random
import math
from faker import Faker
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from tqdm import tqdm

fake = Faker()
Faker.seed(42)
random.seed(42)

# ---------- Configuration ----------
NUM_PDFS = 500           # Set lower for testing (e.g., 5)
WORDS_PER_PDF = 10000    # Minimum words per PDF (target)
OUTPUT_DIR = "synthetic_healthcare_pdfs"
PROGRESS_BATCH_SAVE = 1  # save every PDF
# -----------------------------------

# Create output dir
os.makedirs(OUTPUT_DIR, exist_ok=True)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='SectionTitle', fontSize=14, leading=18, spaceAfter=8, spaceBefore=10))
styles.add(ParagraphStyle(name='MyBodyText', fontSize=11, leading=14))
styles.add(ParagraphStyle(name='MyCode', fontName='Courier', fontSize=8, leading=10))

# Small helper functions
def word_count(text: str) -> int:
    return len(text.split())

def generate_research_title():
    topics = [
        "AI and Clinical Decision Support",
        "Telemedicine in Rural Healthcare",
        "Precision Medicine and Genomic Data",
        "Interoperability of EHR Systems",
        "FHIR Implementation Case Study",
        "Natural Language Processing for Clinical Notes",
        "Healthcare Cost Optimization via Data Analytics",
        "Machine Learning for Patient Risk Stratification",
        "Digital Therapeutics and Outcomes",
        "IoT and Remote Monitoring in Chronic Disease"
    ]
    return f"{random.choice(topics)}: A Synthetic Review"

def generate_abstract(min_words=200):
    sentences = []
    while word_count(" ".join(sentences)) < min_words:
        sentences.append(fake.paragraph(nb_sentences=3))
    return " ".join(sentences)

def generate_section(title, min_words=800):
    text = f"<b>{title}</b><br/>"
    body = []
    while word_count(" ".join(body)) < min_words:
        # Mix in paragraphs, lists and small bullet-like paragraphs
        p = fake.paragraph(nb_sentences=random.randint(3,7))
        body.append(p)
    return text + "<br/>".join(body)

def generate_fhir_patient_record():
    # Generate synthetic FHIR-like JSON for patient (no real PHI)
    patient_id = str(uuid.uuid4())
    pat = {
        "resourceType": "Patient",
        "id": patient_id,
        "identifier": [{"system": "urn:synthetic-hospital", "value": fake.bothify(text='??-#####')}],
        "name": [{"use": "official", "family": fake.last_name(), "given": [fake.first_name()]}],
        "gender": random.choice(["male", "female", "other", "unknown"]),
        "birthDate": fake.date_of_birth(minimum_age=0, maximum_age=100).isoformat(),
        "address": [{
            "line": [fake.street_address()],
            "city": fake.city(),
            "state": fake.state(),
            "postalCode": fake.postcode(),
            "country": fake.country()
        }],
        "telecom": [{"system": "phone", "value": fake.phone_number()}],
    }

    # Add conditions, medications and encounters
    conditions = []
    meds = []
    for _ in range(random.randint(0, 4)):
        cond = {
            "id": str(uuid.uuid4()),
            "clinicalStatus": "active",
            "MyCode": {"text": random.choice([
                "Hypertension", "Type 2 Diabetes Mellitus", "Asthma", "COPD", "Chronic Kidney Disease",
                "Coronary Artery Disease", "Hypothyroidism", "Anxiety Disorder", "Depression"
            ])},
            "onsetDateTime": fake.date_between(start_date='-10y', end_date='today').isoformat()
        }
        conditions.append(cond)

    for _ in range(random.randint(0, 4)):
        med = {
            "id": str(uuid.uuid4()),
            "medicationCodeableConcept": {"text": random.choice([
                "Metformin 500mg", "Amlodipine 5mg", "Salbutamol inhaler", "Atorvastatin 20mg", "Levothyroxine 50mcg"
            ])},
            "dosage": {"text": random.choice(["Once daily", "Twice daily", "As needed", "At bedtime"])}
        }
        meds.append(med)

    encounter = {
        "resourceType": "Encounter",
        "id": str(uuid.uuid4()),
        "status": "finished",
        "class": {"code": "OUTPATIENT"},
        "period": {"start": fake.date_between(start_date='-2y', end_date='today').isoformat()}
    }

    bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {"resource": pat},
            *[{"resource": c} for c in conditions],
            *[{"resource": m} for m in meds],
            {"resource": encounter}
        ]
    }
    # Return as pretty JSON string
    return json.dumps(bundle, indent=2)

def generate_references(num=8):
    refs = []
    for i in range(num):
        author = f"{fake.last_name()}, {fake.first_name()[0]}."
        year = random.randint(2005, 2025)
        title = fake.sentence(nb_words=random.randint(4,10)).rstrip('.')
        journal = random.choice([
            "Journal of Synthetic Medicine", "International Journal of Health Informatics",
            "Proceedings of Clinical Data Science", "Healthcare Systems Review"
        ])
        refs.append(f"{author} ({year}). {title}. {journal}.")
    return "<br/>".join(refs)

def assemble_document(target_words):
    # Build parts until target word count reached
    parts = []

    # Title and author block
    title = generate_research_title()
    author_line = f"Author: {fake.name()}, {fake.job()}<br/>Affiliation: {fake.company()}<br/>"
    parts.append(f"<b><font size=16>{title}</font></b><br/>{author_line}")

    # Abstract
    parts.append(f"<b>Abstract</b><br/>{generate_abstract(min_words=250)}")

    # Introduction
    parts.append(generate_section("Introduction", min_words=700))

    # Literature review + multiple mini-reviews
    for _ in range(3):
        parts.append(generate_section("Literature Review", min_words=600))

    # Methods
    parts.append(generate_section("Methods", min_words=700))

    # Synthetic FHIR patient block(s)
    fhir_count = random.randint(1, 4)
    fhir_blocks = []
    for _ in range(fhir_count):
        fhir_blocks.append(generate_fhir_patient_record())
    fhir_text = "<b>Example Synthetic FHIR Records</b><br/><pre>" + "\n\n".join(fhir_blocks) + "</pre>"
    parts.append(fhir_text)

    # Case study
    parts.append(generate_section("Case Study", min_words=900))

    # Results & Discussion
    parts.append(generate_section("Results", min_words=700))
    parts.append(generate_section("Discussion", min_words=700))

    # Conclusion
    parts.append(generate_section("Conclusion", min_words=300))

    # References
    parts.append("<b>References</b><br/>" + generate_references(num=12))

    # Stitch until target_words met (if still short, add more paragraphs)
    current_text = "\n\n".join(parts)
    while word_count(current_text) < target_words:
        # Append additional synthetic paragraphs and small sub-sections
        extra = fake.paragraph(nb_sentences=random.randint(4,8))
        current_text += "\n\n" + extra

        # Occasionally add a small FHIR snippet to increase realism
        if random.random() < 0.05:
            current_text += "\n\n" + "<pre>" + generate_fhir_patient_record() + "</pre>"

    return current_text

def create_pdf_from_text(filename, full_text):
    # Use ReportLab Platypus to create PDF with paragraphs
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=30, leftMargin=30,
                            topMargin=30, bottomMargin=18)
    story = []

    # Basic split by two newlines to paragraphs
    paragraphs = full_text.split("\n\n")
    for p in paragraphs:
        # Avoid extremely long lines for paragraphs like JSON blocks: use monospace style
        if p.strip().startswith("{") or p.strip().startswith("[") or p.strip().startswith("<pre>"):
            # place as code-style paragraph
            # Remove <pre> if present and keep JSON block
            cleaned = p.replace("<pre>", "").replace("</pre>", "")
            # Wrap code block into multiple small paragraphs to avoid PDF rendering issues
            lines = cleaned.splitlines()
            # Add a small title if it's a JSON block
            story.append(Paragraph("<b>FHIR / JSON snippet</b>", styles['SectionTitle']))
            for ln in lines:
                if ln.strip() == "":
                    story.append(Spacer(1, 2*mm))
                else:
                    # we use <font face="Courier"> for monospace in reportlab's para
                    safe_ln = ln.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    story.append(Paragraph(f'<font face="Courier" size="8">{safe_ln}</font>', styles['MyBodyText']))
            story.append(Spacer(1, 4*mm))
        else:
            # Clean html-like tags (we used <b> and <br/> earlier). Replace <br/> with line breaks.
            p_fixed = p.replace("<br/>", "<br/>")
            story.append(Paragraph(p_fixed, styles['MyBodyText']))
            story.append(Spacer(1, 4*mm))

        # Limit story length to avoid memory blowup; flush page breaks occasionally
        if len(story) > 200:
            story.append(PageBreak())

    doc.build(story)

def main():
    print(f"Configuration: NUM_PDFS={NUM_PDFS}, WORDS_PER_PDF={WORDS_PER_PDF}, OUTPUT_DIR='{OUTPUT_DIR}'")
    # Quick sanity check
    if NUM_PDFS > 2000:
        print("Warning: Very large number of PDFs requested. Ensure you have disk space and time.")
    est_words = NUM_PDFS * WORDS_PER_PDF
    print(f"Estimated total words: {est_words:,}")

    for i in tqdm(range(1, NUM_PDFS + 1), desc="Generating PDFs"):
        filename = os.path.join(OUTPUT_DIR, f"synthetic_healthcare_{i:04d}.pdf")
        # Build document content
        doc_text = assemble_document(WORDS_PER_PDF)

        # Create PDF file
        create_pdf_from_text(filename, doc_text)

        # Optionally check actual word count
        wc = word_count(doc_text)
        if wc < WORDS_PER_PDF:
            print(f"NOTE: Generated file {filename} only has {wc} words (target {WORDS_PER_PDF}).")
        # Save every PROGRESS_BATCH_SAVE
        if i % PROGRESS_BATCH_SAVE == 0:
            pass  # Could flush or print intermediate logs

    print("Done. All PDFs written to:", OUTPUT_DIR)
    total_files = len([f for f in os.listdir(OUTPUT_DIR) if f.endswith(".pdf")])
    print(f"Total PDF files in '{OUTPUT_DIR}': {total_files}")

if __name__ == "__main__":
    main()
