import doctest
import os
import random
import shutil
import time
import logging

from functools import wraps
from inspect import signature

def typeassert(*ty_args, **ty_kwargs): #https://github.com/callmexss/pyhandy/blob/master/pyhandy/pyhandy.py
    """Decorator to check type of specific arguments."""

    def decorator(func):
        sig = signature(func)
        bind_types = sig.bind_partial(*ty_args, **ty_kwargs).arguments

        def wrapper(*args, **kwargs):
            for name, obj in sig.bind(*args, **kwargs).arguments.items():
                if name in bind_types:
                    if not isinstance(obj, bind_types[name]):
                        raise TypeError(f"{obj} must be {bind_types[name]}")
            return func(*args, **kwargs)

        return wrapper

    return decorator

def get_logger_with_format(logger_name=None,logger_format='%(asctime)s - %(name)s %(levelname)s: %(message)s\n',**kwargs):
    '''
    Creates a logger that logs message in the given format.

    For info about logRecord attributes see:
    https://docs.python.org/3/library/logging.html#logrecord-attributes

    Examples:
    --------------
    ```python
    logger = get_logger_with_format('my_logger','%(asctime)s:%(levelname)s:%(name)s:%(message)s\n')
    logger = get_logger_with_format('file-processing','PROCESSING FILE xxx - %(message)s')
    logger = get_logger_with_format(logger_format='%(levelname)s__FILE_PLACEHOLDER__ %(message)s') #root logger with new format
    ```
    '''
    if 'format' in kwargs:
        logger_format = kwargs['format']
    if logger_name is None:
        #https://stackoverflow.com/questions/6847862/how-to-change-the-format-of-logged-messages-temporarily-in-python
        logger = logging.getLogger() 
        logger.handlers[0].setFormatter(logging.Formatter(logger_format))
    else:
        logger = logging.getLogger(logger_name)
        logger_handler = logging.StreamHandler()  # Handler for the logger
        logger.addHandler(logger_handler)
        # New formatter for the handler:
        logger_handler.setFormatter(logging.Formatter(logger_format))
    
    return logger
