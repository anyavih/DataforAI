import json
import pandas as pd

def json_to_csv():
    input_file = "verification_sample.json"
    output_file = "verification_sample_readable.csv"

    # 1. Load the JSON data
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: verification_sample.json not found.")
        return

    # 2. Flatten the data into a spreadsheet format
    rows = []
    for item in data:
        rows.append({
            "Tracking_ID": item.get("id"),
            "Supported_Fact": item["triplets"]["supported"],
            "Refuted_Lie": item["triplets"]["refuted"]["statement"],
            "Refuted_Reasoning": item["triplets"]["refuted"]["rationale"],
            "Unverifiable_Hallucination": item["triplets"]["unverifiable"]["statement"],
            "Unverifiable_Reasoning": item["triplets"]["unverifiable"]["rationale"]
        })

    # 3. Save as CSV
    df = pd.DataFrame(rows)
    df.to_csv(output_file, index=False)
    
    print(f"Success! Created '{output_file}'.")
    print("You can now upload this file to Google Drive and open it with Google Sheets.")

if __name__ == "__main__":
    json_to_csv()