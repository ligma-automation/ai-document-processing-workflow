import pandas as pd


def determine_review(row):
    """
    Determine whether a document requires human review.
    Multiple reasons can trigger review.
    """

    reasons = []

    document_type = row.get("Document_Type")
    confidence = row.get("Classification_Confidence")
    reference = row.get("Reference_Number")
    entity = row.get("Primary_Entity")
    amount = row.get("Amount")
    priority = row.get("Priority")

    # Low-confidence classification
    if confidence == "Low":
        reasons.append("Low classification confidence")

    # Anything already routed to Manual Review
    if row.get("Route_To") == "Manual Review":
        reasons.append("Document routed to manual review")

    # Important identifying fields missing
    if document_type in ["Invoice", "Purchase Order"]:
        if pd.isna(reference) or not str(reference).strip():
            reasons.append("Missing reference number")

        if pd.isna(entity) or not str(entity).strip():
            reasons.append("Missing vendor/supplier")

        if pd.isna(amount):
            reasons.append("Missing monetary amount")

    # Large financial transactions
    if document_type in ["Invoice", "Purchase Order"]:
        if pd.notna(amount) and amount >= 10000:
            reasons.append("Amount requires manager approval")

    # Contracts require human/legal review
    if document_type == "Contract":
        reasons.append("Contract requires legal review")

    # High-priority support requests
    if document_type == "Support Request":
        if str(priority).lower() == "high":
            reasons.append("High-priority support request")

    review_required = "Yes" if reasons else "No"

    return {
        "Review_Required": review_required,
        "Review_Reason": (
            "; ".join(dict.fromkeys(reasons))
            if reasons
            else "No manual review required"
        ),
    }


def apply_review_rules(routed_df):
    results = []

    for _, row in routed_df.iterrows():

        review = determine_review(row)

        results.append(
            {
                **row.to_dict(),
                **review,
            }
        )

    return pd.DataFrame(results)


if __name__ == "__main__":

    from extract import extract_documents
    from classify import classify_documents
    from summarize import enrich_documents
    from route import route_documents

    documents_df, _ = extract_documents()

    classified_df = classify_documents(documents_df)

    enriched_df = enrich_documents(classified_df)

    routed_df = route_documents(enriched_df)

    reviewed_df = apply_review_rules(routed_df)

    columns = [
        "Document_Name",
        "Document_Type",
        "Classification_Confidence",
        "Route_To",
        "Review_Required",
        "Review_Reason",
    ]

    print("\nHUMAN REVIEW QUEUE\n")

    print(
        reviewed_df[
            columns
        ].to_string(index=False)
    )

    print(
        "\nDocuments requiring review:",
        (reviewed_df["Review_Required"] == "Yes").sum()
    )