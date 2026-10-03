import math

SLIP = lambda conf: 0.20 - 0.035 * conf
def lik(answer, pred, conf, kind):
    if kind == "correct": return (1 - SLIP(conf)) if answer == pred else SLIP(conf) / 4
    if kind == "misconception": return 0.85 if answer == pred else 0.04
    return 0.30
def update(prior, sig, answer, conf):
    post = {}
    for hypothesis, probability in prior.items():
        if hypothesis == "correct": likelihood = lik(answer, sig["real"], conf, "correct")
        elif hypothesis == "unknown":
            likelihood = 0.30 if answer not in set(sig.values()) else 0.03
        else: likelihood = lik(answer, sig[hypothesis], conf, "misconception")
        post[hypothesis] = probability * likelihood
    normalizer = sum(post.values())
    return {hypothesis: value / normalizer for hypothesis, value in post.items()}
def entropy(distribution):
    return -sum(probability * math.log2(probability) for probability in distribution.values() if probability > 0)
def info_gain(post, sig, conf=3):
    answers = set(sig.values()) | {"__other__"}
    expected_entropy = 0
    for answer in answers:
        probability = sum(post[h] * lik(answer, sig.get(h, "__x__"), conf, "correct" if h == "correct" else "misconception" if h != "unknown" else "u") for h in post)
        if probability == 0: continue
        expected_entropy += probability * entropy(update(post, {**sig, "unknown": "__none__"} if "unknown" not in sig else sig, answer, conf))
    return entropy(post) - expected_entropy
