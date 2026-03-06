import pandas as pd
import json
import os
import time
from dotenv import load_dotenv
from tqdm import tqdm
from openai import OpenAI

# 1. LOAD CONFIGURATION
load_dotenv()
client = OpenAI()

if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY not found. Please check your .env file.")
    exit()

# 2. DEFINE THE AUDITOR PERSONA
SYSTEM_PROMPT = """
### ROLE
You are an expert Corporate ESG Auditor and Forensic Accountant. Your task is to generate a high-fidelity synthetic training dataset for a greenwashing detection model.

### INSTRUCTIONS
For each provided <chunk>, you must generate a "Verification Triplet." Do not skip any chunks.

1. SUPPORTED:
- A purely factual statement derived strictly from the text.
- Must be a neutral summary that requires no external inference.

2. REFUTED (The "Subtle Lie"):
- A statement that looks nearly identical to the truth but contains a minor, critical error.
- Strategy: Change one specific variable: a date (e.g., 2030 to 2035), a numerical value (e.g., 3,200 MW to 3,000 MW), or a qualifying verb (e.g., "targeting" to "will achieve").
- This tests the model's sensitivity to numerical discrepancies and "subtle hedging."

3. UNVERIFIABLE (The "Realistic Hallucination"):
- A formal-sounding statement that is plausible for the industry but is NOT supported by the text.
- Strategy: Introduce an external "phantom" fact, such as a specific federal grant, a partnership with the EPA, or a non-existent metric like "Scope 5 emissions."

### OUTPUT FORMAT
Output EXACTLY as a JSON object with a 'data' array. You must include a "rationale" for the Refuted and Unverifiable claims to explain the logic of your manipulation.

{
  "data": [
    {
      "id": "Tracking_ID_from_chunk",
      "triplets": {
        "supported": "string",
        "refuted": {
          "rationale": "string",
          "statement": "string"
        },
        "unverifiable": {
          "rationale": "string",
          "statement": "string"
        }
      }
    }
  ]
}
"""

# 3. HELPER FUNCTIONS
def generate_triplets_batch(batch_df):
    """Sends a batch of 5 chunks to GPT-4o for triplet generation."""
    user_content = "<chunks>\n"
    for _, row in batch_df.iterrows():
        user_content += f"<chunk id='{row['evidence_id']}'>\n{row['evidence_text']}\n</chunk>\n"
    user_content += "</chunks>"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            temperature=0.2 
        )
        
        raw_json = json.loads(response.choices[0].message.content)
        return raw_json.get("data", raw_json) if isinstance(raw_json, (dict, list)) else []
            
    except Exception as e:
        tqdm.write(f"  [!] API Error: {e}")
        return None

def print_verification_snapshot(ticker, stage, input_text, triplet):
    """Prints a comparison snapshot to terminal for human validation."""
    tqdm.write(f"\n{'='*20} {stage.upper()} SNAPSHOT: {ticker} {'='*20}")
    tqdm.write(f"INPUT (ID): {input_text[:120]}...")
    tqdm.write(f"  [SUPPORTED]: {triplet['supported']}")
    tqdm.write(f"  [REFUTED]  : {triplet['refuted']['statement']}")
    tqdm.write(f"    Reasoning: {triplet['refuted']['rationale']}")
    tqdm.write(f"  [UNVERIF]  : {triplet['unverifiable']['statement']}")
    tqdm.write(f"    Reasoning: {triplet['unverifiable']['rationale']}")
    tqdm.write(f"{'='*70}\n")

# 4. MAIN EXECUTION
def main():
    input_file = "filtered_climate_evidence.csv"
    output_file = "final_triplets_dataset.json"
    batch_size = 5  
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Run file_filter.py first.")
        return

    df = pd.read_csv(input_file)
    unique_tickers = df['ticker'].unique()
    final_results = []
    
    # Milestone markers for snapshots
    milestones = {0: "Beginning", len(unique_tickers)//2: "Middle", len(unique_tickers)-1: "End"}

    print(f"Loaded {len(df)} chunks across {len(unique_tickers)} companies.")
    
    # PROGRESS BAR: Tracks overall company progress
    for idx, ticker in enumerate(tqdm(unique_tickers, desc="Total Company Progress")):
        company_df = df[df['ticker'] == ticker]
        stage = milestones.get(idx)

        # BATCH LOOP: Processes 5 chunks at a time
        for i in range(0, len(company_df), batch_size):
            batch_df = company_df.iloc[i:i+batch_size]
            batch_output = generate_triplets_batch(batch_df)
            
            if batch_output:
                final_results.extend(batch_output)
                
                # Print periodic snapshots for quality control
                if stage and i == 0:
                    print_verification_snapshot(ticker, stage, batch_df.iloc[0]['evidence_text'], batch_output[0]['triplets'])

        # Atomic Saving: Writes to disk after every company is completed
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(final_results, f, indent=4)
        
        time.sleep(1) # Prevent rate limiting

    print(f"\nSUCCESS: Generated {len(final_results)} triplets saved to {output_file}.")

if __name__ == "__main__":
    main()