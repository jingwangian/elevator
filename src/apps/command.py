from collections import defaultdict


class Request:
    def __init__(self, request_type, floor_number):
        self.floor = floor_number
        self.request_type = request_type


class CommandList:
    """Keep all the command for the elevator

    The command for each floor includes:
        STOP: People want to stop at that floor
        UP: People want to pickup at that floor and go up
        DOWN: People want to pickup at that floor and go down
    """

    STOP = 'STOP'
    UP = 'UP'
    DOWN = 'DOWN'

    def __init__(self):
        self.floors = defaultdict(set)
        self.requests = []

    def __str__(self):
        return str(self.floors)

    def set_stop(self, number):
        """Set request STOP  state in that floor
        """

        self.floors[number].add(self.STOP)
        request = Request(self.STOP, number)
        self.requests.append(request)

    def set_up(self, number):
        """Set request go up state in that floor
        """

        self.floors[number].add(self.UP)
        request = Request(self.STOP, number)
        self.requests.append(request)

    def set_down(self, number):
        """Set request go down state in that floor
        """

        self.floors[number].add(self.DOWN)
        request = Request(self.DOWN, number)
        self.requests.append(request)

    def clear_stop(self, number):
        """Clear request STOP state in that floor
        """

        if self.STOP in self.floors[number]:
            self.floors[number].remove(self.STOP)

        if len(self.floors[number]) == 0:
            del self.floors[number]

    def clear_up(self, number):
        """Clear request go up state in that floor
        """

        if self.UP in self.floors[number]:
            self.floors[number].remove(self.UP)

        if len(self.floors[number]) == 0:
            del self.floors[number]

    def clear_down(self, number):
        """Clear request go down state in that floor
        """

        if self.DOWN in self.floors[number]:
            self.floors[number].remove(self.DOWN)

        if len(self.floors[number]) == 0:
            del self.floors[number]

    def has_stop_request_at(self, number):
        """Check the specific floor need stop or not
        """

        return self.STOP in self.floors[number]

    def has_up_request_at(self, number):
        """Check the specific floor has pickup and go up request or not
        """

        return self.UP in self.floors[number]

    def has_down_request_at(self, number):
        """Check the specific floor has pickup and go down request or not
        """

        return self.DOWN in self.floors[number]

    def has_any_request_at(self, number):
        return len(self.floors[number]) > 0

    def get_highest_floor_number(self):
        """Return the highest floor number from all requests
        """

        floor_number_list = []
        for floor_number in self.floors.keys():
            if self.has_any_request_at(floor_number):
                floor_number_list.append(floor_number)

        if not floor_number_list:
            return -1000

        return max(floor_number_list)
        # return max([floor_number for floor_number in self.floors.keys() if len(self.floors[floor_number])])

    def get_lowest_floor_number(self):
        """Return the lowest floor number from all requests
        """

        floor_number_list = []
        for floor_number in self.floors.keys():
            if self.has_any_request_at(floor_number):
                floor_number_list.append(floor_number)

        if not floor_number_list:
            return 1000

        return min(floor_number_list)

    def copy(self):
        """Return a deep copy of commands
        """

        commands = CommandList()

        for floor_number in self.floors:
            if self.has_up_request_at(floor_number):
                commands.set_up(floor_number)

            if self.has_down_request_at(floor_number):
                commands.set_down(floor_number)

            if self.has_stop_request_at(floor_number):
                commands.set_stop(floor_number)

        return commands

    def is_empty(self):
        return len([floor for floor in self.floors if len(self.floors[floor])]) == 0

    def clear_requests(self):
        self.requests = []
