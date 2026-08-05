from app.models import Case, CaseStatus
from app.schemas import ScorecardCreate
from app.services import create_scorecard


class FakeSession:
    def __init__(self) -> None:
        self.added = []
        self.committed = False

    def add(self, value) -> None:
        self.added.append(value)

    def flush(self) -> None:
        return None

    def commit(self) -> None:
        self.committed = True

    def refresh(self, value) -> None:
        return None


def test_scorecard_is_explainable_and_prioritizes_qualified_case() -> None:
    case = Case(title="Test case", state="TX", status=CaseStatus.DISCOVERED)
    db = FakeSession()
    payload = ScorecardCreate(
        recording_likelihood=90,
        editorial_value=85,
        acquisition_feasibility=75,
        legal_risk=10,
        timeliness=80,
        estimated_cost=10,
        explanation={"recording_likelihood": "Traffic pursuit reported by official source."},
    )

    scorecard = create_scorecard(db, case, payload)

    assert scorecard.total_score == 74
    assert case.status == CaseStatus.PRIORITIZED
    assert scorecard.explanation["recording_likelihood"].startswith("Traffic pursuit")
    assert db.committed
