import datetime
import random

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory
from faker import Faker
from validate_docbr import CPF

from .constants import (
    ESPECIE_CHOICES,
    SEXO_CHOICES,
    STATUS_CHOICES,
    TIPO_CONSULTA_CHOICES,
)
from .models import Consulta, Doenca, Paciente, Sintoma, Tutor, Veterinario

# Configuração inicial para gerar dados fictícios em português do Brasil
fake_pt_br = Faker("pt_BR")
cpf_generator = CPF()  # Gerador de CPFs válidos


class TutorFactory(DjangoModelFactory):
    """Factory para criação de objetos Tutor com dados fictícios"""

    class Meta:  # type: ignore
        model = Tutor
        # Garante que não serão criados tutores duplicados com mesmo CPF
        django_get_or_create = ("cpf",)

    # Gera nome completo aleatório em português
    nome_completo = factory.Faker("name", locale="pt_BR")  # type: ignore

    # Gera CPF formatado dinamicamente
    @factory.lazy_attribute  # type: ignore
    def cpf(self):
        return cpf_generator.generate(True)

    # Gera telefones e email
    telefone_principal = factory.LazyAttribute(  # type: ignore
        lambda o: fake_pt_br.phone_number()
    )
    telefone_secundario = factory.Maybe(  # type: ignore
        "has_secondary_phone",  # 40% de chance de ter telefone secundário
        yes_declaration=factory.LazyAttribute(  # type: ignore
            lambda o: fake_pt_br.phone_number()
        ),  # type: ignore
        no_declaration=None,  # type: ignore
    )
    # Gera email baseado no nome, removendo caracteres especiais
    email = factory.LazyAttribute(  # type: ignore
        lambda obj: f"{obj.nome_completo.lower().replace(' ', '_').replace('ã', 'a').replace('ç', 'c').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')}.{fake_pt_br.random_int(min=10, max=999)}@{fake_pt_br.free_email_domain()}"
    )

    # Gera endereço completo com dados brasileiros
    endereco_rua = factory.Faker(  # type: ignore
        "street_address", locale="pt_BR"
    )  # type: ignore
    endereco_numero = factory.Faker("building_number")  # type: ignore
    endereco_complemento = factory.Faker(  # type: ignore
        "sentence", nb_words=random.randint(1, 3), locale="pt_BR"
    )
    endereco_bairro = factory.Faker("bairro", locale="pt_BR")  # type: ignore
    endereco_cidade = factory.Faker("city", locale="pt_BR")  # type: ignore
    endereco_uf = factory.Faker("estado_sigla", locale="pt_BR")  # type: ignore
    endereco_cep = factory.LazyAttribute(  # type: ignore
        lambda o: fake_pt_br.postcode().replace("-", "")
    )

    # Observações aleatórias
    observacoes = factory.Faker(
        "paragraph",
        nb_sentences=random.randint(  # type: ignore
            1, 2
        ),
        variable_nb_sentences=True,
        locale="pt_BR",
    )

    class Params:
        # Parâmetro para controle de telefone secundário
        has_secondary_phone = factory.LazyAttribute(  # type: ignore
            lambda o: fake_pt_br.boolean(chance_of_getting_true=40)
        )


