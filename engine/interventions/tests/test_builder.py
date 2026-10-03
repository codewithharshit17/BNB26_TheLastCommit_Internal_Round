import pytest
from engine.interventions.builder import build
def test_builder_stub():
    with pytest.raises(NotImplementedError): build()
