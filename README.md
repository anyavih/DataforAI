# Auditing Greenwashing in SEC Filings with LLMs

This repository contains the end-to-end pipeline for extracting, processing, and auditing corporate climate disclosures using Natural Language Inference (NLI). Our research focuses on identifying subtle lies and hallucinations in S&P 500 Energy and Utilities filings where general-purpose LLMs often fail.

## Repository Structure

* **`data_scrape.py`**: Automates retrieval of 10-K filings for 49 companies using the `edgar` and `pandas` libraries. It targets Item 1 (Business), Item 1A (Risk Factors), and Item 7 (MD&A).
* **`file_clean.py`**: Cleans raw text using Regex to fix PDF artifacts and `spaCy` for grammatical segmentation.
* **`file_filter.py`**: Implements `run_climate_filter()`, using a 25+ keyword Regex pattern (e.g., "emissions", "RVO", "CCUS") to isolate high-fidelity climate evidence.
* **`data_creator.py`**: Generates synthetic "Verification Triplets" (Supported, Refuted, and Unverifiable claims) using GPT-4o.
* **`seven_five_chunks.py`**: Script used to manage the "Golden Set" validation data, consisting of a 75/25 split between synthetic and human-authored triplets.
* **`csv_converter.py`**: Manages the `dataset_manifest.csv`, logging metadata such as SEC accession numbers and filing dates for auditable tracking.
* **`DataAI.ipynb`**: The main notebook for training the **roberta-base** NLI model. It handles the 90-10 stratified test-train split and the fine-tuning process.

##  Key Research Findings

* **LLM Baseline**: In preliminary testing, state-of-the-art models like Gemini and Claude accurately labeled only $\approx60\%$ of "Golden Set" data when identifying factual truths vs. lies.
* **NLI Performance**: Our fine-tuned RoBERTa model achieved a **Macro-F1 score of 0.973**, proving highly effective at forensic analysis.
* **Error Detection**: The model maintained 100% accuracy in detecting refuted claims involving subtle numerical or temporal manipulations (e.g., changing a 50% reduction goal to 35%).

##  Authors
* **Simran Nayak** 
* **Anya Hansen** 