class PacienteFactory(DjangoModelFactory):
    """Factory para criação de objetos Paciente com dados fictícios"""

    class Meta:  # type: ignore
        model = Paciente

    # Gera nome e tutor automaticamente
    nome = factory.Faker("first_name", locale="pt_BR")  # type: ignore
    tutor = factory.SubFactory(TutorFactory)  # type: ignore

    # Seleciona espécie aleatória das opções do modelo
    especie = factory.Faker(
        "random_element",
        elements=[  # type: ignore
            x[0] for x in ESPECIE_CHOICES
        ],
    )

    # Define raça baseada na espécie selecionada
    @factory.lazy_attribute  # type: ignore
    def raca(self):
        if self.especie == "CANINO":
            return fake_pt_br.random_element(
                elements=[
                    "Labrador",
                    "Poodle",
                    "Bulldog",
                    "Vira-lata",
                    "Golden Retriever",
                    "Shih Tzu",
                    "Yorkshire",
                ]
            )
        elif self.especie == "FELINO":
            return fake_pt_br.random_element(
                elements=["Siamês", "Persa", "Maine Coon", "SRD", "Bengal", "Ragdoll"]
            )
        elif self.especie == "AVE":
            return fake_pt_br.random_element(
                elements=["Calopsita", "Canário", "Papagaio", "Periquito"]
            )
        elif self.especie == "ROEDOR":
            return fake_pt_br.random_element(
                elements=["Hamster", "Porquinho-da-índia", "Chinchila"]
            )
        elif self.especie == "LAGOMORFO":
            return fake_pt_br.random_element(
                elements=["Coelho Mini Lion", "Coelho Angorá"]
            )
        else:
            return fake_pt_br.word().capitalize()

    # Gera data de nascimento para animais de 0 a 18 anos
    data_nascimento = factory.Faker(  # type: ignore
        "date_of_birth", minimum_age=0, maximum_age=18
    )

    # Seleciona sexo aleatório (exceto 'IND')
    sexo = factory.Faker(
        "random_element",
        elements=[  # type: ignore
            x[0] for x in SEXO_CHOICES if x[0] != "IND"
        ],
    )

    # Campos condicionais (50% chance de ter microchip)
    microchip = factory.Maybe(  # type: ignore
        "has_microchip",
        yes_declaration=factory.Sequence(  # type: ignore
            # type: ignore
            lambda n: f"900{fake_pt_br.bothify(text='##########??##').upper()}{n}"
        ),
        no_declaration=None,  # type: ignore
    )

    # Outras características físicas
    cor_pelagem = factory.Faker("color_name", locale="pt_BR")  # type: ignore
    peso_kg = factory.Faker(
        "pydecimal",
        left_digits=2,
        right_digits=3,  # type: ignore
        positive=True,
        min_value=0.050,
        max_value=95.0,
    )

    # Histórico e informações clínicas
    procedencia = factory.Faker(
        "random_element",
        elements=[  # type: ignore
            "Criador Registrado",
            "Loja de Animais",
            "Adoção de Abrigo",
            "Resgatado",
            "Nascido em casa",
            None,
        ],
    )
    alimentacao_detalhes = factory.Faker(  # type: ignore
        "sentence", nb_words=10, locale="pt_BR"
    )
    contactantes_outros_animais = factory.Faker(  # type: ignore
        "sentence", nb_words=8, locale="pt_BR"
    )
    ambiente_onde_vive = factory.Faker(  # type: ignore
        "sentence", nb_words=7, locale="pt_BR"
    )
    historico_vacinacao = factory.Faker(
        "random_element",
        elements=[  # type: ignore
            "Completo e em dia",
            "Incompleto",
            "Não vacinado",
            "Filhote - em protocolo",
            "Desconhecido",
        ],
    )
    historico_vermifugacao = factory.Faker(
        "random_element",
        elements=[  # type: ignore
            "Regularmente",
            "Ocasionalmente",
            "Não vermifugado",
            "Desconhecido",
        ],
    )

    # Campos condicionais para histórico médico
    doencas_pregressas = factory.Maybe(
        "has_past_illness",
        yes_declaration=factory.Faker(  # type: ignore
            "sentence", nb_words=7
        ),
        no_declaration=None,
    )  # type: ignore
    cirurgias_anteriores = factory.Maybe(
        "has_past_surgery",
        yes_declaration=factory.Faker(  # type: ignore
            "sentence", nb_words=6
        ),
        no_declaration=None,
    )  # type: ignore
    alergias_conhecidas = factory.Maybe(
        "has_allergies",
        yes_declaration=factory.Faker(  # type: ignore
            "sentence", nb_words=5
        ),
        no_declaration=None,
    )  # type: ignore

    # Status do paciente (sempre 'ATIVO')
    status = factory.Faker(
        "random_element", elements=[x[0] for x in STATUS_CHOICES if x[0] == "ATIVO"]
    )

    # Campo de imagem desativado para testes
    # foto = factory.django.ImageField(color='grey')

    # Observações clínicas relevantes
    observacoes_clinicas_relevantes = factory.Faker(  # type: ignore
        "paragraph", nb_sentences=1, variable_nb_sentences=True, locale="pt_BR"
    )

    class Params:
        # Parâmetros para controle de campos opcionais
        has_microchip = factory.LazyAttribute(  # type: ignore
            lambda o: fake_pt_br.boolean(chance_of_getting_true=50)
        )
        has_past_illness = factory.LazyAttribute(  # type: ignore
            lambda o: fake_pt_br.boolean(chance_of_getting_true=20)
        )
        has_past_surgery = factory.LazyAttribute(  # type: ignore
            lambda o: fake_pt_br.boolean(chance_of_getting_true=10)
        )
        has_allergies = factory.LazyAttribute(  # type: ignore
            lambda o: fake_pt_br.boolean(chance_of_getting_true=15)
        )


