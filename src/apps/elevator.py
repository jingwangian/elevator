from enum import Enum
from collections import defaultdict
import time
import logging

from apps.command import CommandList
from apps.message import MessageQueue


DIRECTION_UP = 'UP'
DIRECTION_DOWN = 'DOWN'

STEP_EXECUTE_TIME = 2

STEP2ACTION = {
    'UP_1': 'UP',
    'DOWN_1': 'DOWN',
    'OPEN_DOOR': 'OPEN_DOOR',
    'CLOSE_DOOR': 'CLOSE_DOOR',
    'STOP': 'STOP'
}

logger = logging.getLogger(__name__)


class Elevator:
    STOP = 1
    MOVING_UP = 2
    MOVING_DOWN = 3

    def __init__(self, number=0, current_floor=0, lowest_floor=-1, highest_floor=10):
        self.number = number
        self.lowest_floor = lowest_floor
        self.highest_floor = highest_floor

        self.queue = MessageQueue()
        self.enabled_notify = False

        self.status = Elevator.STOP
        self.current_floor = current_floor

        self.commands = CommandList()

        self.debug = False

    def request_stop(self, floor_number):
        """People inside elevator select the floor to stop

        Args:
            floor_number (int): floor number
        """

        self.commands.set_stop(floor_number)

    def request_down(self, floor_number):
        """People outside calling elevator to pick up and go down

        Args:
            floor_number (int): floor number
        """
        self.commands.set_down(floor_number)

    def request_up(self, floor_number):
        """People outside calling elevator to pick up and go up

        Args:
            floor_number (int): floor number
        """
        self.commands.set_up(floor_number)

    def notify(self, step):
        """Send status message to the monitor

        Args:
            step (string): the action step to be send
        """
        if not self.enabled_notify:
            return

        action = STEP2ACTION[step]
        self.queue.send_status(self.current_floor, action, self.status)

    def move_one_step(self):
        """Move one step from steps plan and change the status
        """

        steps = self.get_steps()

        if len(steps) == 0:
            return

        for step in steps:
            self.notify(step)
            logger.info(f'Execute action: {step} at current_floor: {self.current_floor}')
            time.sleep(STEP_EXECUTE_TIME)
            if step == 'UP_1':
                # Clear the floor which is left
                self.commands.clear_stop(self.current_floor)
                self.commands.clear_up(self.current_floor)
                self.current_floor += 1

                self.status = Elevator.MOVING_UP
                break
            elif step == 'DOWN_1':
                # Clear the floor which is left
                self.commands.clear_stop(self.current_floor)
                self.commands.clear_down(self.current_floor)
                self.current_floor -= 1

                self.status = Elevator.MOVING_DOWN
                time.sleep(STEP_EXECUTE_TIME)
                break
            elif step == 'CLOSE_DOOR':
                if self.status == Elevator.MOVING_DOWN:
                    self.commands.clear_down(self.current_floor)
                else:
                    self.commands.clear_up(self.current_floor)

                self.commands.clear_stop(self.current_floor)

                time.sleep(STEP_EXECUTE_TIME)
                break
            elif step == 'OPEN_DOOR':
                time.sleep(STEP_EXECUTE_TIME)

        return True

    def get_commands(self):
        """Get the command from the controller
        """
        while True:
            result = self.queue.receive_command()
            if not result:
                break

            logger.info(f'Received command: {result}', result)

            if result['command'] == 'STOP':
                self.request_stop(result['number'])
            elif result['command'] == 'UP':
                self.request_up(result['number'])
            elif result['command'] == 'DOWN':
                self.request_down(result['number'])

    def run(self):
        """Move the elevator accordint to the steps plan
        """

        self.enabled_notify = True
        while True:
            self.get_commands()
            steps = self.get_steps()
            if len(steps) == 0:
                if self.status != self.STOP:
                    self.status = self.STOP
                    self.commands.clear_requests()
                    self.notify('STOP')
                time.sleep(1)

            self.move_one_step()

    def decide_move_direction(self):
        """Decide which direction is going firstly

        If first request comes from the upper floor, then the elevator will
        move up direction firstly.

        return: DIRECTION_UP: go_up, DIRECTION_DOWN: go_down
        """

        if self.status == Elevator.MOVING_UP:
            return DIRECTION_UP

        if self.status == Elevator.MOVING_DOWN:
            return DIRECTION_DOWN

        for floor in [req.floor for req in self.commands.requests]:
            if floor > self.current_floor:
                self.status = Elevator.MOVING_UP
                return DIRECTION_UP
            elif floor < self.current_floor:
                self.status = Elevator.MOVING_DOWN
                return DIRECTION_DOWN

    def up_direction_steps(self, start_floor, commands: CommandList):
        """Get all steps for the moving up direction from the start floor

        Args:
            start_floor (int): the floor number from which to move up
            commands (CommandList): the command list

        Returns:
            [tuple]: 
                First is the steps list;
                Second is the hightest floor number to be arrived
        """

        if commands.is_empty():
            return [], start_floor

        plans = []
        hightest_stop_floor = commands.get_highest_floor_number()

        if start_floor > hightest_stop_floor:
            self.status = self.MOVING_DOWN
            return [], start_floor

        if start_floor == hightest_stop_floor:
            if ((self.commands.has_stop_request_at(start_floor) is False)
                    and (self.commands.has_up_request_at(start_floor) is False)):
                self.status = self.MOVING_DOWN
                return [], start_floor

        for floor_number in range(start_floor, hightest_stop_floor + 1):
            if floor_number > start_floor:
                if self.debug:
                    logger.debug('UP_1 to floor : {floor_number}')
                plans.append('UP_1')

            if commands.has_stop_request_at(floor_number) or commands.has_up_request_at(floor_number):
                plans.append('OPEN_DOOR')
                plans.append('CLOSE_DOOR')
                if self.debug:
                    logger.debug(f'OPEN_CLOSE_DOOR at {floor_number}')

                commands.clear_stop(floor_number)
                commands.clear_up(floor_number)

        return plans, hightest_stop_floor

    def down_direction_plan(self, start_floor, commands: CommandList):
        """Get all steps for the moving down direction from the start floor

        Args:
            start_floor (int): the floor number from which to move down
            commands (CommandList): the command list

        Returns:
            [tuple]: 
                First is the steps list;
                Second is the lowest floor number to be arrived
        """

        if commands.is_empty():
            return [], start_floor

        plans = []
        lowerest_stop_floor = commands.get_lowest_floor_number()

        if start_floor < lowerest_stop_floor:
            self.status = self.MOVING_UP
            return [], start_floor

        if start_floor == lowerest_stop_floor:
            if ((self.commands.has_stop_request_at(start_floor) is False)
                    and (self.commands.has_down_request_at(start_floor) is False)):
                self.status = self.MOVING_UP
                return [], start_floor

        for floor_number in range(start_floor, lowerest_stop_floor - 1, -1):
            if floor_number < start_floor:
                if self.debug:
                    logger.debug(f'DOWN_1 to floor : {floor_number}')
                plans.append('DOWN_1')

            if commands.has_stop_request_at(floor_number) or commands.has_down_request_at(floor_number):
                plans.append('OPEN_DOOR')
                plans.append('CLOSE_DOOR')
                if self.debug:
                    logger.debug(f'OPEN_CLOSE_DOOR at {floor_number}')

                commands.clear_stop(floor_number)
                commands.clear_down(floor_number)

        return plans, lowerest_stop_floor

    def get_steps(self):
        plans = []
        current_floor = self.current_floor

        # make a copy here because we don't really consume the command here
        command_list = self.commands.copy()

        if command_list.is_empty():
            return plans

        if self.decide_move_direction() == DIRECTION_UP:
            return_steps, current_floor = self.up_direction_steps(current_floor, command_list)
            plans.extend(return_steps)
            return_steps, current_floor = self.down_direction_plan(current_floor, command_list)
            plans.extend(return_steps)
            return_steps, current_floor = self.up_direction_steps(current_floor, command_list)
            plans.extend(return_steps)
        else:
            return_steps, current_floor = self.down_direction_plan(current_floor, command_list)
            plans.extend(return_steps)
            return_steps, current_floor = self.up_direction_steps(current_floor, command_list)
            plans.extend(return_steps)
            return_steps, current_floor = self.down_direction_plan(current_floor, command_list)
            plans.extend(return_steps)

        assert command_list.is_empty()
        return plans
