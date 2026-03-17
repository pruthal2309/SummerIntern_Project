from datasets import load_dataset

# 1. Load new dataset from Hugging Face
new_dataset = load_dataset("dataset_name", split="train", streaming=True)

# 2. Save to text files (like you did before)
import os
from tqdm import tqdm

output_dir = "data/raw/new_dataset_name"
os.makedirs(output_dir, exist_ok=True)

for i, row in enumerate(new_dataset):
    text = row.get("text", "")
    if text:
        with open(f"{output_dir}/doc_{i}.txt", "w", encoding="utf-8") as f:
            f.write(text)

# 3. Run the pipeline again
# python ingestion/load_documents.py
