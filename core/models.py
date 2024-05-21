from django.db import models
from rest_framework.authtoken.admin import User


# Create your models here.

class Servico(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    valor = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.nome


class LocalAtendimento(models.Model):
    rua = models.CharField(max_length=200)
    bairro = models.CharField(max_length=200)
    numero = models.CharField(max_length=50)
    cidade = models.CharField(max_length=200)
    estado = models.CharField(max_length=200)
    pais = models.CharField(max_length=200)


class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    servico = models.ManyToManyField(Servico)
    local_atendimento = models.ForeignKey(LocalAtendimento, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user


class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    endereco = models.ForeignKey(LocalAtendimento, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user


class MeioPagamento(models.Model):
    nome = models.CharField(max_length=200)

    def __str__(self):
        return self.nome


class Atendimento(models.Model):
    servico = models.ForeignKey(Servico, on_delete=models.SET_NULL)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL)
    prestador_servico = models.ForeignKey(Usuario, on_delete=models.SET_NULL)
    data_hora = models.DateTimeField()
    valor = models.DecimalField(max_digits=5, decimal_places=2)
    meio_pagamento = models.ForeignKey(MeioPagamento, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Atendimento de {self.servico} para {self.cliente} por {self.prestador_servico} em {self.data_hora}"
