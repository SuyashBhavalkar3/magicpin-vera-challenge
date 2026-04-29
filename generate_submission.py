import json
import os
from pathlib import Path
from bot import compose

def main():
    expanded_dir = Path("expanded")
    test_pairs_path = expanded_dir / "test_pairs.json"
    
    if not test_pairs_path.exists():
        print(f"Error: {test_pairs_path} not found. Run generate_dataset.py first.")
        return

    with open(test_pairs_path) as f:
        test_pairs = json.load(f)["pairs"]

    submissions = []
    
    for pair in test_pairs:
        test_id = pair["test_id"]
        trigger_id = pair["trigger_id"]
        merchant_id = pair["merchant_id"]
        customer_id = pair.get("customer_id")

        # Load contexts
        with open(expanded_dir / "triggers" / f"{trigger_id}.json") as f:
            trigger = json.load(f)
        with open(expanded_dir / "merchants" / f"{merchant_id}.json") as f:
            merchant = json.load(f)
        with open(expanded_dir / "categories" / f"{merchant['category_slug']}.json") as f:
            category = json.load(f)
        
        customer = None
        if customer_id:
            with open(expanded_dir / "customers" / f"{customer_id}.json") as f:
                customer = json.load(f)

        # Compose
        result = compose(category, merchant, trigger, customer)
        
        # Format for submission
        submission_line = {
            "test_id": test_id,
            "body": result["body"],
            "cta": result["cta"],
            "send_as": result["send_as"],
            "suppression_key": result["suppression_key"],
            "rationale": result["rationale"]
        }
        submissions.append(submission_line)

    # Write to JSONL
    with open("submission.jsonl", "w", encoding="utf-8") as f:
        for entry in submissions:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Successfully generated submission.jsonl with {len(submissions)} entries.")

if __name__ == "__main__":
    main()
