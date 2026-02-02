from edgar import *
import pandas as pd
import os

set_identity("ClimateAuditProject secretsanta123456789baker@gmail.com")

#Target companies to be scraped 
tickers = [
    #Integrated Oil & Gas / E&P
    "XOM", "CVX", "COP", "EOG", "SLB", "MPC", "PSX", "VLO", "WMB", "OKE",
    "KMI", "BKR", "HAL", "OXY", "DVN", "FANG", "CTRA", "TRGP", "HES", "APA",
    #Utilities & Power
    "NEE", "SO", "DUK", "CEG", "AEP", "SRE", "D", "EXC", "XEL", "PCG",
    "ED", "PEG", "WEC", "EIX", "ETR", "DTE", "FE", "ES", "AEE", "PPL",
    "CNP", "CMS", "ATO", "LNT", "EVRG", "NI", "PNW", "NRG",
    #Solar/Clean Tech
    "FSLR", "ENPH"]

#Create the output directory if it doesn't exist
output_dir = "data"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

#Storage for metadata
dataset_records = []

#Loop through companies and fetch data
print(f"Starting extraction for {len(tickers)} companies...")

for ticker in tickers:
    try:
        print(f"Fetching 10-K for {ticker}...")
        company = Company(ticker)
        
        #Get the most recent 10-K file 
        filing = company.get_filings(form="10-K").latest()
        if not filing:
            print(f"  [!] No 10-K found for {ticker}")
            continue
        #Get the Content Object 
        k10 = filing.obj()
        if not k10:
            print(f"  [!] Could not parse 10-K object for {ticker}")
            continue
        #Extract sections of interest 
        risk_factors = k10["Item 1A"] 
        mda = k10["Item 7"]
        
        #Define file names 
        date_str = str(filing.filing_date) 
        filename_base = f"{ticker}_{date_str}"
        rf_path = os.path.join(output_dir, f"{filename_base}_RiskFactors.txt")
        mda_path = os.path.join(output_dir, f"{filename_base}_MDA.txt")
        #Save Risk Factors
        with open(rf_path, "w", encoding="utf-8") as f:
            f.write(risk_factors if risk_factors else "SECTION NOT FOUND")
        #Save MD&A
        with open(mda_path, "w", encoding="utf-8") as f:
            f.write(mda if mda else "SECTION NOT FOUND")
            
        #Log metadata using the FILING object for the accession number
        dataset_records.append({
            "ticker": ticker,
            "filing_date": date_str,
            "accession_number": filing.accession_number, 
            "risk_factors_file": rf_path,
            "mda_file": mda_path,
            "has_risk_factors": bool(risk_factors),
            "has_mda": bool(mda)
        })
        
        print(f"  [+] Saved {ticker}")

    except Exception as e:
        print(f"  [!] Error processing {ticker}: {e}")

#Save final manifest CSV
if dataset_records:
    df = pd.DataFrame(dataset_records)
    df.to_csv("dataset_manifest.csv", index=False)
    print("\nSuccess! Metadata saved to 'dataset_manifest.csv'")
else:
    print("\nNo data was collected.")