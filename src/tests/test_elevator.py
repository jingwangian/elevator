import pytest
from apps.elevator import Elevator

@pytest.fixture
def elevator():
    return Elevator(number=0)


class TestElevator:
    def test_init(self):
        e = Elevator(number=0)
        assert e.current_floor == 0
        assert e.lowest_floor == -1
        assert e.highest_floor == 10

    def test_stop(self, elevator):
        elevator.request_stop(-1)
        elevator.request_stop(3)
        elevator.request_stop(5)

        steps = elevator.get_steps()

        assert steps == ['DOWN_1', 'OPEN_DOOR', 'CLOSE_DOOR', 'UP_1', 'UP_1', 'UP_1', 'UP_1',
                         'OPEN_DOOR', 'CLOSE_DOOR', 'UP_1', 'UP_1', 'OPEN_DOOR', 'CLOSE_DOOR']

    def test_up(self, elevator):
        elevator.request_up(-1)
        elevator.request_stop(3)

        steps = elevator.get_steps()

        assert steps == ['DOWN_1', 'OPEN_DOOR', 'CLOSE_DOOR', 'UP_1', 'UP_1', 'UP_1', 'UP_1',
                         'OPEN_DOOR', 'CLOSE_DOOR']

    def test_down(self, elevator):
        elevator = Elevator(number=0)

        elevator.request_down(3)
        elevator.request_stop(-1)

        steps = elevator.get_steps()

        assert steps == ['UP_1', 'UP_1', 'UP_1', 'OPEN_DOOR', 'CLOSE_DOOR',
                         'DOWN_1', 'DOWN_1', 'DOWN_1', 'DOWN_1', 'OPEN_DOOR', 'CLOSE_DOOR']

    def test_mix_action(self, elevator):
        elevator.current_floor = 2

        elevator.request_stop(1)
        elevator.request_stop(0)
        elevator.request_up(2)
        elevator.request_down(4)
        elevator.request_stop(7)

        steps = elevator.get_steps()

        assert steps == [
            'DOWN_1', 'OPEN_DOOR', 'CLOSE_DOOR', 'DOWN_1', 'OPEN_DOOR', 'CLOSE_DOOR', 'UP_1', 'UP_1', 'OPEN_DOOR',
            'CLOSE_DOOR', 'UP_1', 'UP_1', 'UP_1', 'UP_1', 'UP_1', 'OPEN_DOOR', 'CLOSE_DOOR', 'DOWN_1', 'DOWN_1',
            'DOWN_1', 'OPEN_DOOR', 'CLOSE_DOOR']
