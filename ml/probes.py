import math
from collections.abc import Mapping

from .posterior import entropy, lik, update


def _safe_prior(posterior):
    """Return a finite, normalized copy of a posterior distribution."""
    if not isinstance(posterior, Mapping):
        return {}
    cleaned = {}
    for hypothesis, probability in posterior.items():
        try:
            value = float(probability)
        except (TypeError, ValueError):
            value = 0.0
        cleaned[hypothesis] = value if math.isfinite(value) and value > 0 else 0.0
    total = sum(cleaned.values())
    if not cleaned:
        return {}
    if total <= 0 or not math.isfinite(total):
        share = 1 / len(cleaned)
        return {hypothesis: share for hypothesis in cleaned}
    return {hypothesis: value / total for hypothesis, value in cleaned.items()}


def _safe_signature(signature):
    if not isinstance(signature, Mapping):
        return {}
    return {
        hypothesis: prediction
        for hypothesis, prediction in signature.items()
        if isinstance(hypothesis, str) and isinstance(prediction, str)
    }


def _likelihood(hypothesis, answer, signature, confidence):
    if hypothesis == "correct":
        return lik(answer, signature.get("real"), confidence, "correct")
    if hypothesis == "unknown":
        predictions = {
            prediction
            for name, prediction in signature.items()
            if name != "unknown"
        }
        return 0.85 if answer not in predictions else 0.03
    return lik(answer, signature.get(hypothesis), confidence, "misconception")


def info_gain(posterior, signature, confidence=3):
    """Compute expected entropy reduction for one candidate signature.

    Candidate signatures use the engine format: ``real`` plus misconception
    IDs mapped to predicted output strings. Invalid signatures have zero gain.
    """
    prior = _safe_prior(posterior)
    signature = _safe_signature(signature)
    if not prior or not signature:
        return 0.0

    possible_answers = set(signature.values())
    possible_answers.add("__other__")
    current_entropy = entropy(prior)
    expected_entropy = 0.0
    outcome_weights = {}
    for answer in possible_answers:
        outcome_weights[answer] = sum(
            prior[hypothesis] * _likelihood(hypothesis, answer, signature, confidence)
            for hypothesis in prior
        )

    total_outcome_weight = sum(outcome_weights.values())
    if total_outcome_weight <= 0 or not math.isfinite(total_outcome_weight):
        return 0.0

    for answer, outcome_weight in outcome_weights.items():
        if outcome_weight <= 0 or not math.isfinite(outcome_weight):
            continue
        probability = outcome_weight / total_outcome_weight
        posterior_after_answer = update(prior, signature, answer, confidence)
        expected_entropy += probability * entropy(posterior_after_answer)

    gain = current_entropy - expected_entropy
    return max(0.0, gain) if math.isfinite(gain) else 0.0


def _candidate_signature(candidate):
    """Extract a signature from a bare signature or an item wrapper."""
    if isinstance(candidate, Mapping):
        for key in ("signature", "sig"):
            value = candidate.get(key)
            if isinstance(value, Mapping):
                return value
        return candidate if "real" in candidate else {}
    if callable(candidate):
        try:
            value = candidate()
        except Exception:
            return {}
        return value if isinstance(value, Mapping) else {}
    return {}


def select_probe(posterior, candidate_items, confidence=3):
    """Return the highest-information candidate, preserving input-order ties."""
    if not candidate_items:
        return None
    best_candidate = None
    best_gain = float("-inf")
    for candidate in candidate_items:
        gain = info_gain(posterior, _candidate_signature(candidate), confidence)
        if gain > best_gain:
            best_candidate = candidate
            best_gain = gain
    return best_candidate


def next_probe(posterior, item_bank):
    """Select the next probe from a posterior and item bank."""
    return select_probe(posterior, item_bank)
