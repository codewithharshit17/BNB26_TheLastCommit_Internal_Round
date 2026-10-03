import random

from engine.simulator.students import simulate


def test_student_simulation_is_reproducible():
    item = {"signature": {"real": "20", "index_1_based": "10"}, "misconception": "index_1_based"}
    assert simulate("clean", item, random.Random(7)) == simulate("clean", item, random.Random(7))


def test_clean_student_uses_misconception_prediction():
    item = {"signature": {"real": "20", "index_1_based": "10"}, "misconception": "index_1_based"}
    result = simulate("clean", item, random.Random(1))
    assert result["answer"] == "10"


def test_patcher_and_true_learner_differ_on_transfer():
    item = {"signature": {"real": "20", "index_1_based": "10"}, "misconception": "index_1_based", "intervened": True, "is_transfer": True}
    patcher = simulate("patcher", item, random.Random(1))
    learner = simulate("true_learner", item, random.Random(1))
    assert patcher["answer"] == "10"
    assert learner["answer"] == "20"
