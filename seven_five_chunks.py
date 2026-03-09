import json
import random
import os

# List of IDs provided by you to EXCLUDE from the random sample
BANNED_IDS = {
    "AEE_RiskFactors_46", "ENPH_Business_0", "OKE_RiskFactors_27", 
    "SLB_Business_22", "TRGP_Business_193", "HAL_Business_37", 
    "PSX_MDA_217", "APA_Business_146", "CEG_Business_26", 
    "CMS_Business_45", "VLO_RiskFactors_84", "NRG_RiskFactors_139", 
    "OXY_MDA_28", "FAANG_Business_44", "SRE_Business_377", 
    "XOM_RiskFactors_27", "PPL_Business_73", "PCG_RiskFactors_93", 
    "NEE_RiskFactors_146", "MPC_RiskFactors_11", "KMI_Business_109", 
    "EXC_Business_56", "ETR_MDA_134", "DUK_MDA_40", "AEP_RiskFactors_92"
}

def create_sampling_set(input_file, output_file, sample_size=75):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Please run data_creator.py first.")
        return

    print(f"Loading data from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_count = len(data)
    
    # --- FILTER STEP ---
    # Keep only items whose ID is NOT in the banned set
    filtered_data = [item for item in data if item['id'] not in BANNED_IDS]
    
    excluded_count = total_count - len(filtered_data)
    print(f"Excluded {excluded_count} specific examples provided in your list.")
    print(f"Pool available for sampling: {len(filtered_data)} triplets.")

    if len(filtered_data) < sample_size:
        print(f"Warning: Only {len(filtered_data)} triplets available after filtering. Sampling all of them.")
        sample_size = len(filtered_data)

    # Randomly select 75 triplets from the FILTERED list
    golden_sample = random.sample(filtered_data, sample_size)

    # Save the sample for manual review
    with open(output_file, 'w', encoding='utf-8') as f_out:
        json.dump(golden_sample, f_out, indent=4)

    print(f"\nSuccessfully sampled {sample_size} random triplets (excluding banned IDs).")
    print(f"Saved to: {output_file}\n")

    # Print the first 2 for confirmation
    for i, item in enumerate(golden_sample[:2]):
        print(f"--- Sample {i+1} (ID: {item['id']}) ---")
        print(f"  [SUPPORTED]: {item['triplets']['supported']}")
        print(f"  [REFUTED]  : {item['triplets']['refuted']['statement']}")
        print(f"  [UNVERIF]  : {item['triplets']['unverifiable']['statement']}")
        print("-" * 50)

if __name__ == "__main__":
    create_sampling_set("final_triplets_dataset.json", "verification_sample.json")