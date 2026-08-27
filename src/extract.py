from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "sample_documents"

SUPPORTED_EXTENSIONS = {".txt"}


def extract_text_from_file(file_path: Path) -> str:
    """
    Read text from a supported document.
    """
    if file_path.suffix.lower() == ".txt":
        return file_path.read_text(encoding="utf-8").strip()

    raise ValueError(f"Unsupported file type: {file_path.suffix}")


def extract_documents():
    """
    Discover supported documents and return:
    1. Combined document metadata/text dataframe
    2. Processing summary dataframe
    """

    records = []
    summary = []

    for file_path in sorted(INPUT_DIR.iterdir()):
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:
            text = extract_text_from_file(file_path)

            records.append(
                {
                    "Document_Name": file_path.name,
                    "File_Type": file_path.suffix.lower(),
                    "Character_Count": len(text),
                    "Raw_Text": text,
                }
            )

            summary.append(
                {
                    "Document_Name": file_path.name,
                    "Status": "Loaded",
                    "Characters": len(text),
                }
            )

        except Exception as exc:
            summary.append(
                {
                    "Document_Name": file_path.name,
                    "Status": f"Failed: {exc}",
                    "Characters": 0,
                }
            )

    if not records:
        raise ValueError("No supported documents were found.")

    documents_df = pd.DataFrame(records)
    summary_df = pd.DataFrame(summary)

    return documents_df, summary_df


if __name__ == "__main__":
    documents_df, summary_df = extract_documents()

    print("\nDOCUMENTS LOADED\n")
    print(summary_df.to_string(index=False))

    print(f"\nTotal Documents: {len(documents_df)}")