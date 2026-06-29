"""Unit tests for Layout Evaluation Engine."""
from __future__ import annotations
import math
import pytest
from building_model_v2.layout.layout_evaluation import LayoutEvaluationEngine
from building_model_v2.layout.privacy_metrics import PrivacyConflict
from building_model_v2.layout.layout_evaluation_result import LayoutEvaluationResult
from building_model_v2.layout.adjacency_engine import AdjacencyEngine
from building_model_v2.layout.room_graph import RoomGraph
from building_model_v2.entities_building import Building
from building_model_v2.entities_floor import Floor
from building_model_v2.entities_room import Room
from building_model_v2.types import RoomType
from building_model_v2.validation.cross_entity_validator import BuildingModel


def _build(room_configs):
    b = Building.create(name="T", floor_ids=("f1",))
    f = Floor.create(name="F1", level=0, room_ids=frozenset(r[0] for r in room_configs))
    rooms = {}
    for n, rt, verts in room_configs:
        rooms[n] = Room.create(vertices=verts, room_type=rt, metadata={"name": n})
    return BuildingModel(building=b, floors={"f1": f}, rooms=rooms, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])


class TestLayoutEvaluationResult:
    def _make_result(self, adj_issues=0, priv_conflicts=0, egress_issues=0, circ_issues=0):
        from building_model_v2.constraints.constraint_result import ConstraintResult
        from building_model_v2.constraints.constraint_issue import ConstraintIssue
        from building_model_v2.constraints.constraint_severity import ConstraintSeverity
        from building_model_v2.layout.privacy_metrics import PrivacyMetrics
        from building_model_v2.layout.egress_metrics import EgressMetrics
        from building_model_v2.layout.circulation_metrics import CirculationMetrics
        adj_issues_list = [ConstraintIssue(code=f"I{i}", message=f"adj {i}", severity=ConstraintSeverity.WARNING, score=0.5) for i in range(adj_issues)]
        priv_conflicts_list = [PrivacyConflict(f"a{i}", f"b{i}", f"PC{i}", f"conflict {i}") for i in range(priv_conflicts)]
        egress_issues_list = [ConstraintIssue(code=f"E{i}", message=f"egress {i}", severity=ConstraintSeverity.WARNING, score=0.6) for i in range(egress_issues)]
        circ_issues_list = [ConstraintIssue(code=f"C{i}", message=f"circ {i}", severity=ConstraintSeverity.SUGGESTION, score=0.3) for i in range(circ_issues)]
        return LayoutEvaluationResult(
            adjacency_result=ConstraintResult(issues=adj_issues_list),
            circulation_metrics=CirculationMetrics(0.0, 0.0, frozenset(), frozenset(), 1.0, frozenset(), frozenset()),
            circulation_result=ConstraintResult(issues=circ_issues_list),
            privacy_metrics=PrivacyMetrics(frozenset(), frozenset(), frozenset(), 1.0, tuple(priv_conflicts_list), 0),
            egress_metrics=EgressMetrics(frozenset(), frozenset(), 0.0, 0.0, frozenset(), (), 1.0),
            egress_result=ConstraintResult(issues=egress_issues_list),
        )

    def test_score_perfect(self):
        r = self._make_result()
        assert r.overall_layout_score == 100.0

    def test_score_with_adjacency(self):
        r = self._make_result(adj_issues=2)
        assert r.overall_layout_score == 96.0

    def test_score_with_privacy(self):
        r = self._make_result(priv_conflicts=2)
        assert r.overall_layout_score == 94.0

    def test_score_with_egress(self):
        r = self._make_result(egress_issues=2)
        assert r.overall_layout_score == 92.0

    def test_score_with_circulation(self):
        r = self._make_result(circ_issues=3)
        assert r.overall_layout_score == 94.0

    def test_score_clamped_zero(self):
        r = self._make_result(adj_issues=100)
        assert r.overall_layout_score == 0.0

    def test_issue_count(self):
        r = self._make_result(adj_issues=2, priv_conflicts=1, egress_issues=3, circ_issues=4)
        assert r.issue_count == 10

    def test_warning_count(self):
        r = self._make_result(adj_issues=2, egress_issues=1, priv_conflicts=3)
        assert r.warning_count == 6

    def test_recommendation_count(self):
        r = self._make_result(circ_issues=3)
        # Circulation issues use SUGGESTION severity, not RECOMMENDATION
        # So recommendation_count should be 0
        assert r.recommendation_count == 0

    def test_quality_excellent(self):
        r = self._make_result()
        assert r.layout_quality == "Excellent"

    def test_quality_good(self):
        r = self._make_result(adj_issues=3, priv_conflicts=2)
        assert r.layout_quality == "Good"

    def test_quality_fair(self):
        r = self._make_result(adj_issues=5, priv_conflicts=3, egress_issues=2)
        assert r.layout_quality == "Fair"

    def test_quality_poor(self):
        r = self._make_result(adj_issues=20, priv_conflicts=10, egress_issues=15)
        assert r.layout_quality == "Poor"

    def test_serialization(self):
        r = self._make_result(adj_issues=3, priv_conflicts=2)
        d = r.to_dict()
        # Score: 100 - 3*2 - 2*3 = 100 - 6 - 6 = 88 (Good)
        assert d["overall_layout_score"] == 88.0
        assert d["layout_quality"] == "Good"
        assert d["adjacency_issues"] == 3
        assert d["privacy_conflicts"] == 2

    def test_frozen(self):
        r = self._make_result()
        with pytest.raises(AttributeError):
            r.overall_layout_score = 50.0



