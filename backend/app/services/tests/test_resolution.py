from backend.app.services.resolution import next_state


def blank_evidence():
    return {"discriminator_passes": 0, "surface_forms": [], "delayed_retest": False}


def test_correct_answer_on_non_discriminator_does_not_resolve():
    state, evidence = next_state("intervened", {**blank_evidence(), "passed": True, "informative": False}, "discriminator", 0.05)
    assert state == "intervened"
    assert evidence["discriminator_passes"] == 0


def test_three_discriminators_two_surfaces_and_delayed_retest_confirm():
    state, evidence = "intervened", blank_evidence()
    for surface in ("a[0]", "values[1]", "name[2]"):
        state, evidence = next_state(state, {**evidence, "passed": True, "informative": True, "surface_form": surface}, "discriminator", 0.1)
    assert state == "suspected_resolved"
    state, evidence = next_state(state, {**evidence, "passed": True, "informative": True}, "retest", 0.1)
    assert state == "confirmed_resolved"
    assert evidence["discriminator_passes"] == 3
    assert len(evidence["surface_forms"]) == 3
    assert evidence["delayed_retest"] is True


def test_misconception_can_relapse_after_confirmation():
    state, _ = next_state("confirmed_resolved", blank_evidence(), "diagnostic", 0.4)
    assert state == "relapsed"


def test_patcher_stays_suspected_without_required_evidence():
    evidence = {**blank_evidence(), "discriminator_passes": 1, "surface_forms": ["a[0]"], "passed": True, "informative": True, "surface_form": "a[0]"}
    state, _ = next_state("intervened", evidence, "transfer", 0.1)
    assert state == "suspected_resolved"
