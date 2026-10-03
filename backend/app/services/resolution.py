def next_state(state, evidence, item_kind, posterior_m):
    """Advance one misconception using only evidence from informative items.

    ``evidence`` is a copy of the persisted evidence object. Passing on an item
    only counts when it distinguishes this misconception from correct Python.
    """
    valid_states = {"active", "intervened", "suspected_resolved", "confirmed_resolved", "relapsed"}
    if state not in valid_states:
        state = "active"
    updated = {
        **evidence,
        "discriminator_passes": int(evidence.get("discriminator_passes", 0)),
        "surface_forms": list(evidence.get("surface_forms", [])),
        "delayed_retest": bool(evidence.get("delayed_retest", False)),
    }

    # Delivery is recorded by the intervention route, then the next item is evidence.
    if evidence.get("intervention_delivered") and state in {"active", "relapsed"}:
        return "intervened", updated

    if state == "confirmed_resolved":
        if posterior_m >= 0.4:
            return "relapsed", updated
        return state, updated

    if item_kind in {"discriminator", "transfer", "retest"}:
        informative = bool(evidence.get("informative", True))
        passed = bool(evidence.get("passed", False))
        if item_kind == "discriminator" and informative and passed:
            updated["discriminator_passes"] += 1
        if item_kind in {"discriminator", "transfer"} and informative:
            surface = evidence.get("surface_form")
            if surface and surface not in updated["surface_forms"]:
                updated["surface_forms"].append(surface)
        if item_kind == "retest" and informative and passed:
            updated["delayed_retest"] = True

        if not passed and informative and posterior_m >= 0.4:
            return ("relapsed" if state == "confirmed_resolved" else "active"), updated

    if posterior_m >= 0.4:
        return ("relapsed" if state == "confirmed_resolved" else "active"), updated

    has_new_pass = item_kind in {"discriminator", "transfer"} and evidence.get("informative", True) and evidence.get("passed", False)
    if state in {"intervened", "suspected_resolved"} and has_new_pass and posterior_m < 0.15:
        if (updated["discriminator_passes"] >= 3
                and len(updated["surface_forms"]) >= 2
                and updated["delayed_retest"]):
            return "confirmed_resolved", updated
        return "suspected_resolved", updated

    # Retest can supply the final piece after the third discriminator/transfer pass.
    if (state == "suspected_resolved" and item_kind == "retest"
            and updated["delayed_retest"] and posterior_m < 0.15
            and updated["discriminator_passes"] >= 3
            and len(updated["surface_forms"]) >= 2):
        return "confirmed_resolved", updated
    return state, updated
