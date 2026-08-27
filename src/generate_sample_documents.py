from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "sample_documents"
OUTPUT_DIR.mkdir(exist_ok=True)

DOCUMENTS = {
    "invoice_001.txt": """
INVOICE

Vendor: Northstar Technology LLC
Invoice Number: INV-10482
Invoice Date: 2026-08-12
Due Date: 2026-09-12
Amount Due: $8,450.00

Bill To:
Atlas Medical Group

Description:
Automation consulting services and API integration support.

Payment Terms:
Net 30
""",

    "invoice_002.txt": """
INVOICE

Vendor: Blue Ridge Services
Invoice Number: INV-22107
Invoice Date: 2026-08-18
Due Date: 2026-09-17
Amount Due: $3,275.50

Bill To:
Summit Financial Partners

Description:
Monthly reporting automation and dashboard maintenance.

Payment Terms:
Net 30
""",

    "purchase_order_001.txt": """
PURCHASE ORDER

PO Number: PO-77831
Supplier: Pioneer Manufacturing
Order Date: 2026-08-14
Requested Delivery Date: 2026-09-01

Items:
25 Industrial Sensors @ $185.00 each
10 Control Modules @ $420.00 each

Total Order Value: $8,825.00

Ship To:
Northstar Logistics
Atlanta Distribution Center
""",

    "purchase_order_002.txt": """
PURCHASE ORDER

PO Number: PO-88510
Supplier: Evergreen Retail Systems
Order Date: 2026-08-20
Requested Delivery Date: 2026-09-05

Items:
50 Barcode Scanners @ $95.00 each
20 Mobile Workstations @ $310.00 each

Total Order Value: $10,950.00

Ship To:
Redwood Operations
Dallas Facility
""",

    "contract_001.txt": """
SERVICE AGREEMENT

Parties:
Vertex Technology Solutions
and
Crescent Health Services

Effective Date: 2026-09-01
Contract Term: 12 months

Scope of Services:
Vertex Technology Solutions will provide API integration,
data pipeline monitoring, and automated reporting support.

Monthly Fee: $6,500

Termination:
Either party may terminate with 30 days written notice.

Confidentiality:
Both parties agree to protect confidential business information.
""",

    "support_request_001.txt": """
SUPPORT REQUEST

Customer: Oakline Partners
Ticket Number: SUP-44218
Priority: High

Issue:
The automated financial report did not refresh this morning.
The dashboard is showing yesterday's data.

Requested Action:
Please investigate the failed refresh and restore reporting access
before the 2:00 PM executive meeting.
""",

    "support_request_002.txt": """
SUPPORT REQUEST

Customer: Atlas Medical Group
Ticket Number: SUP-55903
Priority: Medium

Issue:
Several incoming CSV files were rejected during the nightly
reporting process due to unexpected column names.

Requested Action:
Review the incoming file structure and identify which files
require correction.
""",

    "general_document_001.txt": """
INTERNAL MEMO

To: Operations Leadership
From: Business Analytics Team
Date: 2026-08-21

Subject: Weekly Reporting Process

The operations team currently spends approximately four hours
each Friday consolidating location-level spreadsheets before
leadership reporting can begin.

The team would like to evaluate automation opportunities for
file consolidation, validation, exception reporting, and KPI generation.
""",

    "ambiguous_document_001.txt": """
BUSINESS NOTICE

Reference: 2026-0824-A

Please review the attached account information and confirm whether
additional action is required before September 5.

Contact:
Jordan Lee
Operations Department
""",
}


def generate_documents():
    print("\nGenerating synthetic business documents...\n")

    for filename, content in DOCUMENTS.items():
        path = OUTPUT_DIR / filename
        path.write_text(content.strip() + "\n", encoding="utf-8")
        print(f"Created: {filename}")

    print(f"\nCreated {len(DOCUMENTS)} documents.")
    print(f"Output folder: {OUTPUT_DIR}\n")


if __name__ == "__main__":
    generate_documents()