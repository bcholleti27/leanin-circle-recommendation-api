
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

DATASETS = (
    "users",
    "circles",
    "memberships",
    "topics",
    "activity",
)


def load_dataset(name: str) -> list[dict]:
    """Load one seed dataset from its JSON file."""
    if name not in DATASETS:
        raise ValueError(f"Unknown dataset: {name}")

    file_path = DATA_DIR / f"{name}.json"

    with file_path.open(encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
       raise TypeError(f"{name}.json must contain a JSON array")

    return records


def load_all_data() -> dict[str, list[dict]]:
    """Load all five datasets."""
    return {
        name: load_dataset(name)
        for name in DATASETS
    }
