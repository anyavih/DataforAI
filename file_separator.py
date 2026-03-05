import os
import re
import math

def split_xom_files(input_folder, output_base_folder):
    if not os.path.exists(output_base_folder):
        os.makedirs(output_base_folder)

    # Pattern matches the dashed header and the bracketed metadata [cite: 2, 7, 25]
    chunk_pattern = re.compile(r'(--- \w+_\w+_\d+ ---\n\[\w+ \| \d+ \| \w+\])')

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_folder, filename)
            
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()

            parts = chunk_pattern.split(content)
            chunks = []
            
            # If there's a preamble (Source 1), prepend it to the first actual chunk
            preamble = parts[0] if parts[0].strip() else ""
            
            for i in range(1, len(parts), 2):
                header = parts[i]
                body = parts[i+1] if (i+1) < len(parts) else ""
                full_chunk = header + body
                
                if i == 1: # Attach the file-level header to the very first chunk 
                    chunks.append(preamble + full_chunk)
                else:
                    chunks.append(full_chunk)

            # Distribution logic for 5 files
            total_chunks = len(chunks)
            chunks_per_file = math.ceil(total_chunks / 5)

            file_output_dir = os.path.join(output_base_folder, filename.replace(".txt", ""))
            os.makedirs(file_output_dir, exist_ok=True)

            for i in range(5):
                start_idx = i * chunks_per_file
                end_idx = start_idx + chunks_per_file
                file_batch = chunks[start_idx:end_idx]

                if file_batch:
                    output_filename = f"{filename.replace('.txt', '')}_part_{i+1}.txt"
                    output_path = os.path.join(file_output_dir, output_filename)
                    
                    with open(output_path, 'w', encoding='utf-8') as f_out:
                        f_out.write("".join(file_batch))

            print(f"Processed {filename}: {total_chunks} chunks split into 5 files.")

if __name__ == "__main__":
    split_xom_files("/Users/anyavih/DataforAI/data_company_combined", "/Users/anyavih/DataforAI/data_company_split")