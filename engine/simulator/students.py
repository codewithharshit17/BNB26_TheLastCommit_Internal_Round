import random

from engine.signature import signature as make_signature


STUDENT_TYPES = {"clean", "noisy", "mixed", "unknown", "patcher", "true_learner"}


def _signature(item):
    value = item.get("signature") if isinstance(item, dict) else None
    if isinstance(value, dict):
        return value
    code = item.get("code", "") if isinstance(item, dict) else ""
    return make_signature(code)


def _targets(item):
    if not isinstance(item, dict):
        return []
    values = item.get("misconceptions", item.get("targets"))
    if values is None:
        values = [item.get("misconception", item.get("target"))]
    if isinstance(values, str):
        values = [values]
    return [str(value) for value in values if value is not None]


def _random_wrong(signature, real, rng):
    choices = sorted({value for key, value in signature.items() if key != "real" and value != real})
    return rng.choice(choices) if choices else "unknown"


def simulate(student_type, item, rng):
    """Return one reproducible attempt for a simple simulated student type."""
    if student_type not in STUDENT_TYPES:
        raise ValueError("unknown student type")
    if not isinstance(rng, random.Random):
        raise TypeError("rng must be random.Random")

    sig = _signature(item)
    real = str(sig.get("real", ""))
    targets = _targets(item)
    target = targets[0] if targets else None
    is_transfer = bool(item.get("is_transfer", False)) if isinstance(item, dict) else False
    intervened = bool(item.get("intervened", False)) if isinstance(item, dict) else False

    if student_type == "true_learner" and intervened:
        answer = real
    elif student_type == "patcher" and intervened:
        if not is_transfer:
            answer = real
        else:
            predicted = sig.get(target)
            answer = str(predicted) if predicted is not None and str(predicted) != real else real
    elif student_type == "noisy" and rng.random() < 0.30:
        answer = _random_wrong(sig, real, rng)
    elif student_type == "mixed":
        predictions = [sig.get(misconception) for misconception in targets]
        predictions = [str(value) for value in predictions if value is not None and str(value) != real]
        answer = rng.choice(predictions) if predictions and rng.random() < 0.85 else real
    else:
        predicted = sig.get(target) if target else None
        if predicted is not None and str(predicted) != real and rng.random() < 0.85:
            answer = str(predicted)
        else:
            answer = real

    return {
        "item_id": item.get("item_id") if isinstance(item, dict) else None,
        "code": item.get("code", "") if isinstance(item, dict) else "",
        "signature": sig,
        "answer": answer,
        "real_output": real,
        "confidence": rng.randint(1, 5),
        "family": item.get("family") if isinstance(item, dict) else None,
        "misconception": target,
        "student_type": student_type,
        "is_transfer": is_transfer,
        "intervened": intervened,
    }
