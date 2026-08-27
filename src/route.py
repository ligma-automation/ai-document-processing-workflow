import pandas as pd


def determine_route(row):
    """
    Determine the recommended business destination
    for a processed document.
    """

    document_type = row.get("Document_Type")
    confidence = row.get("Classification_Confidence")
    priority = row.get("Priority")
    amount = row.get("Amount")

    # Low-confidence documents always go to manual review
    if confidence == "Low":
        return {
            "Route_To": "Manual Review",
            "Routing_Reason": "Low classification confidence.",
        }

    # Invoices
    if document_type == "Invoice":

        if pd.notna(amount) and amount >= 10000:
            return {
                "Route_To": "Accounts Payable + Manager Approval",
                "Routing_Reason":
                    "Invoice requires additional approval due to amount.",
            }

        return {
            "Route_To": "Accounts Payable",
            "Routing_Reason":
                "Invoice routed to Accounts Payable.",
        }

    # Purchase Orders
    if document_type == "Purchase Order":

        if pd.notna(amount) and amount >= 10000:
            return {
                "Route_To": "Procurement + Manager Approval",
                "Routing_Reason":
                    "Purchase order exceeds approval threshold.",
            }

        return {
            "Route_To": "Procurement",
            "Routing_Reason":
                "Purchase order routed to Procurement.",
        }

    # Contracts
    if document_type == "Contract":
        return {
            "Route_To": "Legal / Contract Management",
            "Routing_Reason":
                "Contract requires legal and contract review.",
        }

    # Support Requests
    if document_type == "Support Request":

        if str(priority).lower() == "high":
            return {
                "Route_To": "Priority Support Queue",
                "Routing_Reason":
                    "High-priority support request.",
            }

        return {
            "Route_To": "Support Operations",
            "Routing_Reason":
                "Support request routed to standard support queue.",
        }

    # General business documents
    if document_type == "General Document":
        return {
            "Route_To": "Operations",
            "Routing_Reason":
                "General business document routed to Operations.",
        }

    return {
        "Route_To": "Manual Review",
        "Routing_Reason":
            "No routing rule matched the document.",
    }


def route_documents(enriched_df):
    results = []

    for _, row in enriched_df.iterrows():

        routing = determine_route(row)

        result = {
            **row.to_dict(),
            **routing,
        }

        results.append(result)

    return pd.DataFrame(results)


if __name__ == "__main__":

    from extract import extract_documents
    from classify import classify_documents
    from summarize import enrich_documents

    documents_df, _ = extract_documents()

    classified_df = classify_documents(
        documents_df
    )

    enriched_df = enrich_documents(
        classified_df
    )

    routed_df = route_documents(
        enriched_df
    )

    columns = [
        "Document_Name",
        "Document_Type",
        "Classification_Confidence",
        "Amount",
        "Priority",
        "Route_To",
        "Routing_Reason",
    ]

    print("\nDOCUMENT ROUTING\n")

    print(
        routed_df[
            columns
        ].to_string(index=False)
    )