from celery import shared_task
import time


@shared_task
def add(x, y):
    return x + y
