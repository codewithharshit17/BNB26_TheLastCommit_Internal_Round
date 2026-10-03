import math
SLIP = lambda conf: 0.20 - 0.035*conf          # confident wrong answers are rarely slips

def lik(answer, pred, conf, kind):
    if kind == "correct":      return (1-SLIP(conf)) if answer == pred else SLIP(conf)/4
    if kind == "misconception":return 0.85 if answer == pred else 0.04
    return 0.30                                  # "unknown": explains any answer weakly

def update(prior, sig, answer, conf):
    """prior: {hyp: p}; sig: {'real':..., mid:...}; hyps = 'correct', misconception ids, 'unknown'"""
    post = {}
    for h, p in prior.items():
        if h == "correct": l = lik(answer, sig["real"], conf, "correct")
        elif h == "unknown": 
            known = set(sig.values()); l = 0.30 if answer not in known else 0.03
        else: l = lik(answer, sig[h], conf, "misconception")
        post[h] = p * l
    z = sum(post.values()); return {h: v/z for h, v in post.items()}

def entropy(d): return -sum(p*math.log2(p) for p in d.values() if p > 0)

def info_gain(post, sig, conf=3):
    """expected entropy reduction from asking a probe whose signature is `sig`"""
    answers = set(sig.values()) | {"__other__"}
    exp_h = 0
    for a in answers:
        pa = sum(post[h] * lik(a, sig.get(h, "__x__"), conf, "correct" if h=="correct" else "misconception" if h!="unknown" else "u")
                 for h in post)
        if pa == 0: continue
        newpost = update(post, {**sig, "unknown": "__none__"} if "unknown" not in sig else sig, a, conf)
        exp_h += pa * entropy(newpost)
    return entropy(post) - exp_h
