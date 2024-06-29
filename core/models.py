from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from rest_framework.authtoken.admin import User


# Create your models here.

class Servico(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    valor = models.DecimalField(max_digits=5, decimal_places=2,
                                validators=[MinValueValidator(1), MaxValueValidator(9999)])

    def __str__(self):
        return self.nome


class Endereco(models.Model):
    rua = models.CharField(max_length=200)
    bairro = models.CharField(max_length=200)
    numero = models.CharField(max_length=50)
    cidade = models.CharField(max_length=200)
    estado = models.CharField(max_length=200)
    cep = models.CharField(max_length=50)
    pais = models.CharField(max_length=200)

    # definir uma class meta
    class Meta:
        verbose_name = 'Endereço'
        abstract = True
        """
        Com abstract = True nao sera criado uma tabela no banco
        """

    def __str__(self):
        return f"{self.rua}, {self.numero}, {self.bairro}, {self.cidade}, {self.estado}, {self.pais}"


class Profile(Endereco):
    """
    Uso de herenca multipla para herdar os campos de Endereco
    """
    TIPO_CLIENTE = 'CLIENTE'
    TIPO_PRESTADOR = 'PRESTADOR'

    CHOICES_TIPO = (
        (TIPO_CLIENTE, 'Cliente'),
        (TIPO_PRESTADOR, 'Prestador'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=CHOICES_TIPO)
    telefone = models.CharField(max_length=11, blank=False, null=False,
                                validators=[RegexValidator(
                                    regex=r'[0-9]{2}9[0-9]{8}$',
                                    message='Telefone invalido - Formato esperado: 85992563678'
                                )])
    email = models.EmailField(unique=True, validators=[EmailValidator()])

    def save(self, *args, **kwargs):
        if self.tipo == Profile.TIPO_PRESTADOR:
            pass
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Perfil'

    def __str__(self):
        return f'{self.user.username} ({self.tipo})'


class PrestadorManager(models.Manager):
    # ProxyModel
    """
    O models.Manager é uma classe fornecida pelo Django que atua como uma interface entre a model e o banco de dados.
    Por padrão, Django fornece um Manager chamado objects para cada modelo.
    No entanto, podemos criar um manager personalizado para adicionar funcionalidades
    ou para modificar o comportamento padrão das consultas.
    """
    def get_queryset(self):
        """
        Return a new QuerySet object. Subclasses can override this method to
        customize the behavior of the Manager.
        """
        return super().get_queryset().filter(tipo=Profile.TIPO_PRESTADOR)


class Prestador(Profile):
    objects = PrestadorManager()

    def save(self, *args, **kwargs):
        if self.id is None:
            self.tipo = Profile.TIPO_PRESTADOR
        return super().save(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name_plural = 'Prestadores'


class ClienteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(tipo=Profile.TIPO_CLIENTE)


class Cliente(Profile):
    objects = ClienteManager()

    def save(self, *args, **kwargs):
        if self.id is None:
            self.tipo = Profile.TIPO_CLIENTE
        return super().save(*args, **kwargs)

    class Meta:
        proxy = True


class MeioPagamento(models.Model):
    nome = models.CharField(max_length=200)

    def __str__(self):
        return self.nome


class Atendimento(models.Model):
    STATUS_AGENDADO = 'AGENDADO'
    STATUS_CONCLUIDO = 'CONCLUIDO'
    STATUS_CANCELADO = 'CANCELADO'

    CHOICES_STATUS = (
        (STATUS_AGENDADO, 'Agendado'),
        (STATUS_CONCLUIDO, 'Concluído'),
        (STATUS_CANCELADO, 'Cancelado'),
    )
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE,
                                related_name='atendimentos_cliente')
    prestador_servico = models.ForeignKey(Prestador, on_delete=models.CASCADE,
                                          related_name='atendimentos_prestador')
    data_hora = models.DateTimeField()
    valor = models.DecimalField(max_digits=8,
                                decimal_places=2,
                                validators=[MinValueValidator(0)],
                                blank=True)
    meio_pagamento = models.ForeignKey(MeioPagamento, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=CHOICES_STATUS)

    def is_new_attendance(self):
        return self.id is None

    def _load_value_from_service(self):
        if self.is_new_attendance():
            self.valor = self.servico.valor
        elif self.status == Atendimento.STATUS_AGENDADO and self.servico.valor < self.valor:
            self.valor = self.servico.valor

    def _validate_status_change(self):
        if not self.is_new_attendance():
            instancia_do_banco = Atendimento.objects.get(id=self.id)

            # self -> o objeto a ser salvo
            # instancia_do_banco -> o objeto já salvo

            if (instancia_do_banco.status in (Atendimento.STATUS_CONCLUIDO,
                                              Atendimento.STATUS_CANCELADO)
                    and instancia_do_banco.status != self.status):
                raise ValidationError('Não é possível atualizar o status de um atendimento finalizado.', 1001)

    def save(self, *args, **kwargs):
        self._load_value_from_service()
        self._validate_status_change()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Atendimento de {self.servico} para {self.cliente} por {self.prestador_servico} em {self.data_hora}"
