import re
import pandas as pd


DOCUMENT_TYPES = [
    "Invoice",
    "Purchase Order",
    "Contract",
    "Support Request",
    "General Document",
    "Manual Review",
]


def normalize_text(text):
    if pd.isna(text):
        return ""
    return str(text).lower().strip()


def classify_document(text):
    """
    Classify a document using keyword-based business rules.

    Returns:
        document_type
        confidence
        reason
    """

    text_lower = normalize_text(text)

    scores = {
        "Invoice": 0,
        "Purchase Order": 0,
        "Contract": 0,
        "Support Request": 0,
        "General Document": 0,
    }

    # -----------------------------
    # Invoice signals
    # -----------------------------
    invoice_keywords = [
        "invoice number",
        "amount due",
        "payment terms",
        "bill to",
        "invoice date",
    ]

    for keyword in invoice_keywords:
        if keyword in text_lower:
            scores["Invoice"] += 1

    # -----------------------------
    # Purchase Order signals
    # -----------------------------
    po_keywords = [
        "purchase order",
        "po number",
        "supplier",
        "requested delivery date",
        "total order value",
        "ship to",
    ]

    for keyword in po_keywords:
        if keyword in text_lower:
            scores["Purchase Order"] += 1

    # -----------------------------
    # Contract signals
    # -----------------------------
    contract_keywords = [
        "service agreement",
        "effective date",
        "contract term",
        "scope of services",
        "termination",
        "confidentiality",
    ]

    for keyword in contract_keywords:
        if keyword in text_lower:
            scores["Contract"] += 1

    # -----------------------------
    # Support Request signals
    # -----------------------------
    support_keywords = [
        "support request",
        "ticket number",
        "priority",
        "issue:",
        "requested action",
    ]

    for keyword in support_keywords:
        if keyword in text_lower:
            scores["Support Request"] += 1

    # -----------------------------
    # General document signals
    # -----------------------------
    general_keywords = [
        "internal memo",
        "subject:",
        "operations",
        "leadership",
        "business analytics",
    ]

    for keyword in general_keywords:
        if keyword in text_lower:
            scores["General Document"] += 1

    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]

    # -----------------------------
    # Confidence logic
    # -----------------------------
    if best_score >= 4:
        confidence = "High"

    elif best_score >= 2:
        confidence = "Medium"

    else:
        return (
            "Manual Review",
            "Low",
            "Document did not contain enough reliable classification signals.",
        )

    reason = (
        f"Matched {best_score} classification signals "
        f"for {best_type}."
    )

    return best_type, confidence, reason


def classify_documents(documents_df):
    results = []

    for _, row in documents_df.iterrows():

        document_type, confidence, reason = classify_document(
            row["Raw_Text"]
        )

        results.append(
            {
                **row.to_dict(),
                "Document_Type": document_type,
                "Classification_Confidence": confidence,
                "Classification_Reason": reason,
            }
        )

    return pd.DataFrame(results)


if __name__ == "__main__":

    from extract import extract_documents

    documents_df, _ = extract_documents()

    classified_df = classify_documents(documents_df)

    print(
        classified_df[
            [
                "Document_Name",
                "Document_Type",
                "Classification_Confidence",
            ]
        ].to_string(index=False)
    )