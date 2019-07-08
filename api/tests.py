from celery import Celery
import logging

app = Celery('tasks', backend='redis://127.0.0.1:6379/3', broker='redis://127.0.0.1:6379/2')


class task(object):

    logger = logging.getLogger(__name__)

    def __init__(self, app, *args, **kwargs):
        self.app = app
        self.args, self.kwargs = args, kwargs

    def __call__(self, task_cls):
        self.kwargs["name"] = "{c.__module__}.{c.__name__}".format(c=task_cls)

        @self.app.task(*self.args, **self.kwargs)
        def wrapper(*args, **kwargs):
            print("In wrapper")
            return task_cls(*args, **kwargs).start()

        wrapper.task_class = task_cls
        return wrapper

class BaseTask(object):
    '''
    BaseTask class for all tasks.
    '''

    def __init__(self, app, *args, **kwargs):
        super(BaseTask, self).__init__()
        self.app = app
        self.args, self.kwargs = args, kwargs
        self.task_class = self.__class__
        print("In Init of base task")

    def start(self):
        print("In start of base task")
        ''' Method that starts task executions. '''
        return self.run()

    def run(self):  # pragma: no cover
        print("In Run of base task")
        ''' Method with task logic. '''
        # pylint: disable=notimplemented-raised,
        raise NotImplemented


@task(app, ignore_result=True, bind=True)
class Excute(BaseTask):
    def __init__(self, app, **kwargs):
        super(self.__class__, self).__init__(app, **kwargs)
        self.data = kwargs["arg1_key"]
        self.data1 = kwargs["arg2_key"]
        print(self.data)
        print(self.data1)
        print("In init of Excute")

    def run(self):
        print("In run of execute")
        return "123456"

kwargs = {'arg1_key':'arg1', 'arg2_key':'arg2' }
class_test = Excute
class_test(**kwargs)
