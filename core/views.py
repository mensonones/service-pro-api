from django.http import HttpResponse
from core.tasks import add


def test(request):
    add.delay(100, 14)
    return HttpResponse('Processando...')
