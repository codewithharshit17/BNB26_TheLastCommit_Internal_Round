from engine import *
from posterior import *
if __name__ == "__main__":
    items = {
     "range":  "for i in range(3):\n    print(i)",
     "upper":  "name = 'hello'\nname.upper()\nprint(name)",
     "idx":    "a = [10, 20, 30]\nprint(a[1])",
     "alias":  "a = [1, 2, 3]\nb = a\na.append(4)\nprint(b)",
     "prec":   "print(10 + 20 + 30 / 3)",
     "evil":   "import os\nprint(1)",
     "loop":   "while True:\n    pass",
    }
    for k, s in items.items():
        print(k, signature(s))
    # posterior demo: student answers "20" to a[1] (they think 1-based => 10? no) 
    hyps = ["correct","index_1_based","index_from_m1","range_1_to_n","unknown"]
    prior = {h: 1/len(hyps) for h in hyps}
    s1 = signature("a = [10, 20, 30]\nprint(a[1])")
    print("sig", s1)
    post = update(prior, {**s1}, "10", 5); print({k: round(v,3) for k,v in post.items()})
    s2 = signature("a = [10, 20, 30]\nprint(a[2])")
    print("IG probe a[1]:", round(info_gain(post, s1),3), " IG probe a[2]:", round(info_gain(post, s2),3))
