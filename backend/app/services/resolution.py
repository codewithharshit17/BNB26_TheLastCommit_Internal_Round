def next_state(state, evidence, item_kind, posterior_m):
    """State machine: active -> intervened -> suspected_resolved -> confirmed_resolved; any failed delayed retest can relapse."""
    raise NotImplementedError("TODO(Aneesh): implement misconception resolution state machine")
