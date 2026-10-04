import base64
import os

import requests
import streamlit as st

from dotenv import load_dotenv

from utils.text_utils import (
    html_preview,
    safe_filename
)


load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide"
)


st.markdown(
    """
    <style>

    .hero {
        padding: 25px;
        border-radius: 18px;
        background:
            linear-gradient(
                135deg,
                #111827,
                #1f2937
            );
        color: white;
        margin-bottom: 20px;
    }

    .hero h1 {
        margin: 0;
    }

    .preview {
        background: #111827;
        color: #f9fafb;
        border-radius: 14px;
        padding: 25px;
        max-height: 650px;
        overflow-y: auto;
        line-height: 1.7;
    }

    .preview h3 {
        color: #fbbf24;
    }

    .notice {
        padding: 15px;
        border-radius: 10px;
        background: #fff7ed;
        border: 1px solid #fed7aa;
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="hero">

        <h1>⚖️ LegalEase</h1>

        <p>
        AI-Powered Legal Document Generator
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="notice">

    ⚠️ LegalEase creates AI-assisted drafts.
    Please review the document with a qualified
    legal professional before signing.

    </div>
    """,
    unsafe_allow_html=True
)


if "content" not in st.session_state:

    st.session_state.content = ""


if "model" not in st.session_state:

    st.session_state.model = ""


if "demo_mode" not in st.session_state:

    st.session_state.demo_mode = False


left, right = st.columns(
    [0.9, 1.1],
    gap="large"
)


# =====================================================
# LEFT SIDE
# =====================================================

with left:

    st.subheader(
        "📄 Document Details"
    )

    document_type = st.selectbox(
        "Document Type",
        [
            "Employment Contract",
            "Non-Disclosure Agreement",
            "Lease Agreement",
            "Employment Offer Letter",
            "Freelance Work Contract",
            "Service Agreement",
            "Partnership Agreement",
            "General Agreement",
            "Custom Legal Document"
        ]
    )


    parties = st.text_area(
        "Parties Involved",
        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),
        height=100
    )


    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Payment within 30 days; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),
        height=160
    )


    st.caption(
        "Separate different clauses using semicolons (;)"
    )


    effective_date = st.text_input(
        "Effective Date",
        placeholder="October 1, 2026"
    )


    jurisdiction = st.text_input(
        "Jurisdiction",
        placeholder="Tamil Nadu, India"
    )


    additional_instructions = st.text_area(
        "Additional Instructions",
        placeholder=(
            "Use clear professional language "
            "and include signature blocks."
        ),
        height=100
    )


    include_disclaimer = st.checkbox(
        "Include legal-review notice",
        value=True
    )


    logo_file = st.file_uploader(
        "Upload Logo (Optional)",
        type=[
            "png",
            "jpg",
            "jpeg"
        ]
    )


    logo_base64 = None


    if logo_file:

        raw_logo = (
            logo_file.getvalue()
        )

        if len(raw_logo) > 2 * 1024 * 1024:

            st.error(
                "Logo must be smaller than 2 MB."
            )

        else:

            logo_base64 = (
                "data:image/png;base64,"
                + base64.b64encode(
                    raw_logo
                ).decode()
            )


    # =================================================
    # GENERATE
    # =================================================

    if st.button(
        "✨ Generate Document",
        type="primary",
        use_container_width=True
    ):

        missing = []

        if not parties.strip():

            missing.append(
                "Parties"
            )

        if not terms.strip():

            missing.append(
                "Terms"
            )

        if not effective_date.strip():

            missing.append(
                "Effective Date"
            )


        if missing:

            st.error(
                "Please enter: "
                + ", ".join(missing)
            )

        else:

            payload = {

                "document_type":
                    document_type,

                "parties":
                    parties,

                "terms":
                    terms,

                "effective_date":
                    effective_date,

                "jurisdiction":
                    jurisdiction,

                "additional_instructions":
                    additional_instructions,

                "include_disclaimer":
                    include_disclaimer,

                "logo_base64":
                    logo_base64
            }


            with st.spinner(
                "🤖 Generating legal document..."
            ):

                try:

                    response = requests.post(
                        f"{BACKEND_URL}/api/generate",
                        json=payload,
                        timeout=120
                    )


                    response.raise_for_status()


                    data = (
                        response.json()
                    )


                    st.session_state.content = (
                        data["content"]
                    )


                    st.session_state.model = (
                        data["model"]
                    )


                    st.session_state.demo_mode = (
                        data["demo_mode"]
                    )


                    st.success(
                        "Document generated successfully!"
                    )


                except requests.RequestException as exc:

                    st.error(
                        "Unable to connect to FastAPI backend."
                    )

                    st.code(
                        str(exc)
                    )


# =====================================================
# RIGHT SIDE
# =====================================================

with right:

    st.subheader(
        "✏️ Preview & Edit"
    )


    if st.session_state.content:

        if st.session_state.demo_mode:

            st.warning(
                "Demo Mode is active. "
                "Gemini was not called."
            )


        st.caption(
            f"AI Model: {st.session_state.model}"
        )


        edited_content = st.text_area(
            "Editable Document",
            value=st.session_state.content,
            height=450
        )


        st.session_state.content = (
            edited_content
        )


        st.markdown(
            "### 👁️ Styled Preview"
        )


        preview = html_preview(
            st.session_state.content
        )


        st.markdown(
            f"""
            <div class="preview">

            {preview}

            </div>
            """,
            unsafe_allow_html=True
        )


        st.divider()


        st.subheader(
            "⬇️ Download"
        )


        filename = safe_filename(
            document_type
        )


        # =================================================
        # TXT
        # =================================================

        st.download_button(
            "⬇️ Download TXT",
            data=st.session_state.content.encode(
                "utf-8"
            ),
            file_name=f"{filename}.txt",
            mime="text/plain",
            use_container_width=True
        )


        export_payload = {

            "content":
                st.session_state.content,

            "document_type":
                document_type,

            "logo_base64":
                logo_base64
        }


        # =================================================
        # DOCX
        # =================================================

        if st.button(
            "📘 Create DOCX",
            use_container_width=True
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/api/export/docx",
                    json=export_payload,
                    timeout=60
                )

                response.raise_for_status()


                st.download_button(
                    "💾 Save DOCX",
                    data=response.content,
                    file_name=f"{filename}.docx",
                    mime=(
                        "application/vnd.openxmlformats-"
                        "officedocument.wordprocessingml.document"
                    ),
                    use_container_width=True
                )


            except requests.RequestException as exc:

                st.error(
                    f"DOCX export failed: {exc}"
                )


        # =================================================
        # PDF
        # =================================================

        if st.button(
            "📕 Create PDF",
            use_container_width=True
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/api/export/pdf",
                    json=export_payload,
                    timeout=60
                )

                response.raise_for_status()


                st.download_button(
                    "💾 Save PDF",
                    data=response.content,
                    file_name=f"{filename}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )


            except requests.RequestException as exc:

                st.error(
                    f"PDF export failed: {exc}"
                )

    else:

        st.info(
            "Your generated document will appear here."
        )


st.divider()


st.caption(
    "LegalEase — AI-assisted legal document drafting."
)