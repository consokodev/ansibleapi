# -*- coding: utf-8 -*-
from api.exceptions import DVTException


class TaskError(DVTException):
    _default_message = "{}"

    def __init__(self, message):
        msg = self._default_message.format(message)
        super(TaskError, self).__init__(msg)