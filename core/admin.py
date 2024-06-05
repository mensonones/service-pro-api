from django.contrib import admin
from .models import Servico, Cliente, Profile, MeioPagamento, Atendimento, Prestador


# Register your models here.

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor')
    search_fields = ('nome',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo', 'telefone', 'email')
    search_fields = ('user__username', 'email')


""" @admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo', 'telefone', 'email') """


""" @admin.register(Prestador)
class PrestadorAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo', 'telefone', 'email') """


@admin.register(MeioPagamento)
class MeioPagamentoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    list_display = ('servico', 'cliente', 'prestador_servico', 'data_hora', 'valor', 'meio_pagamento', 'status')
    search_fields = ('servico__nome', 'cliente__user__username', 'prestador_servico__user__username')
