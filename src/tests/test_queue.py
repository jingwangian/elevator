from apps.message import MessageQueue, CommandType


class TestMessageQueue:
    def test_init(self):
        queue = MessageQueue()

        assert queue.command_topic == 'ELEVATOR_COMMAND'
        assert queue.status_topic == 'ELEVATOR_CH'

    def test_send_command(self):
        queue = MessageQueue()
        queue.clear_command()

        queue.send_command(CommandType.STOP, 1)
        queue.send_command(CommandType.UP, 2)
        queue.send_command(CommandType.DOWN, 3)

    def test_receive_command(self):
        queue = MessageQueue()
        result = queue.receive_command()

        assert result == {'command': CommandType.STOP, 'number': 1}

        result = queue.receive_command()
        assert result == {'command': CommandType.UP, 'number': 2}

        result = queue.receive_command()
        assert result == {'command': CommandType.DOWN, 'number': 3}

