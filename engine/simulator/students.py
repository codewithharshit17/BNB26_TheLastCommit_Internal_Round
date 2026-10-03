def simulate(student_type, item, rng):
    """Simulate clean, noisy, mixed, unknown, patcher, or true_learner students."""
    if student_type not in {"clean", "noisy", "mixed", "unknown", "patcher", "true_learner"}:
        raise ValueError("unknown student type")
    raise NotImplementedError("TODO(Sukhada): implement student simulation")
