from django.db import models
from django.utils import timezone

from .constants import (
    ESPECIE_CHOICES,
    HELP_TEXT_CEP_FORMAT,
    HELP_TEXT_CPF_FORMAT,
    HELP_TEXT_PACIENTE_FOTO,
    HELP_TEXT_TUTOR_OBSERVACOES,
    SEXO_CHOICES,
    STATUS_CHOICES,
    TIPO_CONSULTA_CHOICES,
)


class Tutor(models.Model):
    """
    Modelo que representa o tutor (proprietário) de um paciente.

    Um tutor pode ter múltiplos pacientes associados.
    O CPF é validado tanto no serializer quanto no modelo.
    """

    nome_completo = models.CharField(max_length=255, verbose_name="Nome Completo")
    cpf = models.CharField(
        max_length=14,
        unique=True,
        verbose_name="CPF",
        help_text=HELP_TEXT_CPF_FORMAT,
        db_index=True,  # Índice para buscas rápidas por CPF
    )
    telefone_principal = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Telefone Principal"
    )
    telefone_secundario = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Telefone Secundário",
    )
    email = models.EmailField(
        unique=True,
        blank=True,
        null=True,
        verbose_name="E-mail",
        db_index=True,  # Índice para buscas rápidas por email
    )
    endereco_rua = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Rua/Avenida"
    )
    endereco_numero = models.CharField(
        max_length=10, blank=True, null=True, verbose_name="Número"
    )
    endereco_complemento = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Complemento"
    )
    endereco_bairro = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Bairro"
    )
    endereco_cidade = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Cidade"
    )
    endereco_uf = models.CharField(
        max_length=2, blank=True, null=True, verbose_name="UF"
    )
    endereco_cep = models.CharField(
        max_length=9,
        blank=True,
        null=True,
        verbose_name="CEP",
        help_text=HELP_TEXT_CEP_FORMAT,
    )
    data_cadastro = models.DateTimeField(
        default=timezone.now, verbose_name="Data de Cadastro"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações",
        help_text=HELP_TEXT_TUTOR_OBSERVACOES,
    )

    class Meta:
        verbose_name = "Tutor"
        verbose_name_plural = "Tutores"
        ordering = ["nome_completo"]
        indexes = [
            models.Index(fields=["cpf"], name="tutor_cpf_idx"),
            models.Index(fields=["email"], name="tutor_email_idx"),
        ]

    def __str__(self):
        return self.nome_completo


