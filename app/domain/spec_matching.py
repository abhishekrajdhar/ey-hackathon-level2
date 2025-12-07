from typing import Dict


def compute_spec_match(required: Dict, candidate: Dict) -> float:
    """
    Simple spec-match metric:
    - For each key in required, check if candidate has same value (or close for numeric).
    - Return percentage of matched keys.
    """
    if not required:
        return 0.0

    total = len(required)
    matches = 0

    for key, req_val in required.items():
        cand_val = candidate.get(key)

        if isinstance(req_val, (int, float)) and isinstance(cand_val, (int, float)):
            if cand_val == 0:
                continue
            diff_ratio = abs(cand_val - req_val) / cand_val
            if diff_ratio <= 0.1:  # 10% tolerance
                matches += 1
        else:
            if str(req_val).lower() == str(cand_val).lower():
                matches += 1

    return round(100.0 * matches / total, 2)
