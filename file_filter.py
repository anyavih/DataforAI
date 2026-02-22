import pandas as pd
import re
import os

def run_climate_filter():
    input_file = "segmented_evidence_robust.csv"
    output_csv = "filtered_climate_evidence.csv"
    output_dir = "data_filtered"
    combined_dir = "data_company_combined" 

    try:
        df = pd.read_csv(input_file)
        print(f"Loaded {len(df)} total chunks from {input_file}.")
    except FileNotFoundError:
        print(f"Error: {input_file} not found. Please run the segmentation script first.")
        return

    keywords = [
        # Core Terms
        r"\bclimate\b",
        r"\bemissions?\b",       
        r"\brenewables?\b",     
        
        # Comprehensive Carbon Terms
        r"\bcarbon\b",                  
        r"\bcarbon neutral\b",
        r"\bcarbon capture\b",
        r"\bcarbon offsets?\b",          
        r"\bcarbon credits?\b",
        r"\bcarbon footprint\b",
        r"\binternal carbon pric(e|ing)\b", 
        
        # Technical & Reporting Frameworks
        r"\b(ghg|greenhouse gas(es)?)\b",
        r"\bscope [123]\b",              
        r"\bnet[- ]?zero\b",    
        r"\besg\b",
        r"\bsustainability\b",
        r"\bdecarbonization\b",
        
        # Sector-Specific Energy & Utility Terms
        r"\brvo\b",                  
        r"\bcoal retirements?\b",    
        r"\bclean energy\b",
        r"\bmethane\b",              
        r"\bflaring\b",
        r"\brenewable portfolio standard\b",
        r"\bccus\b",
        
        # Regulatory & Risk Frameworks
        r"\binflation reduction act\b",
        r"\bira\b", 
        r"\bparis agreement\b",
        r"\btransition risk\b",
        r"\bphysical risk\b",
        r"\bepa\b"
    ]

    regex_pattern = "|".join(keywords)

    print("Applying regex filter for climate-related keywords...")
    climate_df = df[df['evidence_text'].str.contains(regex_pattern, case=False, na=False, regex=True)].copy()

    # Save the filtered dataset to CSV
    climate_df.to_csv(output_csv, index=False)
    
    # Save individual text files 
    print(f"Creating individual text files in '{output_dir}' directory...")
    os.makedirs(output_dir, exist_ok=True) 
    
    for index, row in climate_df.iterrows():
        file_name = f"{row.get('evidence_id', f'chunk_{index}')}.txt"
        file_path = os.path.join(output_dir, file_name)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(str(row['evidence_text']))

    print(f"Creating combined company files in '{combined_dir}' directory...")
    os.makedirs(combined_dir, exist_ok=True)

    if 'ticker' in climate_df.columns:
        # Group the DataFrame by the company ticker
        grouped = climate_df.groupby('ticker')
        
        for ticker, group in grouped:
            combined_file_path = os.path.join(combined_dir, f"{ticker}_combined_evidence.txt")
            
            with open(combined_file_path, "w", encoding="utf-8") as f:
                f.write(f"=== CLIMATE EVIDENCE FOR {ticker} ===\n\n")
                
                # Iterate through that specific company's chunks to build the scrollable text
                for idx, row in group.iterrows():
                    chunk_id = row.get('evidence_id', f'chunk_{idx}')
                    text = str(row['evidence_text'])
                    f.write(f"--- {chunk_id} ---\n")
                    f.write(f"{text}\n\n")
                    
        print(f"Successfully created {len(grouped)} combined company files.")
    else:
        print("Warning: 'ticker' column not found. Cannot group by company.")

    # Calculate reduction for logging
    reduction_pct = (1 - (len(climate_df) / len(df))) * 100
    print("\n--- Filtering Complete ---")
    print(f"Original Chunks: {len(df)}")
    print(f"Climate Chunks : {len(climate_df)}")
    print(f"Noise Removed  : {reduction_pct:.1f}%")
    print(f"Saved CSV to   : {output_csv}")
    print(f"Saved TXTs to  : {output_dir}/")
    print(f"Saved Combined : {combined_dir}/")

if __name__ == "__main__":
    run_climate_filter()
