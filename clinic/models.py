from django.db import models
from django.utils import timezone  # para utilizar a data e hora atuais


class Tutor(models.Model):
    nome_completo = models.CharField(
        max_length=255, verbose_name='Nome Completo')
    cpf = models.CharField(max_length=14, unique=True,
                           verbose_name='CPF', help_text="formato: XXX.XXX.XXX-XX")
    telefone_principal = models.CharField(
        max_length=20, blank=True, null=True, verbose_name='Telefone Principal')
    telefone_secundario = models.CharField(
        # Corrigido 'Secundario' para 'Secundário'
        max_length=20, blank=True, null=True, verbose_name='Telefone Secundário')
    email = models.EmailField(
        # Adicionado blank=True, null=True se for opcional mas único
        unique=True, blank=True, null=True, verbose_name='E-mail')
    endereco_rua = models.CharField(
        max_length=255, blank=True, null=True, verbose_name='Rua/Avenida')
    endereco_numero = models.CharField(
        max_length=10, blank=True, null=True, verbose_name='Número')
    endereco_complemento = models.CharField(
        max_length=100, blank=True, null=True, verbose_name='Complemento')
    endereco_bairro = models.CharField(
        max_length=100, blank=True, null=True, verbose_name='Bairro')
    endereco_cidade = models.CharField(
        max_length=100, blank=True, null=True, verbose_name='Cidade')
    endereco_uf = models.CharField(
        max_length=2, blank=True, null=True, verbose_name='UF')
    endereco_cep = models.CharField(
        max_length=9, blank=True, null=True, verbose_name='CEP', help_text="formato: XXXXX-XXX")
    data_cadastro = models.DateTimeField(
        default=timezone.now, verbose_name='Data de Cadastro')
    observacoes = models.TextField(
        blank=True, null=True, verbose_name='Observações',
        help_text="Informações adicionais sobre o tutor")

    class Meta:
        verbose_name = 'Tutor'
        verbose_name_plural = 'Tutores'
        ordering = ['nome_completo']

    def __str__(self):
        return self.nome_completo


class Paciente(models.Model):
    ESPECIE_CHOICES = [
        ('CANINO', 'Canino'),
        ('FELINO', 'Felino'),
        ('AVE', 'Ave'),
        ('REPTIL', 'Réptil'),
        ('ROEDOR', 'Roedor'),
        ('LAGOMORFO', 'Lagomorfo (Coelho)'),
        ('OUTRO', 'Outro'),
    ]
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('F', 'Fêmea'),
        ('MC', 'Macho Castrado'),
        ('FC', 'Fêmea Castrada'),
        ('IND', 'Indefinido'),
    ]
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('OBITO', 'Óbito'),
        ('TRANSFERIDO', 'Transferido'),
        ('PERDIDO', 'Perdido'),
    ]

    nome = models.CharField(
        max_length=100, verbose_name='Nome do Paciente')
    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.PROTECT,
        related_name='pacientes',
        verbose_name='Tutor Responsável',  # Corrigido 'Tutor' para 'Tutor Responsável'
        help_text="Tutor responsável pelo paciente")  # Corrigido help_text
    especie = models.CharField(
        max_length=10, choices=ESPECIE_CHOICES, verbose_name='Espécie')
    raca = models.CharField(
        max_length=100, blank=True, null=True, verbose_name='Raça')
    data_nascimento = models.DateField(
        blank=True, null=True, verbose_name='Data de Nascimento')
    sexo = models.CharField(
        max_length=3, choices=SEXO_CHOICES, blank=True, null=True, verbose_name='Sexo')
    microchip = models.CharField(
        # unique=True se o microchip for realmente único
        max_length=50, blank=True, null=True, unique=True,
        verbose_name='Microchip')
    cor_pelagem = models.CharField(
        max_length=50, blank=True, null=True, verbose_name='Cor da Pelagem')
    peso_kg = models.DecimalField(
        max_digits=6, decimal_places=3, blank=True, null=True,
        verbose_name='Peso (kg)')
    data_cadastro = models.DateTimeField(
        default=timezone.now, verbose_name='Data de Cadastro')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='ATIVO',
        verbose_name='Status')
    foto = models.ImageField(
        upload_to='pacientes_fotos/', blank=True, null=True,
        verbose_name='Foto', help_text="Foto do paciente")
    observacoes_clinicas = models.TextField(
        blank=True, null=True, verbose_name='Observações Clínicas Relevantes')
    alergias_conhecidas = models.TextField(
        blank=True, null=True, verbose_name='Alergias Conhecidas')

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['nome']

    def __str__(self):
    # fmt: off
        return f"{self.nome} (Espécie: {self.get_especie_display()}) - Tutor: {self.tutor.nome_completo}" # type: ignore
    # fmt: on  

    @property
    def idade(self):
        if self.data_nascimento:
            hoje = timezone.now().date()
            anos = hoje.year - self.data_nascimento.year - \
                ((hoje.month, hoje.day) <
                 (self.data_nascimento.month, self.data_nascimento.day))
            if anos > 0:
                return f"{anos} ano(s)"
            else:
                meses = (hoje.year - self.data_nascimento.year) * \
                    12 + hoje.month - self.data_nascimento.month
                if hoje.day < self.data_nascimento.day:
                    meses -= 1
                if meses > 0:
                    return f"{meses} mes(es)"
                else:
                    dias = (hoje - self.data_nascimento).days
                    if dias == 0:
                        return "Hoje"  # Para recém-nascidos no dia
                    if dias < 0:
                        return "Data futura"  # Para evitar idade negativa se data_nascimento for no futuro
                    return f"{dias} dia(s)"
        return "Não informada"


