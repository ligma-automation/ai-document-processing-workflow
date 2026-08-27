import re
import pandas as pd


# ============================================================
# HELPERS
# ============================================================

def extract_value(text, label):
    """
    Extract the value immediately following a labeled field.

    Example:
        Invoice Number: INV-10482
        -> INV-10482
    """

    pattern = rf"{re.escape(label)}\s*:\s*(.+)"

    match = re.search(
        pattern,
        str(text),
        flags=re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    return None


def clean_money(value):
    """
    Convert values such as '$8,450.00' to 8450.00.
    """

    if not value:
        return None

    cleaned = re.sub(
        r"[^\d.-]",
        "",
        str(value),
    )

    try:
        return float(cleaned)
    except ValueError:
        return None


# ============================================================
# DOCUMENT-SPECIFIC EXTRACTION
# ============================================================

def process_invoice(text):
    vendor = extract_value(text, "Vendor")
    invoice_number = extract_value(
        text,
        "Invoice Number"
    )
    invoice_date = extract_value(
        text,
        "Invoice Date"
    )
    due_date = extract_value(
        text,
        "Due Date"
    )

    amount = clean_money(
        extract_value(
            text,
            "Amount Due"
        )
    )

    summary = (
        f"Invoice {invoice_number or 'N/A'} "
        f"from {vendor or 'unknown vendor'} "
        f"for "
        f"${amount:,.2f}"
        if amount is not None
        else
        f"Invoice {invoice_number or 'N/A'} "
        f"from {vendor or 'unknown vendor'}."
    )

    return {
        "Primary_Entity": vendor,
        "Reference_Number": invoice_number,
        "Document_Date": invoice_date,
        "Due_Date": due_date,
        "Amount": amount,
        "Priority": None,
        "Summary": summary,
    }


def process_purchase_order(text):
    supplier = extract_value(
        text,
        "Supplier"
    )

    po_number = extract_value(
        text,
        "PO Number"
    )

    order_date = extract_value(
        text,
        "Order Date"
    )

    delivery_date = extract_value(
        text,
        "Requested Delivery Date"
    )

    amount = clean_money(
        extract_value(
            text,
            "Total Order Value"
        )
    )

    summary = (
        f"Purchase order {po_number or 'N/A'} "
        f"for {supplier or 'unknown supplier'} "
        f"valued at "
        f"${amount:,.2f}."
        if amount is not None
        else
        f"Purchase order {po_number or 'N/A'} "
        f"for {supplier or 'unknown supplier'}."
    )

    return {
        "Primary_Entity": supplier,
        "Reference_Number": po_number,
        "Document_Date": order_date,
        "Due_Date": delivery_date,
        "Amount": amount,
        "Priority": None,
        "Summary": summary,
    }


def process_contract(text):
    parties = []

    lines = [
        line.strip()
        for line in str(text).splitlines()
        if line.strip()
    ]

    if "Parties:" in lines:
        index = lines.index("Parties:")

        candidate_lines = lines[
            index + 1:index + 4
        ]

        for line in candidate_lines:
            if line.lower() != "and":
                parties.append(line)

    entity = (
        " / ".join(parties)
        if parties
        else None
    )

    effective_date = extract_value(
        text,
        "Effective Date"
    )

    term = extract_value(
        text,
        "Contract Term"
    )

    amount = clean_money(
        extract_value(
            text,
            "Monthly Fee"
        )
    )

    summary = (
        f"Service agreement between "
        f"{entity or 'business parties'}"
    )

    if term:
        summary += f" for {term}"

    if amount is not None:
        summary += (
            f" at ${amount:,.2f} per month"
        )

    summary += "."

    return {
        "Primary_Entity": entity,
        "Reference_Number": None,
        "Document_Date": effective_date,
        "Due_Date": None,
        "Amount": amount,
        "Priority": None,
        "Summary": summary,
    }


def process_support_request(text):
    customer = extract_value(
        text,
        "Customer"
    )

    ticket = extract_value(
        text,
        "Ticket Number"
    )

    priority = extract_value(
        text,
        "Priority"
    )

    issue_match = re.search(
        r"Issue:\s*(.*?)(?:Requested Action:|$)",
        str(text),
        flags=re.IGNORECASE | re.DOTALL,
    )

    issue = None

    if issue_match:
        issue = " ".join(
            issue_match.group(1).split()
        )

    summary = (
        f"{priority or 'Unspecified'} priority "
        f"support request from "
        f"{customer or 'unknown customer'}"
    )

    if issue:
        summary += f": {issue}"

    return {
        "Primary_Entity": customer,
        "Reference_Number": ticket,
        "Document_Date": None,
        "Due_Date": None,
        "Amount": None,
        "Priority": priority,
        "Summary": summary,
    }


def process_general_document(text):
    subject = extract_value(
        text,
        "Subject"
    )

    document_date = extract_value(
        text,
        "Date"
    )

    summary = (
        subject
        if subject
        else
        "General business document requiring review."
    )

    return {
        "Primary_Entity": None,
        "Reference_Number": None,
        "Document_Date": document_date,
        "Due_Date": None,
        "Amount": None,
        "Priority": None,
        "Summary": summary,
    }


def process_manual_review(text):
    reference = extract_value(
        text,
        "Reference"
    )

    return {
        "Primary_Entity": None,
        "Reference_Number": reference,
        "Document_Date": None,
        "Due_Date": None,
        "Amount": None,
        "Priority": None,
        "Summary":
            "Document could not be confidently classified.",
    }


# ============================================================
# PROCESS CLASSIFIED DOCUMENTS
# ============================================================

def enrich_documents(classified_df):

    results = []

    for _, row in classified_df.iterrows():

        document_type = row[
            "Document_Type"
        ]

        text = row[
            "Raw_Text"
        ]

        if document_type == "Invoice":
            extracted = process_invoice(text)

        elif document_type == "Purchase Order":
            extracted = process_purchase_order(
                text
            )

        elif document_type == "Contract":
            extracted = process_contract(text)

        elif document_type == "Support Request":
            extracted = process_support_request(
                text
            )

        elif document_type == "General Document":
            extracted = process_general_document(
                text
            )

        else:
            extracted = process_manual_review(
                text
            )

        result = {
            **row.to_dict(),
            **extracted,
        }

        results.append(result)

    return pd.DataFrame(results)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    from extract import extract_documents
    from classify import classify_documents

    documents_df, _ = extract_documents()

    classified_df = classify_documents(
        documents_df
    )

    enriched_df = enrich_documents(
        classified_df
    )

    columns = [
        "Document_Name",
        "Document_Type",
        "Primary_Entity",
        "Reference_Number",
        "Amount",
        "Priority",
        "Summary",
    ]

    print("\nDOCUMENT INTELLIGENCE\n")

    print(
        enriched_df[
            columns
        ].to_string(index=False)
    )