class Paciente(models.Model):
    """
    Modelo que representa um paciente (animal) da clínica.

    Cada paciente está vinculado a um tutor e contém informações
    completas sobre histórico médico, características físicas e comportamentais.
    """

    nome = models.CharField(
        max_length=100, verbose_name="Nome do Paciente", db_index=True
    )
    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.PROTECT,
        related_name="pacientes",
        verbose_name="Tutor Responsável",
        help_text="Tutor responsável pelo paciente",
    )
    especie = models.CharField(
        max_length=10, choices=ESPECIE_CHOICES, verbose_name="Espécie"
    )
    raca = models.CharField(max_length=100, blank=True, null=True, verbose_name="Raça")
    data_nascimento = models.DateField(
        blank=True, null=True, verbose_name="Data de Nascimento"
    )
    sexo = models.CharField(
        max_length=3, choices=SEXO_CHOICES, blank=True, null=True, verbose_name="Sexo"
    )
    microchip = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Microchip",
        db_index=True,
    )
    cor_pelagem = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Cor da Pelagem"
    )
    peso_kg = models.DecimalField(
        max_digits=6, decimal_places=3, blank=True, null=True, verbose_name="Peso (kg)"
    )
    procedencia = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Procedência"
    )
    alimentacao_detalhes = models.TextField(
        blank=True, null=True, verbose_name="Detalhes da Alimentação"
    )
    contactantes_outros_animais = models.TextField(
        blank=True, null=True, verbose_name="Contactantes e Ambiente"
    )
    ambiente_onde_vive = models.TextField(
        blank=True, null=True, verbose_name="Ambiente em que Vive (detalhes)"
    )
    historico_vacinacao = models.TextField(
        blank=True, null=True, verbose_name="Histórico de Vacinação"
    )
    historico_vermifugacao = models.TextField(
        blank=True, null=True, verbose_name="Histórico de Vermifugação"
    )
    doencas_pregressas = models.TextField(
        blank=True, null=True, verbose_name="Doenças Pregressas"
    )
    cirurgias_anteriores = models.TextField(
        blank=True, null=True, verbose_name="Cirurgias Anteriores"
    )
    alergias_conhecidas = models.TextField(
        blank=True, null=True, verbose_name="Alergias Conhecidas"
    )

    data_cadastro = models.DateTimeField(
        default=timezone.now, verbose_name="Data de Cadastro"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="ATIVO", verbose_name="Status"
    )
    foto = models.ImageField(
        upload_to="pacientes_fotos/",
        blank=True,
        null=True,
        verbose_name="Foto",
        help_text=HELP_TEXT_PACIENTE_FOTO,
    )
    observacoes_clinicas_relevantes = models.TextField(
        blank=True, null=True, verbose_name="Outras Observações Clínicas Relevantes"
    )

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ["nome"]
        indexes = [
            models.Index(fields=["nome"], name="paciente_nome_idx"),
            models.Index(fields=["microchip"], name="paciente_microchip_idx"),
            models.Index(fields=["tutor", "nome"], name="paciente_tutor_nome_idx"),
        ]

    def __str__(self):
        return f"{self.nome} (Espécie: {self.get_especie_display()}) - Tutor: {self.tutor.nome_completo}"  # type: ignore

    @property
    def idade(self):
        """
        Calcula e retorna a idade do paciente de forma legível.

        Returns:
            str: Idade em anos, meses ou dias, dependendo da idade
        """
        if self.data_nascimento:
            hoje = timezone.now().date()
            anos = (
                hoje.year
                - self.data_nascimento.year
                - (
                    (hoje.month, hoje.day)
                    < (self.data_nascimento.month, self.data_nascimento.day)
                )
            )
            if anos > 0:
                return f"{anos} ano(s)"
            else:
                meses = (
                    (hoje.year - self.data_nascimento.year) * 12
                    + hoje.month
                    - self.data_nascimento.month
                )
                if hoje.day < self.data_nascimento.day:
                    meses -= 1
                if meses > 0:
                    return f"{meses} mes(es)"
                else:
                    dias = (hoje - self.data_nascimento).days
                    if dias == 0:
                        return "Hoje"
                    if dias < 0:
                        return "Data futura"  # Para evitar idade negativa se data_nascimento for no futuro
                    return f"{dias} dia(s)"
        return "Não informada"


class Veterinario(models.Model):
    nome_completo = models.CharField(max_length=255, verbose_name="Nome do Veterinário")
    crmv = models.CharField(
        max_length=20, blank=True, null=True, unique=True, verbose_name="CRMV"
    )

    class Meta:
        verbose_name = "Veterinário"
        verbose_name_plural = "Veterinários"
        ordering = ["nome_completo"]

    def __str__(self):
        return self.nome_completo


class Sintoma(models.Model):
    nome = models.CharField(max_length=200, unique=True, verbose_name="Nome do Sintoma")
    descricao = models.TextField(
        blank=True, null=True, verbose_name="Descrição do Sintoma (opcional)"
    )

    class Meta:
        verbose_name = "Sintoma"
        verbose_name_plural = "Sintomas"
        ordering = ["nome"]

    def __str__(self):
        return self.nome  # type: ignore