class VeterinarioFactory(DjangoModelFactory):
    """Factory para criação de objetos Veterinario com dados fictícios"""

    class Meta:  # type: ignore
        model = Veterinario
        # Evita duplicatas por CRMV
        django_get_or_create = ("crmv",)

    nome_completo = factory.Faker("name", locale="pt_BR")  # type: ignore

    # Gera CRMV único com sigla de estado e números sequenciais
    crmv = factory.Sequence(  # type: ignore
        lambda n: f"CRMV-{fake_pt_br.state_abbr().upper()}-{fake_pt_br.random_number(digits=4, fix_len=True)}{n}"
    )


class SintomaFactory(DjangoModelFactory):
    """Factory para criação de objetos Sintoma com dados fictícios"""

    class Meta:
        model = Sintoma
        # Evita duplicatas por nome
        django_get_or_create = ("nome",)

    # Gera nome único para cada sintoma
    nome = factory.Sequence(  # type: ignore
        lambda n: f"Sintoma Auto {fake_pt_br.unique.word().capitalize()}{n}"
    )
    descricao = factory.Faker("sentence", nb_words=random.randint(3, 10))  # type: ignore


class ConsultaFactory(DjangoModelFactory):
    """Factory para criação de objetos Consulta com dados fictícios complexos"""

    class Meta:  # type: ignore
        model = Consulta

    # Cria paciente e veterinário automaticamente
    paciente = factory.SubFactory(PacienteFactory)  # type: ignore
    veterinario_responsavel = factory.SubFactory(  # type: ignore
        VeterinarioFactory
    )  # type: ignore

    # Gera data/hora aleatória nos últimos 2 anos
    data_hora_agendamento = factory.LazyAttribute(  # type: ignore
        lambda o: timezone.make_aware(
            fake_pt_br.date_time_between(start_date="-2y", end_date="now")
        )
    )

    # Seleciona tipo de consulta aleatório
    tipo_consulta = factory.Faker(
        "random_element",
        elements=[  # type: ignore
            x[0] for x in TIPO_CONSULTA_CHOICES
        ],
    )

    # Queixa principal e histórico
    queixa_principal_tutor = factory.Faker(  # type: ignore
        "sentence", nb_words=12, locale="pt_BR"
    )
    historico_doenca_atual = factory.Faker(
        "paragraph",
        nb_sentences=random.randint(  # type: ignore
            2, 4
        ),
        variable_nb_sentences=True,
        locale="pt_BR",
    )

    # Anamnese por sistemas (80% chance de preencher cada seção)
    anamnese_sistema_respiratorio = factory.Maybe(
        "fill_anamnese",
        yes_declaration=factory.Faker("paragraph", nb_sentences=2),
        no_declaration=None,
    )
    anamnese_sistema_cardiovascular = factory.Maybe(
        "fill_anamnese",
        yes_declaration=factory.Faker("paragraph", nb_sentences=2),
        no_declaration=None,
    )
    anamnese_sistema_digestorio = factory.Maybe(
        "fill_anamnese",
        yes_declaration=factory.Faker("paragraph", nb_sentences=2),
        no_declaration=None,
    )
    anamnese_sistema_urinario = factory.Maybe(
        "fill_anamnese",
        yes_declaration=factory.Faker("paragraph", nb_sentences=2),
        no_declaration=None,
    )
    anamnese_sistema_reprodutor = factory.Maybe(
        "fill_anamnese",
        yes_declaration=factory.Faker("paragraph", nb_sentences=2),
        no_declaration=None,
    )
    anamnese_sistema_locomotor = factory.Maybe(
        "fill_anamnese",
        yes_declaration=factory.Faker("paragraph", nb_sentences=2),
        no_declaration=None,
    )
    anamnese_sistema_neurologico = factory.Maybe(
        "fill_anamnese",
        yes_declaration=factory.Faker("paragraph", nb_sentences=2),
        no_declaration=None,
    )
    anamnese_pele_anexos = factory.Maybe(
        "fill_anamnese",
        yes_declaration=factory.Faker("paragraph", nb_sentences=2),
        no_declaration=None,
    )
    anamnese_olhos = factory.Maybe(
        "fill_anamnese",
        yes_declaration=factory.Faker("paragraph", nb_sentences=2),
        no_declaration=None,
    )

    # Sinais vitais e exame físico geral
    temperatura_celsius = factory.Faker(
        "pydecimal", left_digits=2, right_digits=1, min_value=36.5, max_value=41.0
    )
    frequencia_cardiaca_bpm = factory.Faker("random_int", min=55, max=190)
    frequencia_respiratoria_mpm = factory.Faker("random_int", min=10, max=45)
    tpc_segundos = factory.Faker("random_element", elements=[1, 2, 3, None])
    hidratacao_status = factory.Faker(
        "random_element",
        elements=[
            "Normohidratado",
            "Desidratação Leve (5%)",
            "Desidratação Moderada (8%)",
            "Desidratação Grave (>10%)",
            None,
        ],
    )
    escore_condicao_corporal = factory.Faker(
        "random_element",
        elements=[
            "Ideal (3/5)",
            "Magro (2/5)",
            "Sobrepeso (4/5)",
            "Caquético (1/5)",
            "Obeso (5/5)",
            None,
        ],
    )
    exame_postura = factory.Faker(
        "random_element",
        elements=[
            "Normal",
            "Postura antálgica",
            "Relutância em mover-se",
            "Decúbito lateral",
            None,
        ],
    )
    exame_nivel_consciencia = factory.Faker(
        "random_element",
        elements=["Alerta e responsivo", "Deprimido", "Estuporoso", "Comatoso", None],
    )
    exame_linfonodos_obs = factory.Faker(
        "random_element",
        elements=[
            "Linfonodos normais à palpação",
            "Linfadenomegalia submandibular bilateral",
            "Linfadenomegalia poplítea unilateral",
            "Sem alterações palpáveis",
        ],
    )
    exame_mucosas_obs = factory.Faker(
        "random_element",
        elements=[
            "Mucosas normocoradas e úmidas (MNCH)",
            "Mucosas pálidas",
            "Mucosas congestas",
            "Mucosas ictéricas",
            "Mucosas cianóticas",
        ],
    )
    exame_pulso_ppm = factory.LazyAttribute(
        lambda o: o.frequencia_cardiaca_bpm + fake_pt_br.random_int(min=-5, max=5)
        if o.frequencia_cardiaca_bpm
        else None
    )
    observacoes_exame_fisico_geral = factory.Faker(
        "paragraph",
        nb_sentences=random.randint(1, 3),
        variable_nb_sentences=True,
        locale="pt_BR",
    )

    # Exame físico por sistemas (80% chance de preencher cada seção)
    examefisico_sistema_respiratorio = factory.Maybe(
        "fill_examefisico",
        yes_declaration=factory.Faker("paragraph", nb_sentences=2),
        no_declaration=None,
    )
    examefisico_sistema_cardiovascular = factory.Maybe(
        "fill_examefisico",
        yes_declaration=factory.Faker("paragraph", nb_sentences=2),
        no_declaration=None,
    )
    examefisico_sistema_digestorio = factory.Maybe(
        "fill_examefisico",
        yes_declaration=factory.Faker("paragraph", nb_sentences=2),
        no_declaration=None,
    )
    examefisico_sistema_urinario = factory.Maybe(
        "fill_examefisico",
        yes_declaration=factory.Faker("paragraph", nb_sentences=2),
        no_declaration=None,
    )
    examefisico_sistema_reprodutor = factory.Maybe(
        "fill_examefisico",
        yes_declaration=factory.Faker("paragraph", nb_sentences=2),
        no_declaration=None,
    )
    examefisico_sistema_locomotor = factory.Maybe(
        "fill_examefisico",
        yes_declaration=factory.Faker("paragraph", nb_sentences=2),
        no_declaration=None,
    )
    examefisico_sistema_neurologico = factory.Maybe(
        "fill_examefisico",
        yes_declaration=factory.Faker("paragraph", nb_sentences=2),
        no_declaration=None,
    )
    examefisico_pele_anexos = factory.Maybe(
        "fill_examefisico",
        yes_declaration=factory.Faker("paragraph", nb_sentences=2),
        no_declaration=None,
    )
    examefisico_olhos = factory.Maybe(
        "fill_examefisico",
        yes_declaration=factory.Faker("paragraph", nb_sentences=2),
        no_declaration=None,
    )
    examefisico_ouvidos = factory.Maybe(
        "fill_examefisico",
        yes_declaration=factory.Faker("paragraph", nb_sentences=2),
        no_declaration=None,
    )

    # Diagnóstico e tratamento
    exames_complementares_solicitados = factory.Maybe(
        "needs_exams",
        yes_declaration=factory.Faker("sentence", nb_words=random.randint(3, 8)),
        no_declaration=None,
    )
    tratamento_prescrito = factory.Maybe(
        "needs_treatment",
        yes_declaration=factory.Faker("paragraph", nb_sentences=random.randint(1, 3)),
        no_declaration=None,
    )
    procedimentos_realizados = factory.Maybe(
        "had_procedures",
        yes_declaration=factory.Faker("sentence", nb_words=random.randint(3, 7)),
        no_declaration=None,
    )
    prognostico = factory.Faker(
        "random_element",
        elements=[
            "Bom",
            "Reservado",
            "Mau",
            "Favorável com tratamento",
            "Desfavorável",
        ],
    )
    instrucoes_para_tutor = factory.Faker(
        "paragraph",
        nb_sentences=random.randint(2, 4),
        variable_nb_sentences=True,
        locale="pt_BR",
    )

    # Data de retorno (55% chance de ter retorno)
    data_proximo_retorno = factory.Maybe(
        "needs_return_visit",
        yes_declaration=factory.LazyAttribute(
            lambda o: timezone.make_aware(
                fake_pt_br.future_datetime(end_date=datetime.timedelta(days=120))
            )
        ),
        no_declaration=None,
    )

    # Adiciona sintomas após a criação da consulta
    @factory.post_generation
    def sintomas_apresentados(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            # Se uma lista foi passada na chamada do factory, usa ela.
            # Ex: ConsultaFactory(sintomas_apresentados=[s1, s2])
            self.sintomas_apresentados.add(*extracted)
        else:
            # Lógica padrão: adiciona alguns sintomas aleatórios.
            if Sintoma.objects.exists():
                num_sintomas = random.randint(1, min(Sintoma.objects.count(), 3))
                sintomas_selecionados = random.sample(
                    list(Sintoma.objects.all()), num_sintomas
                )
                self.sintomas_apresentados.add(*sintomas_selecionados)

    # Adicione também os hooks para seus outros campos M2M
    @factory.post_generation
    def diagnosticos_suspeitos(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.diagnosticos_suspeitos.add(*extracted)

    @factory.post_generation
    def diagnosticos_definitivos(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.diagnosticos_definitivos.add(*extracted)

    class Params:
        # Parâmetros para controle de campos opcionais
        fill_anamnese = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=80)
        )
        fill_examefisico = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=80)
        )
        needs_exams = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=65)
        )
        add_suspected_diagnoses = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=70)
        )
        add_definitive_diagnoses = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=50)
        )
        needs_treatment = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=75)
        )
        had_procedures = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=25)
        )
        needs_return_visit = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=55)
        )


class DoencaFactory(factory.django.DjangoModelFactory):
    """Factory para criar objetos Doenca com dados fictícios."""

    class Meta:
        model = Doenca
        # Garante que não sejam criadas doenças duplicadas com o mesmo nome nos testes
        django_get_or_create = ("nome",)

    nome = factory.Sequence(lambda n: f"Doença Fictícia {n}")
    descricao = factory.Faker("text", max_nb_chars=500, locale="pt_BR")

    # Hook para associar sintomas após a criação da doença
    @factory.post_generation
    def sintomas_associados(self, create, extracted, **kwargs):
        if not create:
            # Se não estivermos salvando no banco de dados, não faz nada.
            return

        if extracted:
            # Se uma lista de sintomas foi passada para o factory, usa ela.
            # Ex: DoencaFactory(sintomas_associados=[sintoma1, sintoma2])
            for sintoma in extracted:
                self.sintomas_associados.add(sintoma)
        else:
            # Caso contrário, cria e associa 3 sintomas aleatórios por padrão.
            for _ in range(3):
                self.sintomas_associados.add(SintomaFactory())
