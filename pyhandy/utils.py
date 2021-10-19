import doctest
import os
import random
import shutil
import time
import logging
import inspect

from functools import wraps
from inspect import signature

def typeassert(*ty_args, **ty_kwargs): #https://github.com/callmexss/pyhandy/blob/master/pyhandy/pyhandy.py
    """
    Decorator to check type of the indicated arguments. 
    If used without arguments it will use the available duck types instead.
    
    Usage
    ----------    
    @typeassert(a=int,b=str)
    def foo(a,b):
        print(f"{a=} and {b=}")
    
    @typeassert
    def foo(a:int,b:str):
        print(f"{a=} and {b=}")
       
    Both of the ways above will yield the same output:
    >foo(1,2)
    > TypeError: 2 must be <class 'str'>
    >foo(1,'2')
    > a=1 and b='2'
    """
    noargs = True
    def decorator(func):
        sig = signature(func)
        bind_types = sig.bind_partial(*ty_args, **ty_kwargs).arguments
        def wrapper(*args, **kwargs):
            duck_types = {name:param.annotation for name,param in sig.parameters.items() if param.annotation is not inspect._empty}
            for name, obj in sig.bind(*args, **kwargs).arguments.items():
                if noargs and name in bind_types:
                    if not isinstance(obj, bind_types[name]):
                        raise TypeError(f"{name} must be {bind_types[name]} got value {obj} of class {type(obj)}")
                elif not noargs and name in duck_types:
                    if not isinstance(obj,duck_types[name]):
                        raise TypeError(f"{name} must be {duck_types[name]} got value {obj} of class {type(obj)}")
            return func(*args, **kwargs)

        return wrapper
    if ty_args:
        noargs = False
        return decorator(ty_args[0])
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