class Doenca(models.Model):
    """
    Representa uma condição ou doença que serve como base de conhecimento.
    Ex: 'Cinomose', 'Gastrite', 'Otite'.
    """

    nome = models.CharField(max_length=200, unique=True, verbose_name="Nome da Doença")
    descricao = models.TextField(
        blank=True,
        null=True,
        help_text="Descrição técnica, etiologia, informações gerais sobre a doença.",
    )

    # Define quais sintomas estão COMUMENTE associados a esta doença.
    sintomas_associados = models.ManyToManyField(
        "Sintoma", blank=True, verbose_name="Sintomas Típicos Associados"
    )

    class Meta:
        verbose_name = "Doença"
        verbose_name_plural = "Doenças"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Consulta(models.Model):
    """
    Modelo que representa uma consulta veterinária.

    Registra todas as informações de uma consulta, incluindo:
    - Anamnese completa por sistemas
    - Exame físico geral e específico
    - Sintomas apresentados
    - Diagnósticos suspeitos (gerados automaticamente)
    - Diagnósticos definitivos (confirmados pelo veterinário)
    - Tratamento prescrito e orientações
    """

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="consultas",
        verbose_name="Paciente",
    )
    # SET_NULL = se o veterinário for removido, a consulta não será excluída, mas o campo ficará vazio
    veterinario_responsavel = models.ForeignKey(
        Veterinario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consultas_realizadas",
        verbose_name="Veterinário Responsável",
    )
    data_hora_agendamento = models.DateTimeField(
        default=timezone.now, verbose_name="Data e Hora do Atendimento"
    )
    tipo_consulta = models.CharField(
        max_length=20,
        choices=TIPO_CONSULTA_CHOICES,
        default="ROTINA",
        verbose_name="Tipo de Consulta",
    )

    queixa_principal_tutor = models.TextField(
        blank=True, null=True, verbose_name="Queixa Principal (relato do tutor)"
    )
    historico_doenca_atual = models.TextField(
        blank=True,
        null=True,
        verbose_name="Histórico da Doença Atual (evolução, tratamentos prévios)",
    )

    # Anamnese Especial (Revisão dos Sistemas)
    anamnese_sistema_respiratorio = models.TextField(
        blank=True,
        null=True,
        verbose_name="Anamnese Sist. Respiratório",
        help_text="Ex: secreção, tosse, espirro, cianose, dispnéia, ruído.",
    )
    anamnese_sistema_cardiovascular = models.TextField(
        blank=True,
        null=True,
        verbose_name="Anamnese Sist. Cardiovascular",
        help_text="Ex: intolerância a exercícios, cansaço, síncope, cianose, tosse.",
    )
    anamnese_sistema_digestorio = models.TextField(
        blank=True,
        null=True,
        verbose_name="Anamnese Sist. Digestório",
        help_text="Ex: apetite, vômito, diarreia.",
    )
    anamnese_sistema_urinario = models.TextField(
        blank=True,
        null=True,
        verbose_name="Anamnese Sist. Urinário",
        help_text="Ex: ingestão de água, aspecto/volume/frequência da urina, tenesmo, disúria.",
    )
    anamnese_sistema_reprodutor = models.TextField(
        blank=True,
        null=True,
        verbose_name="Anamnese Sist. Reprodutor",
        help_text="Ex: secreção, cio, anticoncepcional, prenhez, filhotes, mamas, comportamento.",
    )
    anamnese_sistema_locomotor = models.TextField(
        blank=True,
        null=True,
        verbose_name="Anamnese Sist. Locomotor",
        help_text="Ex: claudicação, trauma, aumento de volume, marcha, impotência, exercícios.",
    )
    anamnese_sistema_neurologico = models.TextField(
        blank=True,
        null=True,
        verbose_name="Anamnese Sist. Neurológico",
        help_text="Ex: convulsão, síncopes, déficits, deambulação, audição, olfato, propriocepção, manias, deglutição, latido/miado.",
    )
    anamnese_pele_anexos = models.TextField(
        blank=True,
        null=True,
        verbose_name="Anamnese Pele e Anexos",
        help_text="Ex: higiene, secreção, alopecia, prurido, lesões, descamação, parasitas, orelha.",
    )
    anamnese_olhos = models.TextField(
        blank=True,
        null=True,
        verbose_name="Anamnese Olhos",
        help_text="Ex: secreção, olho vermelho/esbranquiçado, déficit visual, blefaroespasmo, fotofobia.",
    )

    # Exame Físico Geral (Sinais Vitais e Observações Gerais)
    temperatura_celsius = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True,
        verbose_name="Temperatura (°C)",
    )
    frequencia_cardiaca_bpm = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Frequência Cardíaca (bpm)"
    )
    frequencia_respiratoria_mpm = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Frequência Respiratória (mpm)"
    )
    tpc_segundos = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name="TPC (segundos)"
    )
    hidratacao_status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Status de Hidratação",
        help_text="Ex: Normohidratado, Desidratado (Leve, Moderado, Grave), Hiperhidratado",
    )
    escore_condicao_corporal = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Escore de Condição Corporal",
        help_text="Ex: Caquético, Magro, Ideal, Sobrepeso, Obeso ou Escala 1-9",
    )
    exame_postura = models.CharField(
        max_length=150, blank=True, null=True, verbose_name="Postura e Comportamento"
    )
    exame_nivel_consciencia = models.CharField(
        max_length=150, blank=True, null=True, verbose_name="Nível de Consciência"
    )
    exame_linfonodos_obs = models.TextField(
        # Campo geral para linfonodos
        blank=True,
        null=True,
        verbose_name="Avaliação de Linfonodos",
    )
    exame_mucosas_obs = models.TextField(
        blank=True, null=True, verbose_name="Avaliação de Mucosas"
    )  # Campo geral para mucosas
    exame_pulso_ppm = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Pulso (ppm)"
    )
    observacoes_exame_fisico_geral = models.TextField(
        # Renomeado para clareza
        blank=True,
        null=True,
        verbose_name="Outras Observações do Exame Físico Geral",
    )

    # Exame Físico Específico (por sistema)
    examefisico_sistema_respiratorio = models.TextField(
        blank=True, null=True, verbose_name="Ex. Físico Sist. Respiratório"
    )
    examefisico_sistema_cardiovascular = models.TextField(
        blank=True, null=True, verbose_name="Ex. Físico Sist. Cardiovascular"
    )
    examefisico_sistema_digestorio = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ex. Físico Sist. Digestório",
        help_text="Avaliação de cavidade oral, abdômen (palpação, auscultação), etc.",
    )
    examefisico_sistema_urinario = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ex. Físico Sist. Urinário",
        help_text="Palpação de rins, bexiga, avaliação de genitália externa, etc.",
    )
    examefisico_sistema_reprodutor = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ex. Físico Sist. Reprodutor",
        help_text="Avaliação de testículos, próstata, vulva, vagina, glândulas mamárias, etc.",
    )
    examefisico_sistema_locomotor = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ex. Físico Sist. Locomotor",
        help_text="Avaliação de claudicação, amplitude de movimento, dor articular/muscular, crepitação, etc.",
    )
    examefisico_sistema_neurologico = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ex. Físico Sist. Neurológico",
        help_text="Avaliação de estado mental, pares cranianos, reflexos espinhais, sensibilidade, coordenação, etc.",
    )
    examefisico_pele_anexos = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ex. Físico Pele e Anexos",
        help_text="Avaliação de pelagem, presença de lesões, ectoparasitas, otoscopia, etc.",
    )
    examefisico_olhos = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ex. Físico Olhos",
        help_text="Avaliação com oftalmoscópio, reflexos pupilares, pressão intraocular (se aplicável), etc.",
    )
    examefisico_ouvidos = models.TextField(  # Muitas vezes incluído em Pele e Anexos, mas pode ser separado
        blank=True,
        null=True,
        verbose_name="Ex. Físico Ouvidos",
        help_text="Otoscopia, presença de cerúmen, odor, sensibilidade, etc.",
    )

    sintomas_apresentados = models.ManyToManyField(
        Sintoma,
        blank=True,
        verbose_name="Sintomas Apresentados",
        related_name="consultas_com_sintoma",
    )  # Corrigido related_name

    diagnosticos_suspeitos = models.ManyToManyField(
        Doenca,
        related_name="consultas_com_suspeita",
        blank=True,
        verbose_name="Suspeitas Diagnósticas",
    )
    exames_complementares_solicitados = models.TextField(
        blank=True,
        null=True,
        verbose_name="Exames Complementares Solicitados/Realizados e Resultados",
    )
    diagnosticos_definitivos = models.ManyToManyField(
        Doenca,
        related_name="consultas_com_diagnostico_definitivo",
        blank=True,
        verbose_name="Diagnósticos Definitivos",
    )
    tratamento_prescrito = models.TextField(
        blank=True,
        null=True,
        verbose_name="Tratamento Prescrito (Medicamentos, doses, frequência)",
    )
    procedimentos_realizados = models.TextField(
        blank=True, null=True, verbose_name="Procedimentos Realizados na Consulta"
    )
    prognostico = models.TextField(blank=True, null=True, verbose_name="Prognóstico")
    instrucoes_para_tutor = models.TextField(
        blank=True, null=True, verbose_name="Instruções para o Tutor e Orientações"
    )
    data_proximo_retorno = models.DateField(
        blank=True, null=True, verbose_name="Data do Próximo Retorno/Reavaliação"
    )

    data_criacao_registro = models.DateTimeField(auto_now_add=True)
    data_ultima_modificacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"
        ordering = ["-data_hora_agendamento"]

    def __str__(self):
        return f"Consulta de {self.paciente.nome} em {self.data_hora_agendamento.strftime('%d/%m/%Y %H:%M')}"
