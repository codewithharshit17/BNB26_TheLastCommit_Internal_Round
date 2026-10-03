import pytest
from engine.simulator.students import simulate
def test_student_stub():
    with pytest.raises(NotImplementedError): simulate("clean", {}, None)
