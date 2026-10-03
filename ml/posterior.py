import math
from collections.abc import Mapping


SLIP = lambda conf: 0.20 - 0.035 * conf


def _confidence(conf):
    """Return a finite confidence value in the supported 1-5 range."""
    try:
        value = float(conf)
    except (TypeError, ValueError):
        return 3.0
    if not math.isfinite(value):
        return 3.0
    return min(5.0, max(1.0, value))


def lik(answer, pred, conf, kind):
    """Return the starter likelihood for a hypothesis and observed answer."""
    confidence = _confidence(conf)
    if kind == "correct":
        slip = SLIP(confidence)
        return (1 - slip) if answer == pred else slip / 4
    if kind == "misconception":
        return 0.85 if answer == pred else 0.04
    return 0.30


def _clean_prior(prior):
    if not isinstance(prior, Mapping):
        return {"correct": 0.5, "unknown": 0.5}

    cleaned = {}
    for hypothesis, probability in prior.items():
        try:
            value = float(probability)
        except (TypeError, ValueError):
            value = 0.0
        cleaned[hypothesis] = value if math.isfinite(value) and value > 0 else 0.0

    if not cleaned:
        return {"correct": 0.5, "unknown": 0.5}
    if sum(cleaned.values()) == 0:
        share = 1 / len(cleaned)
        return {hypothesis: share for hypothesis in cleaned}
    return cleaned


def update(prior, sig, answer, conf):
    """Bayes-update hypothesis probabilities from a signature of predictions.

    ``sig`` is the engine format: ``real`` plus misconception IDs mapped to
    their believed output. Missing or malformed predictions are simply treated
    as non-matches. The prior determines the supported hypothesis set.
    """
    prior = _clean_prior(prior)
    sig = sig if isinstance(sig, Mapping) else {}
    predictions = {
        prediction
        for hypothesis, prediction in sig.items()
        if hypothesis != "unknown" and isinstance(prediction, str)
    }
    has_match = answer in predictions

    likelihoods = {}
    for hypothesis in prior:
        if hypothesis == "correct":
            likelihoods[hypothesis] = lik(answer, sig.get("real"), conf, "correct")
        elif hypothesis == "unknown":
            # Unknown explains answers that none of the available interpreters
            # predicted; otherwise it is weak background noise.
            likelihoods[hypothesis] = 0.85 if not has_match else 0.03
        else:
            likelihoods[hypothesis] = lik(answer, sig.get(hypothesis), conf, "misconception")

    post = {hypothesis: prior[hypothesis] * likelihoods[hypothesis] for hypothesis in prior}
    normalizer = sum(post.values())
    if not math.isfinite(normalizer) or normalizer <= 0:
        share = 1 / len(post)
        return {hypothesis: share for hypothesis in post}
    return {hypothesis: value / normalizer for hypothesis, value in post.items()}
def entropy(distribution):
    return -sum(probability * math.log2(probability) for probability in distribution.values() if probability > 0)
def info_gain(post, sig, conf=3):
    answers = sorted(set(sig.values()) | {"__other__"})
    expected_entropy = 0
    for answer in answers:
        probability = sum(post[h] * lik(answer, sig.get(h, "__x__"), conf, "correct" if h == "correct" else "misconception" if h != "unknown" else "u") for h in post)
        if probability == 0: continue
        expected_entropy += probability * entropy(update(post, {**sig, "unknown": "__none__"} if "unknown" not in sig else sig, answer, conf))
    return entropy(post) - expected_entropy
