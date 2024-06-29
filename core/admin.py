from django.contrib import admin, messages
from .models import Servico, Cliente, Profile, MeioPagamento, Atendimento, Prestador


# Register your models here.

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor')
    search_fields = ('nome',)


# callable
@admin.display(description="Name")
def upper_case_name(obj):
    return f"{obj.user.username}".upper()


# Criei essa classe em comum para CLiente e Prestador para evitar duplicacao de codigo
# @admin.register(Cliente, Prestador)
class ProfileAdminBase(admin.ModelAdmin):
    list_display = (upper_case_name, 'telefone')
    # https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_display_links
    list_display_links = ['telefone']
    search_fields = ('user__username', 'email')
    fieldsets = (
        ('Informações', {
            'fields': ('user', 'telefone', 'email',),
        }),
        ('Endereço', {
            'fields': ('rua', 'bairro', 'numero', 'cidade', 'estado', 'cep', 'pais',),
            'classes': ('collapse',),
        }),
    )

    def get_username(self, obj):
        return obj.user.username  # Ou use obj.user.get_full_name() se preferir o nome completo

    get_username.short_description = 'Username'  # Define a descrição do cabeçalho da coluna no admin

    def has_delete_permission(self, request, obj=None):
        return False


# @admin.register(Profile)
@admin.register(Cliente)
class ClienteAdmin(ProfileAdminBase):
    list_display = (upper_case_name, 'telefone', 'email')


@admin.register(Prestador)
class PrestadorAdmin(ProfileAdminBase):
    # list_display = ('user', 'telefone', 'email')
    pass


@admin.register(MeioPagamento)
class MeioPagamentoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


# Adicionando ações ao ModelAdmin (https://docs.djangoproject.com/en/5.0/ref/contrib/admin/actions/)
@admin.action(description='Atendimento pago')
def atendimento_concluido(modeladmin, request, queryset):
    queryset.update(status=Atendimento.STATUS_CONCLUIDO)


# Adicionando acoes com tratamento de acao
# (https://docs.djangoproject.com/en/5.0/ref/contrib/admin/actions/#handling-errors-in-actions)
@admin.action(description='Atendimento cancelado')
def atendimento_cancelado(modeladmin, request, queryset):
    nao_agendado = queryset.exclude(status=Atendimento.STATUS_AGENDADO)
    if nao_agendado.exists():
        modeladmin.message_user(
            request,
            f'{nao_agendado.count()} atendimentos nao podem ser cancelados porque nao estao com status: Agendado',
            messages.ERROR
        )
    agendados = queryset.filter(status=Atendimento.STATUS_AGENDADO)
    total_agendados = agendados.update(status=Atendimento.STATUS_CANCELADO)

    if total_agendados > 0:
        modeladmin.message_user(
            request,
            f'{total_agendados} atendimentos foram cancelados com sucesso.',
            messages.SUCCESS
        )
    else:
        modeladmin.message_user(
            request,
            'Nenhum atendimento foi cancelado.',
            messages.WARNING
        )


@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    date_hierarchy = 'data_hora'
    list_display = ('servico', 'cliente', 'prestador_servico', 'data_hora', 'valor', 'meio_pagamento', 'status')
    search_fields = ('servico__nome', 'cliente__user__username', 'prestador_servico__user__username')
    readonly_fields = ('valor',)
    actions = [atendimento_concluido, atendimento_cancelado]


# desativando acoes em todo o site
#  (https://docs.djangoproject.com/en/5.0/ref/contrib/admin/actions/#django.contrib.admin.AdminSite.disable_action)
admin.site.disable_action("delete_selected")
