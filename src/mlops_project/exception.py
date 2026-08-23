"""
Custom exception wrapper used across the whole pipeline.

WHY: Plain Python tracebacks don't tell you WHICH file/line inside a large
multi-stage pipeline failed once the exception bubbles up through several
function calls (ingestion -> validation -> transformation -> training).
CustomException captures that context once, at the point of the `raise`,
so logs/API error responses stay informative in production.
"""

import sys


def error_message_detail(error: Exception, error_detail: sys) -> str:
    _, _, exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename if exc_tb else "unknown"
    line_number = exc_tb.tb_lineno if exc_tb else -1
    return (
        f"Error occurred in python script [{file_name}] "
        f"line number [{line_number}] error message [{error}]"
    )


class CustomException(Exception):
    def __init__(self, error_message: Exception, error_detail: sys = sys):
        super().__init__(str(error_message))
        self.error_message = error_message_detail(error_message, error_detail)

    def __str__(self):
        return self.error_message
