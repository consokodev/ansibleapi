# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
import sys
import traceback

import logging
import os
import tempfile


try:
    from Queue import Queue, Empty
except ImportError:  # nocv
    from queue import Queue, Empty

import six

try:
    from yaml import CLoader as Loader, load
except ImportError:  # nocv
    from yaml import Loader, load


# Classes and methods for support
class DummyHistory(object):



    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)

    def __setattr__(self, key, value):
        pass

    def __getattr__(self, item):
        return None  # nocv

    @property
    def raw_stdout(self):
        return ""

    @raw_stdout.setter
    def raw_stdout(self, value):
        self.logger.info(value)

    def write_line(self, value, number):
        self.logger.info(value)  # nocv

    def save(self):
        pass


class tmp_file(object):
    '''
    tạo file key tmp cho task chạy ansible
    '''

    def __init__(self, data="", mode="w", bufsize=0, **kwargs):
        '''
        tmp_file constructor

        :param data: -- string to write in tmp file.
        :type data: str
        :param mode: -- file open mode. Default 'w'.
        :type mode: str
        :param bufsize: -- bufer size for tempfile.NamedTemporaryFile
        :type bufsize: int
        :param kwargs:  -- other kwargs for tempfile.NamedTemporaryFile
        '''

        run_dir = settings.BASE_DIR + "/run"

        # check thư mục tồn if
        if not os.path.exists(run_dir):
            os.mkdir(run_dir)

        kw = not six.PY3 and {"bufsize": bufsize} or {}
        kwargs.update(kw)


        fd = tempfile.NamedTemporaryFile(mode, dir=run_dir, **kwargs)
        self.fd = fd
        if data:
            self.write(data)

    def write(self, wr_string):
        '''
        Write to file and flush

        :param wr_string: -- writable string
        :type wr_string: str
        :return: None
        :rtype: None
        '''
        result = self.fd.write(wr_string)
        self.fd.flush()
        return result

    def __getattr__(self, name):
        return getattr(self.fd, name)

    # def __del__(self):
    #     self.fd.close()

    def __enter__(self):
        '''
        :return: -- file object
        :rtype: tempfile.NamedTemporaryFile
        '''
        return self

    def __exit__(self, type_e, value, tb):
        self.fd.close()
        if value is not None:
            return False

class tmp_file_context(object):
    '''
    Context object for work with tmp_file.
    Auto close on exit from context and
    remove if file stil exist.
    '''

    def __init__(self, *args, **kwargs):
        self.tmp = tmp_file(*args, **kwargs)

    def __enter__(self):
        return self.tmp

    def __exit__(self, type_e, value, tb):
        self.tmp.close()
        if os.path.exists(self.tmp.name):
            os.remove(self.tmp.name)

class assertRaises(object):
    '''
    Context for exclude rises
    '''

    def __init__(self, *args, **kwargs):
        '''
        :param args: -- list of exception classes
        :type args: list,Exception
        :param verbose: -- logging
        :type verbose: bool
        '''
        self._kwargs = dict(**kwargs)
        self._verbose = kwargs.pop("verbose", False)
        self._exclude = kwargs.pop("exclude", False)
        self._excepts = tuple(args)

    def __enter__(self):
        return self  # pragma: no cover

    def __exit__(self, exc_type, exc_val, exc_tb):
        return exc_type is not None and (
            (not self._exclude and not issubclass(exc_type, self._excepts)) or
            (self._exclude and issubclass(exc_type, self._excepts))
        )

class raise_context(assertRaises):
    def execute(self, func, *args, **kwargs):
        with self.__class__(self._excepts, **self._kwargs):
            return func(*args, **kwargs)
        return sys.exc_info()

    def __enter__(self):
        return self.execute

    def __call__(self, original_function):
        def wrapper(*args, **kwargs):
            return self.execute(original_function, *args, **kwargs)

        return wrapper

class exception_with_traceback(raise_context):
    def __init__(self, *args, **kwargs):
        super(exception_with_traceback, self).__init__(**kwargs)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            exc_val.traceback = traceback.format_exc()

class task(object):
    ''' Decorator for Celery task classes

    **Examples**:

            .. code-block:: python

                @task(app)
                class SomeTask(BaseTask):
                    def run(self):
                        return "Result of task"

            .. code-block:: python

                @task(app, bind=True)
                class SomeTask2(BaseTask):
                    def run(self):
                        return "Result of task"
    '''

    logger = logging.getLogger(__name__)

    def __init__(self, app, *args, **kwargs):
        '''
        :param app: -- CeleryApp object
        :type app: celery.Celery
        :param args: -- args for CeleryApp
        :param kwargs: -- kwargs for CeleryApp
        '''
        self.app = app
        self.args, self.kwargs = args, kwargs

    def __call__(self, task_cls):
        self.kwargs["name"] = "{c.__module__}.{c.__name__}".format(c=task_cls)

        @self.app.task(*self.args, **self.kwargs)
        def wrapper(*args, **kwargs):
            return task_cls(*args, **kwargs).start()

        wrapper.task_class = task_cls
        return wrapper

class BaseTask(object):
    '''
    BaseTask class for all tasks.
    '''

    def __init__(self, app, *args, **kwargs):
        '''
        :param app: -- CeleryApp object
        :type app: celery.Celery
        :param args: -- any args for tasks
        :param kwargs: -- any kwargs for tasks
        '''
        # super().__init__()
        super(BaseTask, self).__init__()
        self.app = app
        self.args, self.kwargs = args, kwargs
        self.task_class = self.__class__

    def start(self):
        ''' Method that starts task executions. '''
        return self.run()

    def run(self):  # pragma: no cover
        ''' Method with task logic. '''
        # pylint: disable=notimplemented-raised,
        raise NotImplemented