import json
import logging
import inspect

logger = logging.getLogger("aviara")

def info(message, user_id=None):
    if user_id is None:
        user_id = "None"
    function_name = inspect.stack()[1][3]
    logger.info({"function_name": function_name, "user_id":user_id, "info": message})


def warning(message, user_id=None):
    if user_id is None:
        user_id = "None"
    function_name = inspect.stack()[1][3]
    logger.warning({"function_name": function_name, "user_id":user_id, "info": message})

def error(message, user_id=None):
    if user_id is None:
        user_id = "None"
    function_name = inspect.stack()[1][3]
    logger.error({"function_name": function_name, "user_id":user_id, "info": message})


class JsonFormatter(logging.Formatter):

    def format(self, record):
        log_record = {
            'level': record.levelname,
            'time': self.formatTime(record, self.datefmt),
            'message': record.getMessage(),
            'module': record.module,
            'lineno': record.lineno,
        }
        return json.dumps(log_record)