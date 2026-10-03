from engine.signature import signature
def test_signature_runs():
    result = signature("print(1)")
    assert result["real"] == "1"
    assert "range_1_to_n" in result
