# -*- coding: utf-8 -*-
from ansibleapi.environment import prepare_environment

def get_app(**kwargs):
    """
    :param kwargs:
    :return:
    """
    from celery import Celery
    prepare_environment(**kwargs)

    celery_app = Celery('ansibleapi')

    # tải config từ setting, dấu hiệu nhận biết là 'CELERY'
    celery_app.config_from_object('django.conf:settings', namespace='CELERY')

    # tải tất cả các module task từ đăng ký djanfgo app
    celery_app.autodiscover_tasks()
    return celery_app