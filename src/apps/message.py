from datetime import datetime

import os
import redis
import json


class CommandType:
    STOP = 1
    UP = 2
    DOWN = 3


class MessageQueue:
    def __init__(self):
        host = os.getenv("REDIS_HOSTS", "localhost")
        self.redis = redis.StrictRedis(host=host, port=6379, db=0)
        self.command_topic = 'ELEVATOR_COMMAND'
        self.status_topic = 'ELEVATOR_CH'

    def receive_command(self):
        value = self.redis.rpop(self.command_topic)

        if value:
            return json.loads(value)

    def send_command(self, command_type, floor_number):
        data = {'command': command_type, 'number': floor_number}

        self.redis.lpush(self.command_topic, json.dumps(data))

    def clear_command(self):
        while 1:
            if self.redis.lpop(self.command_topic) is None:
                break

    def send_status(self, floor, action, status):
        t = datetime.now().isoformat()
        data = {'time': t, 'floor': floor, 'action': action, 'status': status}

        self.redis.lpush(self.status_topic, json.dumps(data))

    def get_status(self):
        ret = self.redis.rpop(self.status_topic)

        if ret:
            return json.loads(ret)