class Veterinario(models.Model):
    nome_completo = models.CharField(
        max_length=255, verbose_name="Nome do Veterinário")
    crmv = models.CharField(max_length=20, blank=True, null=True, unique=True,
                            verbose_name="CRMV")

    class Meta:
        verbose_name = "Veterinário"
        verbose_name_plural = "Veterinários"
        ordering = ['nome_completo']

    def __str__(self):
        return self.nome_completo


class Consulta(models.Model):
    TIPO_CONSULTA_CHOICES = [
        ('ROTINA', 'Rotina/Check-up'),
        ('EMERGENCIA', 'Emergência'),
        ('VACINACAO', 'Vacinação'),
        ('CIRURGIA', 'Cirurgia'),
        ('RETORNO', 'Retorno'),
        ('OUTRO', 'Outro'),
    ]
    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name='consultas', verbose_name='Paciente')

    # SET_NULL = se o veterinário for removido, a consulta não será excluída, mas o campo ficará vazio
    veterinario_responsavel = models.ForeignKey(Veterinario, on_delete=models.SET_NULL, null=True, blank=True,
                                                related_name='consultas_realizadas', verbose_name='Veterinário Responsável')  # type: ignore

    data_hora_agendamento = models.DateTimeField(
        default=timezone.now, verbose_name='Data e Hora do Agendamento')
    tipo_consulta = models.CharField(
        max_length=20, choices=TIPO_CONSULTA_CHOICES, default='ROTINA', verbose_name='Tipo de Consulta')

    # Anamnese e Exame Físico
    queixa_principal_tutor = models.TextField(
        blank=True, null=True, verbose_name='Queixa Principal do Tutor',)
    historico_doenca_atual = models.TextField(
        blank=True, null=True, verbose_name='Histórico da Doença Atual',)
    temperatura_celsius = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        verbose_name='Temperatura (°C)')
    frequencia_cardiaca_bpm = models.PositiveIntegerField(
        blank=True, null=True, verbose_name='Frequência Cardíaca (bpm)')
    frequencia_respiratoria_mpm = models.PositiveIntegerField(
        blank=True, null=True, verbose_name='Frequência Respiratória (mpm)')
    tpc_segundos = models.PositiveSmallIntegerField(
        # Tempo de Preenchimento Capilar
        blank=True, null=True, verbose_name='TPC (segundos)')
    hidratacao_status = models.CharField(
        max_length=50, blank=True, null=True,
        verbose_name='Status de Hidratação',
        help_text="Ex: Normal, Desidratado, Hiperdistendido")
    escore_condicao_corporal = models.CharField(max_length=50, blank=True, null=True,
                                                verbose_name='Escore de Condição Corporal',)
    observacoes_exame_fisico = models.TextField(
        blank=True, null=True, verbose_name='Observações do Exame Físico',)

    # Diagnóstico e Tratamento
    suspeitas_diagnosticas = models.TextField(
        blank=True, null=True, verbose_name="Suspeita(s) Diagnóstica(s)")
    exames_complementares_solicitados = models.TextField(
        blank=True, null=True, verbose_name="Exames Complementares Solicitados")
    diagnostico_definitivo = models.TextField(
        blank=True, null=True, verbose_name="Diagnóstico Definitivo")
    tratamento_prescrito = models.TextField(
        blank=True, null=True, verbose_name="Tratamento Prescrito")
    procedimentos_realizados = models.TextField(
        blank=True, null=True, verbose_name="Procedimentos Realizados na Consulta")

    # Pós-Consulta
    prognostico = models.TextField(
        blank=True, null=True, verbose_name="Prognóstico")
    instrucoes_para_tutor = models.TextField(
        blank=True, null=True, verbose_name="Instruções para o Tutor")
    data_proximo_retorno = models.DateField(
        blank=True, null=True, verbose_name="Data do Próximo Retorno")

    data_criacao_registro = models.DateTimeField(auto_now_add=True)
    data_ultima_modificacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Consulta'
        verbose_name_plural = 'Consultas'
        ordering = ['-data_hora_agendamento']  # mais recentes primeiro (-)

    def __str__(self):
        return f"Consulta de {self.paciente.nome} em {self.data_hora_agendamento.strftime('%d/%m/%Y %H:%M')}"
