from os import environ

broker_url = environ.get('CELERY_BROKER_URL')
result_backend = 'rpc://'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'America/Fortaleza'
enable_utc = True