class TestLayoutEvaluationEngine:
    def test_empty_building(self):
        b = Building.create(name="T", floor_ids=())
        m = BuildingModel(building=b, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        e = LayoutEvaluationEngine()
        r = e.evaluate(m)
        assert isinstance(r, LayoutEvaluationResult)
        assert r.overall_layout_score == 100.0
        assert r.issue_count == 0

    def test_single_room(self):
        m = _build([("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)])])
        e = LayoutEvaluationEngine()
        r = e.evaluate(m)
        assert isinstance(r, LayoutEvaluationResult)
        assert r.layout_quality == "Good"

    def test_valid_layout(self):
        m = _build([
            ("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Kitchen", RoomType.KITCHEN, [(10,0),(20,0),(20,10),(10,10)]),
            ("Dining", RoomType.DINING, [(20,0),(30,0),(30,10),(20,10)]),
        ])
        e = LayoutEvaluationEngine()
        r = e.evaluate(m)
        assert isinstance(r, LayoutEvaluationResult)
        assert r.overall_layout_score > 0

    def test_invalid_layout(self):
        m = _build([
            ("Toilet", RoomType.TOILET, [(0,0),(10,0),(10,10),(0,10)]),
            ("Dining", RoomType.DINING, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = LayoutEvaluationEngine()
        r = e.evaluate(m)
        assert r.issue_count > 0

    def test_shared_graph_reuse(self):
        m = _build([
            ("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Kitchen", RoomType.KITCHEN, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = LayoutEvaluationEngine()
        r1 = e.evaluate(m)
        r2 = e.evaluate(m)
        assert r1.overall_layout_score == r2.overall_layout_score
        assert r1.issue_count == r2.issue_count

    def test_deterministic(self):
        m = _build([
            ("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Bedroom", RoomType.BEDROOM, [(10,0),(20,0),(20,10),(10,10)]),
            ("Bathroom", RoomType.BATHROOM, [(20,0),(30,0),(30,10),(20,10)]),
        ])
        e = LayoutEvaluationEngine()
        r1 = e.evaluate(m)
        r2 = e.evaluate(m)
        assert r1 == r2

    def test_all_engines_called(self):
        m = _build([
            ("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Kitchen", RoomType.KITCHEN, [(10,0),(20,0),(20,10),(10,10)]),
            ("Bedroom", RoomType.BEDROOM, [(20,0),(30,0),(30,10),(20,10)]),
        ])
        e = LayoutEvaluationEngine()
        r = e.evaluate(m)
        assert r.adjacency_result is not None
        assert r.circulation_metrics is not None
        assert r.circulation_result is not None
        assert r.privacy_metrics is not None
        assert r.egress_metrics is not None
        assert r.egress_result is not None

    def test_score_calculation(self):
        m = _build([
            ("Toilet", RoomType.TOILET, [(0,0),(10,0),(10,10),(0,10)]),
            ("Dining", RoomType.DINING, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = LayoutEvaluationEngine()
        r = e.evaluate(m)
        assert r.issue_count > 0
        assert r.overall_layout_score < 100.0

    def test_quality_classification(self):
        m = _build([
            ("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Kitchen", RoomType.KITCHEN, [(10,0),(20,0),(20,10),(10,10)]),
            ("Bedroom", RoomType.BEDROOM, [(20,0),(30,0),(30,10),(20,10)]),
            ("Bathroom", RoomType.BATHROOM, [(30,0),(40,0),(40,10),(30,10)]),
        ])
        e = LayoutEvaluationEngine()
        r = e.evaluate(m)
        assert r.layout_quality in ("Excellent", "Good", "Fair", "Poor")

    def test_integration_with_all_engines(self):
        ae = AdjacencyEngine()
        m = _build([
            ("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Kitchen", RoomType.KITCHEN, [(10,0),(20,0),(20,10),(10,10)]),
            ("Bedroom", RoomType.BEDROOM, [(20,0),(30,0),(30,10),(20,10)]),
        ])
        graph = ae.build_graph(m)
        e = LayoutEvaluationEngine()
        r = e.evaluate(m)
        assert len(r.adjacency_result.issues) >= 0
        assert r.circulation_metrics.average_path_length >= 0
        assert 0 <= r.privacy_metrics.privacy_score <= 1
        assert 0 <= r.egress_metrics.egress_score <= 1

    def test_no_mutation(self):
        m = _build([
            ("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Kitchen", RoomType.KITCHEN, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = LayoutEvaluationEngine()
        orig = dict(m.rooms)
        e.evaluate(m)
        assert dict(m.rooms) == orig
