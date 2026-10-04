import html
import re
from typing import List


def sanitize_text(text: str) -> str:

    text = text.replace(
        "\u2018",
        "'"
    )

    text = text.replace(
        "\u2019",
        "'"
    )

    text = text.replace(
        "\u201c",
        '"'
    )

    text = text.replace(
        "\u201d",
        '"'
    )

    text = text.replace(
        "\u2013",
        "-"
    )

    text = text.replace(
        "\u2014",
        "-"
    )

    text = text.replace(
        "\u00a0",
        " "
    )

    text = re.sub(
        r"[ \t]+\n",
        "\n",
        text
    )

    text = re.sub(
        r"\n{4,}",
        "\n\n\n",
        text
    )

    return text.strip()


def split_terms(terms: str) -> List[str]:

    return [
        item.strip()
        for item in terms.split(";")
        if item.strip()
    ]


def html_preview(text: str) -> str:

    escaped = html.escape(text)

    blocks = []

    for paragraph in escaped.split("\n\n"):

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        if re.match(
            r"^(ARTICLE|SECTION|\d+[\.\)]|[A-Z][A-Z\s&-]{4,})",
            paragraph
        ):

            blocks.append(
                f"<h3>{paragraph}</h3>"
            )

        else:

            blocks.append(
                f"<p>{paragraph.replace(chr(10), '<br>')}</p>"
            )

    return "\n".join(blocks)


def safe_filename(document_type: str) -> str:

    filename = re.sub(
        r"[^A-Za-z0-9]+",
        "_",
        document_type
    )

    filename = filename.strip("_")

    if not filename:
        filename = "legal_document"

    return filename.lower()[:80]