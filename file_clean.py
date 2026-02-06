import os
import pandas as pd
import re

def clean_text(text):
    """Basic cleanup for SEC boilerplate and whitespace."""
    #Remove 'SECTION NOT FOUND' markers
    if text == "SECTION NOT FOUND":
        return ""
    #Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    #Remove common SEC artifacts like page numbers or 'Table of Contents'
    text = re.sub(r'Page \d+|Table of Contents', '', text, flags=re.IGNORECASE)
    return text.strip()

def segment_text(text, min_length=200):
    """
    Splits text into paragraphs. 
    Filters out short fragments that don't contain enough context.
    """
    #Split by double newline or typical paragraph breaks
    paragraphs = text.split('\n')
    valid_chunks = []
    for p in paragraphs:
        p = clean_text(p)
        #Only keep paragraphs that look like actual informative sentences
        if len(p) >= min_length:
            valid_chunks.append(p)
            
    return valid_chunks

#Setup
input_dir = "data"
output_records = []

#Process files
print("Segmenting files...")
for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        #Parse metadata from filename (format: TICKER_DATE_SECTION.txt)
        parts = filename.replace(".txt", "").split("_")
        ticker = parts[0]
        section = parts[-1]
        
        with open(os.path.join(input_dir, filename), "r", encoding="utf-8") as f:
            content = f.read()
            chunks = segment_text(content)
            
            for i, chunk in enumerate(chunks):
                output_records.append({
                    "evidence_id": f"{ticker}_{section}_{i}",
                    "ticker": ticker,
                    "section": section,
                    "evidence_text": chunk})

#Save to CSV
df_evidence = pd.DataFrame(output_records)
df_evidence.to_csv("segmented_evidence.csv", index=False)
print(f"Success! Created {len(df_evidence)} evidence chunks.")