from ml.posterior import update
def test_update_normalizes():
    result = update({"correct": 0.5, "unknown": 0.5}, {"real": "1", "unknown": "2"}, "1", 3)
    assert abs(sum(result.values()) - 1) < 1e-9
