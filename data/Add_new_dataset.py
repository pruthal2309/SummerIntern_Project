from datasets import load_dataset
from pathlib import Path
from tqdm import tqdm

# 1. Load new dataset from Hugging Face
new_dataset = load_dataset("dataset_name", split="train", streaming=True)

# 2. Save to text files under the project directory (avoids depending on current working dir)
REPO_ROOT = Path(__file__).resolve().parents[1]
output_dir = REPO_ROOT / "data" / "raw" / "new_dataset_name"
output_dir.mkdir(parents=True, exist_ok=True)

for i, row in enumerate(new_dataset):
    text = row.get("text", "")
    if text:
        out_path = output_dir / f"doc_{i}.txt"
        out_path.write_text(text, encoding="utf-8")

# 3. Run the pipeline again
# python -m backend.main --pipeline
