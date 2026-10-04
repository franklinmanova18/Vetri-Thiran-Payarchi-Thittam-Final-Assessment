import os
from dataclasses import dataclass

from dotenv import load_dotenv

from utils.text_utils import sanitize_text, split_terms

load_dotenv()


@dataclass
class GenerationResult:
    text: str
    model: str
    demo_mode: bool


class GeminiDocumentGenerator:

    def __init__(self):

        self.api_key = os.getenv(
            "GEMINI_API_KEY",
            ""
        ).strip()

        default_model = "gemini-3.8-flash"
        configured_model = os.getenv(
            "LEGAL_EASE_MODEL",
            default_model
        ).strip()

        self.model = configured_model or default_model
        self.fallback_models = [
            self.model,
            "gemini-3.8-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
        ]

        # Keep a stable default while allowing the env value to be used
        # when it is valid. If a model is unavailable, the generator will
        # retry against known alternatives below.
        self.model = self.fallback_models[0]

        self.demo_mode = os.getenv(
            "DEMO_MODE",
            "false"
        ).lower() in {
            "1",
            "true",
            "yes"
        }

        if not self.api_key:
            self.demo_mode = True

    def build_prompt(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        jurisdiction: str,
        additional_instructions: str,
        include_disclaimer: bool
    ) -> str:

        term_list = "\n".join(
            f"- {term}"
            for term in split_terms(terms)
        )

        if not term_list:
            term_list = f"- {terms}"

        disclaimer_instruction = (
            "Include a short notice stating that the draft "
            "should be reviewed by a qualified legal professional "
            "before signing."
            if include_disclaimer
            else
            "Do not add a legal disclaimer."
        )

        prompt = f"""
You are LegalEase, an AI-assisted legal document drafting system.

Your task is to create a professional LEGAL DOCUMENT DRAFT.

IMPORTANT RULES:

1. Do not invent facts.
2. Do not invent laws.
3. Do not invent case citations.
4. Do not invent registration numbers.
5. Do not invent addresses.
6. Do not invent dates.
7. If information is missing, use:
   [INSERT INFORMATION]
8. Use professional legal language.
9. Make the document clearly structured.
10. Include signature sections.
11. The result must be editable plain text.
12. Do not claim that the document is legal advice.

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

EFFECTIVE DATE:
{effective_date}

JURISDICTION:
{jurisdiction or "Not specified"}

TERMS AND CONDITIONS:

{term_list}

ADDITIONAL INSTRUCTIONS:

{additional_instructions or "None"}

DOCUMENT REQUIREMENTS:

- Clear document title
- Introduction / purpose
- Parties
- Definitions when necessary
- Main clauses
- Rights and responsibilities
- Payment terms when relevant
- Confidentiality when relevant
- Term and termination
- Dispute provisions when appropriate
- Governing law only if supplied or appropriate
- Signature blocks
- Clear numbering

{disclaimer_instruction}

Return ONLY the completed document.
Do not explain your reasoning.
"""

        return prompt.strip()

    def demo_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str
    ) -> str:

        terms_list = split_terms(terms)

        formatted_terms = "\n".join(
            f"{index + 1}. {term}"
            for index, term in enumerate(terms_list)
        )

        return f"""
DRAFT {document_type.upper()}

Effective Date: {effective_date}

PARTIES

{parties}


1. PURPOSE

This draft records the principal terms supplied by the
user for a {document_type}.


2. AGREED TERMS

{formatted_terms}


3. GENERAL PROVISIONS

The parties should review all missing details,
applicable law, notice provisions and termination
provisions before signing.


SIGNATURES


Party 1

Name: ______________________________

Signature: _________________________

Date: ______________________________


Party 2

Name: ______________________________

Signature: _________________________

Date: ______________________________


LEGAL REVIEW NOTICE

This is a demonstration draft generated without
an external AI call. It is not legal advice and
should be reviewed by a qualified legal professional
before signing.
""".strip()

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        jurisdiction: str = "",
        additional_instructions: str = "",
        include_disclaimer: bool = True
    ) -> GenerationResult:

        if self.demo_mode:

            demo_text = self.demo_document(
                document_type,
                parties,
                terms,
                effective_date
            )

            return GenerationResult(
                text=sanitize_text(demo_text),
                model="demo",
                demo_mode=True
            )

        if not self.api_key:

            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Add it to .env or enable DEMO_MODE."
            )

        try:

            from google import genai

        except ImportError as exc:

            raise RuntimeError(
                "google-genai is not installed. "
                "Run pip install -r requirements.txt"
            ) from exc

        prompt = self.build_prompt(
            document_type=document_type,
            parties=parties,
            terms=terms,
            effective_date=effective_date,
            jurisdiction=jurisdiction,
            additional_instructions=additional_instructions,
            include_disclaimer=include_disclaimer
        )

        client = genai.Client(
            api_key=self.api_key
        )

        last_error = None

        for candidate_model in dict.fromkeys(self.fallback_models):
            try:
                response = client.models.generate_content(
                    model=candidate_model,
                    contents=prompt
                )
                self.model = candidate_model
                break
            except Exception as exc:
                last_error = exc
                if "404" not in str(exc) and "NOT_FOUND" not in str(exc):
                    raise RuntimeError(
                        f"Gemini API error: {exc}"
                    ) from exc
        else:
            raise RuntimeError(
                f"Gemini API error: {last_error}"
            ) from last_error

        generated_text = getattr(
            response,
            "text",
            None
        )

        if not generated_text:

            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return GenerationResult(
            text=sanitize_text(generated_text),
            model=self.model,
            demo_mode=False
        )