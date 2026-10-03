from engine.rewrites import REGISTRY
def test_registry_excludes_held_out_from_live(): assert all(not item["held_out"] for item in REGISTRY if item["id"] == "index_from_m1") is False
