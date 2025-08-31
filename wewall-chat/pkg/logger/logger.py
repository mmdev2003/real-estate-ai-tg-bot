import os
from typing import Optional, Dict

import pytz
import queue
import atexit
import logging
import traceback
import ujson as json
from datetime import datetime
from logging.handlers import QueueHandler, QueueListener

logger = logging.getLogger("logger")


class ContextLogger:
    def __init__(self, base_logger: logging.Logger, context):
        self.base_logger = base_logger
        self.context = context

    def info(self, msg: str | dict, extra: Optional[Dict] = None):
        merged_extra = {**self.context, **(extra or {})}
        self.base_logger.info(msg, extra=merged_extra, stacklevel=2)

    def warning(self, msg: str, extra: Optional[Dict] = None):
        merged_extra = {**self.context, **(extra or {})}
        self.base_logger.warning(msg, extra=merged_extra, stacklevel=2)

    def error(self, msg: str, exc_info=None, extra: Optional[Dict] = None):
        merged_extra = {**self.context, **(extra or {})}
        self.base_logger.error(msg, exc_info=exc_info, extra=merged_extra, stacklevel=2)

    def debug(self, msg: str, extra: Optional[Dict] = None):
        merged_extra = {**self.context, **(extra or {})}
        self.base_logger.debug(msg, extra=merged_extra, stacklevel=2)


class DevFormatter(logging.Formatter):
    def __init__(self, root_path):
        super().__init__()
        self.root_path = root_path
        default_record_keys = list(logging.LogRecord("", 0, "", 0, "", (), None).__dict__)
        http_keys = ["duration_ms", "http_status", "request_id", "path", "method", "service_name"]
        tg_keys = ["tg_state_status", "tg_update_type", "tg_chat_id", "tg_user_name", "tg_user_message",
                   "tg_message_id", "tg_callback_data"]
        self.not_extra_keys = [
            *default_record_keys,
            *http_keys,
            *tg_keys,
            "lvl", "msg", "file", "traceback",
        ]
        self.record_keys = [
            *http_keys,
            *tg_keys,
        ]
        self.skip_keys = ["message"]

    def format(self, record: logging.LogRecord):
        if record.levelno == logging.ERROR:
            message = f"[{record.levelname}] {record.getMessage()}"
            if record.exc_info:
                exc_type, exc_value, exc_traceback = record.exc_info
                tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                message += "\n" + "".join(tb_lines)
            return message

        log_record = {
            "lvl": record.levelname,
            "msg": record.getMessage(),
        }

        if record.funcName != "logger_middleware":
            filePath = os.path.relpath(os.path.abspath(record.pathname), self.root_path)
            log_record["file"] = f"{filePath}:{record.funcName}:{record.lineno}"

        log_record["extra"] = {}
        for key, value in record.__dict__.items():
            if key in self.skip_keys:
                continue

            if key not in self.not_extra_keys:
                log_record["extra"][key] = value

            if key in self.record_keys:
                log_record[key] = value

        if not list(log_record["extra"]):
            del log_record["extra"]

        return json.dumps(log_record, ensure_ascii=False)


class ProdFormatter(logging.Formatter):
    def __init__(self, root_path):
        super().__init__()
        self.root_path = root_path
        self.timezone = pytz.timezone("UTC")
        default_record_keys = list(logging.LogRecord("", 0, "", 0, "", (), None).__dict__)
        http_keys = ["duration_ms", "http_status", "request_id", "path", "method", "service_name"]
        tg_keys = ["tg_state_status", "tg_update_type", "tg_chat_id", "tg_user_name", "tg_user_message",
                   "tg_message_id", "tg_callback_data"]
        self.not_extra_keys = [
            *default_record_keys,
            *http_keys,
            *tg_keys,
            "lvl", "msg", "file", "traceback",
        ]
        self.record_keys = [
            *http_keys,
            *tg_keys,
        ]
        self.skip_keys = ["message"]

    def format(self, record: logging.LogRecord):
        filePath = os.path.relpath(os.path.abspath(record.pathname), self.root_path)
        log_record = {
            "time": datetime.fromtimestamp(record.created, self.timezone).isoformat(),
            "lvl": record.levelname,
            "msg": record.getMessage(),
            "file": f"{filePath}:{record.funcName}:{record.lineno}"
        }

        if record.levelno == logging.ERROR:
            error_text = f"[{record.levelname}] {record.getMessage()}"
            if record.exc_info:
                exc_type, exc_value, exc_traceback = record.exc_info
                tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                error_text += "\n" + "".join(tb_lines)
            log_record["traceback"] = error_text

        log_record["extra"] = {}
        for key, value in record.__dict__.items():
            if key in self.skip_keys:
                continue

            if key not in self.not_extra_keys:
                log_record["extra"][key] = value

            if key in self.record_keys:
                log_record[key] = value

        if not list(log_record["extra"]):
            del log_record["extra"]

        return json.dumps(log_record, ensure_ascii=False)


def setup_logger(logger_type: str, root_path: str):
    if logger_type == "dev":
        setup_dev_logger(root_path)
    else:
        setup_prod_logger(root_path)


def setup_dev_logger(root_path: str):
    dev_logger = logging.getLogger("logger")
    handler = logging.StreamHandler()

    dev_logger.setLevel(logging.DEBUG)
    handler.setLevel(logging.DEBUG)

    handler.setFormatter(
        DevFormatter(root_path)
    )

    dev_logger.addHandler(handler)


def setup_prod_logger(root_path: str):
    prod_logger = logging.getLogger("logger")

    log_queue = queue.Queue(-1)
    queue_handler = QueueHandler(log_queue)

    prod_logger.setLevel(logging.DEBUG)
    prod_logger.addHandler(queue_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(ProdFormatter(root_path))

    listener = QueueListener(log_queue, stream_handler)
    listener.start()

    atexit.register(listener.stop)

    return prod_logger
