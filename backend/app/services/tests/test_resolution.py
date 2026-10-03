import pytest
from backend.app.services.resolution import next_state
def test_resolution_is_explicit_stub():
    with pytest.raises(NotImplementedError): next_state("active", {}, "diagnostic", 0.5)
