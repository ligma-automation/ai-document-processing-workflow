from pathlib import Path
from datetime import datetime

import pandas as pd

from extract import extract_documents
from classify import classify_documents
from summarize import enrich_documents
from route import route_documents
from review import apply_review_rules


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output_examples"

OUTPUT_DIR.mkdir(exist_ok=True)

EXCEL_OUTPUT = OUTPUT_DIR / "Document_Processing_Report.xlsx"
CSV_OUTPUT = OUTPUT_DIR / "Processed_Documents.csv"
REVIEW_OUTPUT = OUTPUT_DIR / "Human_Review_Queue.csv"


# ============================================================
# REPORTING
# ============================================================

def create_excel_report(processed_df, processing_log):
    """
    Create a polished Excel workbook containing:
    - Executive Summary
    - Processed Documents
    - Human Review Queue
    - Routing Summary
    - Processing Log
    """

    review_df = processed_df[
        processed_df["Review_Required"] == "Yes"
    ].copy()

    routing_summary = (
        processed_df
        .groupby("Route_To", dropna=False)
        .size()
        .reset_index(name="Document_Count")
        .sort_values("Document_Count", ascending=False)
    )

    type_summary = (
        processed_df
        .groupby("Document_Type", dropna=False)
        .size()
        .reset_index(name="Document_Count")
        .sort_values("Document_Count", ascending=False)
    )

    with pd.ExcelWriter(
        EXCEL_OUTPUT,
        engine="xlsxwriter"
    ) as writer:

        workbook = writer.book

        # ----------------------------------------------------
        # Formats
        # ----------------------------------------------------

        title_format = workbook.add_format({
            "bold": True,
            "font_size": 20,
            "font_color": "#FFFFFF",
            "bg_color": "#0F3D2E",
            "align": "left",
            "valign": "vcenter",
        })

        subtitle_format = workbook.add_format({
            "font_size": 10,
            "font_color": "#666666",
        })

        section_format = workbook.add_format({
            "bold": True,
            "font_size": 12,
            "font_color": "#FFFFFF",
            "bg_color": "#1F2937",
        })

        kpi_label_format = workbook.add_format({
            "bold": True,
            "font_color": "#666666",
            "align": "center",
        })

        kpi_value_format = workbook.add_format({
            "bold": True,
            "font_size": 18,
            "font_color": "#0F3D2E",
            "align": "center",
        })

        header_format = workbook.add_format({
            "bold": True,
            "font_color": "#FFFFFF",
            "bg_color": "#0F3D2E",
            "border": 0,
        })

        wrap_format = workbook.add_format({
            "text_wrap": True,
            "valign": "top",
        })

        # ----------------------------------------------------
        # Executive Summary
        # ----------------------------------------------------

        summary_sheet = workbook.add_worksheet(
            "Executive Summary"
        )

        writer.sheets[
            "Executive Summary"
        ] = summary_sheet

        summary_sheet.hide_gridlines(2)

        summary_sheet.set_column("A:A", 3)
        summary_sheet.set_column("B:B", 24)
        summary_sheet.set_column("C:C", 18)
        summary_sheet.set_column("D:D", 4)
        summary_sheet.set_column("E:E", 28)
        summary_sheet.set_column("F:F", 18)

        summary_sheet.merge_range(
            "B2:F3",
            "AI Document Processing Workflow",
            title_format,
        )

        summary_sheet.write(
            "B4",
            "Automated classification, extraction, routing, and human-review controls",
            subtitle_format,
        )

        total_documents = len(processed_df)

        review_count = (
            processed_df["Review_Required"]
            .eq("Yes")
            .sum()
        )

        auto_processed = total_documents - review_count

        high_confidence = (
            processed_df[
                "Classification_Confidence"
            ]
            .eq("High")
            .sum()
        )

        kpis = [
            ("Documents Processed", total_documents),
            ("Auto-Processed", auto_processed),
            ("Human Review", review_count),
            ("High Confidence", high_confidence),
        ]

        columns = ["B", "C", "E", "F"]

        for column, (label, value) in zip(
            columns,
            kpis,
        ):
            summary_sheet.write(
                f"{column}6",
                label,
                kpi_label_format,
            )

            summary_sheet.write(
                f"{column}7",
                int(value),
                kpi_value_format,
            )

        # Document type summary
        summary_sheet.merge_range(
            "B10:C10",
            "Document Classification",
            section_format,
        )

        summary_sheet.write(
            "B11",
            "Document Type",
            header_format,
        )

        summary_sheet.write(
            "C11",
            "Count",
            header_format,
        )

        row_num = 11

        for _, row in type_summary.iterrows():

            summary_sheet.write(
                row_num,
                1,
                row["Document_Type"],
            )

            summary_sheet.write(
                row_num,
                2,
                int(row["Document_Count"]),
            )

            row_num += 1

        # Routing summary
        summary_sheet.merge_range(
            "E10:F10",
            "Routing Distribution",
            section_format,
        )

        summary_sheet.write(
            "E11",
            "Destination",
            header_format,
        )

        summary_sheet.write(
            "F11",
            "Count",
            header_format,
        )

        row_num = 11

        for _, row in routing_summary.iterrows():

            summary_sheet.write(
                row_num,
                4,
                row["Route_To"],
            )

            summary_sheet.write(
                row_num,
                5,
                int(row["Document_Count"]),
            )

            row_num += 1

        # ----------------------------------------------------
        # Other sheets
        # ----------------------------------------------------

        processed_export = processed_df.drop(
            columns=["Raw_Text"],
            errors="ignore",
        )

        processed_export.to_excel(
            writer,
            sheet_name="Processed Documents",
            index=False,
        )

        review_export = review_df.drop(
            columns=["Raw_Text"],
            errors="ignore",
        )

        review_export.to_excel(
            writer,
            sheet_name="Human Review Queue",
            index=False,
        )

        routing_summary.to_excel(
            writer,
            sheet_name="Routing Summary",
            index=False,
        )

        processing_log.to_excel(
            writer,
            sheet_name="Processing Log",
            index=False,
        )

        # ----------------------------------------------------
        # Format exported sheets
        # ----------------------------------------------------

        for sheet_name in [
            "Processed Documents",
            "Human Review Queue",
            "Routing Summary",
            "Processing Log",
        ]:

            worksheet = writer.sheets[
                sheet_name
            ]

            worksheet.hide_gridlines(2)
            worksheet.freeze_panes(1, 0)

            dataframe = {
                "Processed Documents":
                    processed_export,

                "Human Review Queue":
                    review_export,

                "Routing Summary":
                    routing_summary,

                "Processing Log":
                    processing_log,

            }[sheet_name]

            for col_num, column in enumerate(
                dataframe.columns
            ):

                worksheet.write(
                    0,
                    col_num,
                    column,
                    header_format,
                )

                max_length = max(
                    len(str(column)),
                    dataframe[column]
                    .astype(str)
                    .map(len)
                    .max()
                    if len(dataframe)
                    else 0,
                )

                width = min(
                    max(max_length + 2, 12),
                    45,
                )

                worksheet.set_column(
                    col_num,
                    col_num,
                    width,
                    wrap_format,
                )

    return EXCEL_OUTPUT


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    print(
        "\n"
        "=============================================="
    )

    print(
        "LIGNUM AUTOMATION - AI DOCUMENT WORKFLOW"
    )

    print(
        "==============================================\n"
    )

    # 1. Extraction
    print("1. Loading documents...")

    documents_df, processing_log = (
        extract_documents()
    )

    print(
        f"   Documents loaded: "
        f"{len(documents_df)}"
    )

    # 2. Classification
    print("\n2. Classifying documents...")

    classified_df = classify_documents(
        documents_df
    )

    print(
        "   Classification complete."
    )

    # 3. Intelligence extraction
    print(
        "\n3. Extracting business information..."
    )

    enriched_df = enrich_documents(
        classified_df
    )

    print(
        "   Key fields and summaries created."
    )

    # 4. Routing
    print("\n4. Applying routing rules...")

    routed_df = route_documents(
        enriched_df
    )

    print(
        "   Routing decisions complete."
    )

    # 5. Human review
    print(
        "\n5. Applying human-review controls..."
    )

    processed_df = apply_review_rules(
        routed_df
    )

    review_count = (
        processed_df[
            "Review_Required"
        ]
        .eq("Yes")
        .sum()
    )

    print(
        f"   Documents requiring review: "
        f"{review_count}"
    )

    # Add processing timestamp
    processed_df[
        "Processed_At"
    ] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # 6. Export CSVs
    print("\n6. Creating outputs...")

    csv_export = processed_df.drop(
        columns=["Raw_Text"],
        errors="ignore",
    )

    csv_export.to_csv(
        CSV_OUTPUT,
        index=False,
    )

    review_df = csv_export[
        csv_export[
            "Review_Required"
        ] == "Yes"
    ]

    review_df.to_csv(
        REVIEW_OUTPUT,
        index=False,
    )

    # 7. Excel management report
    report_path = create_excel_report(
        processed_df,
        processing_log,
    )

    print("\nOUTPUTS CREATED")

    print(
        f"   Report: {report_path}"
    )

    print(
        f"   Processed data: {CSV_OUTPUT}"
    )

    print(
        f"   Review queue: {REVIEW_OUTPUT}"
    )

    print(
        "\n----------------------------------------------"
    )

    print(
        f"Documents Processed : {len(processed_df)}"
    )

    print(
        f"Human Review        : {review_count}"
    )

    print(
        f"Auto-Processed      : "
        f"{len(processed_df) - review_count}"
    )

    print(
        "----------------------------------------------"
    )

    print(
        "\nPIPELINE COMPLETE\n"
    )


if __name__ == "__main__":
    main()