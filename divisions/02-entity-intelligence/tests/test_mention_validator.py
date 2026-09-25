from extraction.mention_validator import MentionValidator


def test_known_location_is_corrected():

    validator = MentionValidator(
        "datasets/raw/locations.csv"
    )

    mention = {
        "text_span": "Baner",
        "entity_type": "PERSON",
    }

    result = validator.validate(mention)

    assert result["validation_status"] == "CORRECTED"
    assert result["validation_reason"] == "KNOWN_LOCATION"
    assert result["corrected_entity_type"] == "LOCATION"


def test_real_person_is_valid():

    validator = MentionValidator(
        "datasets/raw/locations.csv"
    )

    mention = {
        "text_span": "Akash V Kale",
        "entity_type": "PERSON",
    }

    result = validator.validate(mention)

    assert result["validation_status"] == "VALID"
    assert "corrected_entity_type" not in result