from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]

ENTITY_MENTIONS_FILE = (
    PROJECT_ROOT / "datasets" / "raw" / "entity_mentions.csv"
)

VEHICLES_FILE = (
    PROJECT_ROOT / "datasets" / "raw" / "vehicles.csv"
)


def main():
    mentions = pd.read_csv(ENTITY_MENTIONS_FILE)
    vehicles = pd.read_csv(VEHICLES_FILE)

    person_mentions = mentions[
        mentions["entity_type"] == "PERSON"
    ].copy()

    vehicle_mentions = mentions[
        mentions["entity_type"] == "VEHICLE"
    ][
        ["document_id", "case_id", "extracted_value"]
    ].copy()

    vehicle_mentions["extracted_value"] = (
        vehicle_mentions["extracted_value"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    vehicles["registration_number"] = (
        vehicles["registration_number"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    # Join extracted vehicle → vehicle registry
    matched = vehicle_mentions.merge(
        vehicles[
            [
                "registration_number",
                "registered_owner_id",
                "current_owner_id",
            ]
        ],
        left_on="extracted_value",
        right_on="registration_number",
        how="inner",
    )

    print("Matched vehicle mentions:", len(matched))
    print()

    for _, vehicle_row in matched.iterrows():

        document_id = vehicle_row["document_id"]
        vehicle_number = vehicle_row["extracted_value"]
        registered_owner = vehicle_row["registered_owner_id"]
        current_owner = vehicle_row["current_owner_id"]

        same_document = person_mentions[
            person_mentions["document_id"] == document_id
        ]

        print("=" * 80)
        print("DOCUMENT:", document_id)
        print("VEHICLE:", vehicle_number)
        print("REGISTERED OWNER:", registered_owner)
        print("CURRENT OWNER:", current_owner)
        print()

        if same_document.empty:
            print("No PERSON mentions in same document.")
            continue

        print("PERSON mentions in same document:")

        columns = [
            "text_span",
            "candidate_person_ids",
            "candidate_count",
        ]

        available_columns = [
            column
            for column in columns
            if column in same_document.columns
        ]

        print(
            same_document[available_columns]
            .to_string(index=False)
        )

        print()

        # Check whether either owner appears
        # in the candidate list of a PERSON mention.
        for _, person_row in same_document.iterrows():

            candidates = str(
                person_row.get(
                    "candidate_person_ids",
                    "",
                )
            )

            if (
                str(registered_owner) in candidates
                or str(current_owner) in candidates
            ):
                print(
                    ">>> OWNER APPEARS IN PERSON CANDIDATES:",
                    person_row["text_span"],
                )


if __name__ == "__main__":
    main()