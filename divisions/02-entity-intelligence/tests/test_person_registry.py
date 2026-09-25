import sys
from pathlib import Path

D2_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = D2_ROOT.parents[1]

sys.path.insert(0, str(D2_ROOT))

from extraction.person_registry import PersonRegistryExtractor


PERSON_FILE = PROJECT_ROOT / "datasets" / "raw" / "person.csv"


def test_person_registry_extraction():

    extractor = PersonRegistryExtractor(PERSON_FILE)

    text = (
        "Akash V Kale was reported in connection "
        "with a robbery incident in Pune."
    )

    result = extractor.extract(text)

    matches = [
        item
        for item in result
        if item["entity_type"] == "PERSON"
    ]

    assert len(matches) >= 1

    akash = [
        item
        for item in matches
        if item["extracted_value"] == "Akash V Kale"
    ]

    assert len(akash) >= 1

    assert set(akash[0]["candidate_person_ids"]) == {
        "P001807",
        "P002378",
    }