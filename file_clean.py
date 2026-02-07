import os
import pandas as pd
import re
import spacy
from tqdm import tqdm 

#Load spaCy model for intelligent sentence splitting
#We disable 'ner' and 'parser' to speed up processing, 
#but we MUST add 'sentencizer' to split sentences without the parser.
try:
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    nlp.add_pipe("sentencizer")
    nlp.max_length = 2000000
except OSError:
    print("Spacy model not found. Please run: python -m spacy download en_core_web_sm")
    exit()

def clean_text_robust(text):
    """
    Advanced cleanup to fix PDF artifacts and normalize text.
    """
    if not text or text == "SECTION NOT FOUND":
        return ""

    #Fix Hyphenation (e.g., "sustain-\nability" -> "sustainability")
    #Matches a word character, hyphen, newline/spaces, and a lowercase letter
    text = re.sub(r'(\w+)-\s*\n\s*([a-z])', r'\1\2', text)
    
    #Remove specific SEC artifacts
    #Removes "Table of Contents", "Page X", and repeated underscores often used in tables
    text = re.sub(r'(Table of Contents|Page \d+|_+)', ' ', text, flags=re.IGNORECASE)
    
    #Normalize Whitespace (turn newlines and tabs into single spaces)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def segment_text_robust(text, ticker, year, section, chunk_size=1000, overlap_sentences=2):
    """
    Splits text into chunks using sliding windows and sentence boundaries.
    Injects metadata (Ticker/Year) into the text itself.
    """
    #Parse sentences using spaCy
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 0]
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    #Sliding Window Logic (Sentence-based for safety)
    for sent in sentences:
        sent_len = len(sent)
        
        #If adding the next sentence keeps us under the limit...
        if current_length + sent_len < chunk_size:
            current_chunk.append(sent)
            current_length += sent_len + 1 # +1 accounts for the space we add later
        else:
            #Chunk is full. Save it.
            if current_chunk: 
                #Join the sentences to form the chunk text
                chunk_text = " ".join(current_chunk)
                #Prepend context to the text
                enriched_text = f"[{ticker} | {year} | {section}] {chunk_text}"
                chunks.append(enriched_text)
            
            #Start new chunk with OVERLAP
            #Take the last 'overlap_sentences' from the previous chunk to maintain context
            if len(current_chunk) > overlap_sentences:
                current_chunk = current_chunk[-overlap_sentences:]
            #If the chunk was smaller than the overlap, keep the whole thing
            #Add the current sentence that caused the overflow
            current_chunk.append(sent)
            
            #Recalculate length for the new window
            current_length = sum(len(s) for s in current_chunk) + len(current_chunk)
            
    #Catch the final chunk
    if current_chunk:
        chunk_text = " ".join(current_chunk)
        if len(chunk_text) > 50: # Filter out tiny final debris
            enriched_text = f"[{ticker} | {year} | {section}] {chunk_text}"
            chunks.append(enriched_text)
        
    return chunks


input_dir = "data"
output_records = []

if not os.path.exists(input_dir):
    print(f"Error: Directory '{input_dir}' not found.")
    exit()

files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]

print(f"Processing {len(files)} files with robust segmentation...")

for filename in tqdm(files):
    #Parse metadata from filename (format: TICKER_DATE_SECTION.txt)
    try:
        parts = filename.replace(".txt", "").split("_")
        ticker = parts[0]
        #Extract just the year from the date string (e.g., 2023-02-28 -> 2023)
        year = parts[1].split("-")[0] 
        section = parts[-1]
    except IndexError:
        print(f"Skipping malformed filename: {filename}")
        continue

    file_path = os.path.join(input_dir, filename)
    
    with open(file_path, "r", encoding="utf-8") as f:
        raw_content = f.read()
        
    #Clean
    cleaned_content = clean_text_robust(raw_content)
    
    #Segment with Context
    chunks = segment_text_robust(cleaned_content, ticker, year, section)
    
    #Store
    for i, chunk in enumerate(chunks):
        output_records.append({
            "evidence_id": f"{ticker}_{section}_{i}",
            "ticker": ticker,
            "year": year,
            "section": section,
            "evidence_text": chunk})

#Save to CSV
output_file = "segmented_evidence_robust.csv"
df_evidence = pd.DataFrame(output_records)
df_evidence.to_csv(output_file, index=False)

print(f"\nSuccess! Processing complete.")
print(f"Created {len(df_evidence)} robust evidence chunks.")
print(f"Saved to: {output_file}")
