from app.services import detect_discovery_keywords


def test_detects_multiple_relevant_event_types() -> None:
    hits = detect_discovery_keywords(
        "Police pursuit ends in arrest",
        "A K-9 unit assisted officers after a vehicle chase.",
    )

    assert hits == ["pursuit", "k9", "arrest"]


def test_ignores_irrelevant_public_feed_item() -> None:
    assert detect_discovery_keywords("City council meeting", "Budget agenda released") == []
