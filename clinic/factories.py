import factory
from factory.django import DjangoModelFactory
from faker import Faker
import random
import datetime
from django.utils import timezone
from validate_docbr import CPF
from .models import Tutor, Paciente, Veterinario, Sintoma, Consulta

fake_pt_br = Faker('pt_BR')
cpf_generator = CPF()


class TutorFactory(DjangoModelFactory):
    class Meta:
        model = Tutor
        django_get_or_create = ('cpf',)

    nome_completo = factory.Faker('name', locale='pt_BR')

    @factory.lazy_attribute
    def cpf(self):
        return cpf_generator.generate(True)

    telefone_principal = factory.LazyAttribute(
        lambda o: fake_pt_br.phone_number())
    telefone_secundario = factory.Maybe(
        'has_secondary_phone',
        yes_declaration=factory.LazyAttribute(
            lambda o: fake_pt_br.phone_number()),
        no_declaration=None
    )
    email = factory.LazyAttribute(
        lambda obj: f"{obj.nome_completo.lower().replace(' ', '_').replace('ã', 'a').replace('ç', 'c').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')}.{fake_pt_br.random_int(min=10, max=999)}@{fake_pt_br.free_email_domain()}"
    )

    endereco_rua = factory.Faker('street_address', locale='pt_BR')
    endereco_numero = factory.Faker('building_number')
    endereco_complemento = factory.Faker(
        'sentence', nb_words=random.randint(1, 3), locale='pt_BR')
    endereco_bairro = factory.Faker('bairro', locale='pt_BR')
    endereco_cidade = factory.Faker('city', locale='pt_BR')
    endereco_uf = factory.Faker('estado_sigla', locale='pt_BR')
    endereco_cep = factory.LazyAttribute(
        lambda o: fake_pt_br.postcode().replace('-', ''))

    observacoes = factory.Faker('paragraph', nb_sentences=random.randint(
        1, 2), variable_nb_sentences=True, locale='pt_BR')

    class Params:
        has_secondary_phone = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=40))


class PacienteFactory(DjangoModelFactory):
    class Meta:
        model = Paciente

    nome = factory.Faker('first_name', locale='pt_BR')
    tutor = factory.SubFactory(TutorFactory)
    especie = factory.Faker('random_element', elements=[
                            x[0] for x in Paciente.ESPECIE_CHOICES])

    @factory.lazy_attribute
    def raca(self):
        if self.especie == 'CANINO':
            return fake_pt_br.random_element(elements=['Labrador', 'Poodle', 'Bulldog', 'Vira-lata', 'Golden Retriever', 'Shih Tzu', 'Yorkshire'])
        elif self.especie == 'FELINO':
            return fake_pt_br.random_element(elements=['Siamês', 'Persa', 'Maine Coon', 'SRD', 'Bengal', 'Ragdoll'])
        elif self.especie == 'AVE':
            return fake_pt_br.random_element(elements=['Calopsita', 'Canário', 'Papagaio', 'Periquito'])
        elif self.especie == 'ROEDOR':
            return fake_pt_br.random_element(elements=['Hamster', 'Porquinho-da-índia', 'Chinchila'])
        elif self.especie == 'LAGOMORFO':
            return fake_pt_br.random_element(elements=['Coelho Mini Lion', 'Coelho Angorá'])
        else:
            return fake_pt_br.word().capitalize()

    data_nascimento = factory.Faker(
        'date_of_birth', minimum_age=0, maximum_age=18)
    sexo = factory.Faker('random_element', elements=[
                         x[0] for x in Paciente.SEXO_CHOICES if x[0] != 'IND'])

    microchip = factory.Maybe(
        'has_microchip',
        yes_declaration=factory.Sequence(
            lambda n: f"900{fake_pt_br.bothify(text='##########??##').upper()}{n}"),
        no_declaration=None
    )
    cor_pelagem = factory.Faker('color_name', locale='pt_BR')
    peso_kg = factory.Faker('pydecimal', left_digits=2, right_digits=3,
                            positive=True, min_value=0.050, max_value=95.0)

    procedencia = factory.Faker('random_element', elements=[
                                "Criador Registrado", "Loja de Animais", "Adoção de Abrigo", "Resgatado", "Nascido em casa", None])
    alimentacao_detalhes = factory.Faker(
        'sentence', nb_words=10, locale='pt_BR')
    contactantes_outros_animais = factory.Faker(
        'sentence', nb_words=8, locale='pt_BR')
    ambiente_onde_vive = factory.Faker('sentence', nb_words=7, locale='pt_BR')
    historico_vacinacao = factory.Faker('random_element', elements=[
                                        "Completo e em dia", "Incompleto", "Não vacinado", "Filhote - em protocolo", "Desconhecido"])
    historico_vermifugacao = factory.Faker('random_element', elements=[
                                           "Regularmente", "Ocasionalmente", "Não vermifugado", "Desconhecido"])
    doencas_pregressas = factory.Maybe('has_past_illness', yes_declaration=factory.Faker(
        'sentence', nb_words=7), no_declaration=None)
    cirurgias_anteriores = factory.Maybe('has_past_surgery', yes_declaration=factory.Faker(
        'sentence', nb_words=6), no_declaration=None)
    alergias_conhecidas = factory.Maybe('has_allergies', yes_declaration=factory.Faker(
        'sentence', nb_words=5), no_declaration=None)

    status = factory.Faker('random_element', elements=[
                           x[0] for x in Paciente.STATUS_CHOICES if x[0] == 'ATIVO'])

    # foto = factory.django.ImageField(color='grey')

    observacoes_clinicas_relevantes = factory.Faker(
        'paragraph', nb_sentences=1, variable_nb_sentences=True, locale='pt_BR')

    class Params:
        has_microchip = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=50))
        has_past_illness = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=20))
        has_past_surgery = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=10))
        has_allergies = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=15))


class VeterinarioFactory(DjangoModelFactory):
    class Meta:
        model = Veterinario
        django_get_or_create = ('crmv',)

    nome_completo = factory.Faker('name', locale='pt_BR')
    crmv = factory.Sequence(
        lambda n: f"CRMV-{fake_pt_br.state_abbr().upper()}-{fake_pt_br.random_number(digits=4, fix_len=True)}{n}")


class SintomaFactory(DjangoModelFactory):
    class Meta:
        model = Sintoma
        django_get_or_create = ('nome',)

    nome = factory.Sequence(
        lambda n: f"Sintoma Auto {fake_pt_br.unique.word().capitalize()}{n}")
    descricao = factory.Faker('sentence', nb_words=random.randint(3, 10))


class ConsultaFactory(DjangoModelFactory):
    class Meta:
        model = Consulta

    paciente = factory.SubFactory(PacienteFactory)
    veterinario_responsavel = factory.SubFactory(VeterinarioFactory)
    data_hora_agendamento = factory.LazyAttribute(
        lambda o: timezone.make_aware(fake_pt_br.date_time_between(start_date='-2y', end_date='now')))
    tipo_consulta = factory.Faker('random_element', elements=[
                                  x[0] for x in Consulta.TIPO_CONSULTA_CHOICES])

    queixa_principal_tutor = factory.Faker(
        'sentence', nb_words=12, locale='pt_BR')
    historico_doenca_atual = factory.Faker('paragraph', nb_sentences=random.randint(
        2, 4), variable_nb_sentences=True, locale='pt_BR')

    anamnese_sistema_respiratorio = factory.Maybe('fill_anamnese', yes_declaration=factory.Faker(
        'paragraph', nb_sentences=2), no_declaration=None)
    anamnese_sistema_cardiovascular = factory.Maybe(
        'fill_anamnese', yes_declaration=factory.Faker('paragraph', nb_sentences=2), no_declaration=None)
    anamnese_sistema_digestorio = factory.Maybe('fill_anamnese', yes_declaration=factory.Faker(
        'paragraph', nb_sentences=2), no_declaration=None)
    anamnese_sistema_urinario = factory.Maybe('fill_anamnese', yes_declaration=factory.Faker(
        'paragraph', nb_sentences=2), no_declaration=None)
    anamnese_sistema_reprodutor = factory.Maybe('fill_anamnese', yes_declaration=factory.Faker(
        'paragraph', nb_sentences=2), no_declaration=None)
    anamnese_sistema_locomotor = factory.Maybe('fill_anamnese', yes_declaration=factory.Faker(
        'paragraph', nb_sentences=2), no_declaration=None)
    anamnese_sistema_neurologico = factory.Maybe('fill_anamnese', yes_declaration=factory.Faker(
        'paragraph', nb_sentences=2), no_declaration=None)
    anamnese_pele_anexos = factory.Maybe('fill_anamnese', yes_declaration=factory.Faker(
        'paragraph', nb_sentences=2), no_declaration=None)
    anamnese_olhos = factory.Maybe('fill_anamnese', yes_declaration=factory.Faker(
        'paragraph', nb_sentences=2), no_declaration=None)

    temperatura_celsius = factory.Faker(
        'pydecimal', left_digits=2, right_digits=1, min_value=36.5, max_value=41.0)
    frequencia_cardiaca_bpm = factory.Faker('random_int', min=55, max=190)
    frequencia_respiratoria_mpm = factory.Faker('random_int', min=10, max=45)
    tpc_segundos = factory.Faker('random_element', elements=[1, 2, 3, None])
    hidratacao_status = factory.Faker('random_element', elements=[
                                      "Normohidratado", "Desidratação Leve (5%)", "Desidratação Moderada (8%)", "Desidratação Grave (>10%)", None])
    escore_condicao_corporal = factory.Faker('random_element', elements=[
                                             "Ideal (3/5)", "Magro (2/5)", "Sobrepeso (4/5)", "Caquético (1/5)", "Obeso (5/5)", None])
    exame_postura = factory.Faker('random_element', elements=[
                                  "Normal", "Postura antálgica", "Relutância em mover-se", "Decúbito lateral", None])
    exame_nivel_consciencia = factory.Faker('random_element', elements=[
                                            "Alerta e responsivo", "Deprimido", "Estuporoso", "Comatoso", None])
    exame_linfonodos_obs = factory.Faker('random_element', elements=[
                                         "Linfonodos normais à palpação", "Linfadenomegalia submandibular bilateral", "Linfadenomegalia poplítea unilateral", "Sem alterações palpáveis"])
    exame_mucosas_obs = factory.Faker('random_element', elements=[
                                      "Mucosas normocoradas e úmidas (MNCH)", "Mucosas pálidas", "Mucosas congestas", "Mucosas ictéricas", "Mucosas cianóticas"])
    exame_pulso_ppm = factory.LazyAttribute(
        lambda o: o.frequencia_cardiaca_bpm + fake_pt_br.random_int(min=-5, max=5) if o.frequencia_cardiaca_bpm else None)
    observacoes_exame_fisico_geral = factory.Faker('paragraph', nb_sentences=random.randint(
        1, 3), variable_nb_sentences=True, locale='pt_BR')

    examefisico_sistema_respiratorio = factory.Maybe(
        'fill_examefisico', yes_declaration=factory.Faker('paragraph', nb_sentences=2), no_declaration=None)
    examefisico_sistema_cardiovascular = factory.Maybe(
        'fill_examefisico', yes_declaration=factory.Faker('paragraph', nb_sentences=2), no_declaration=None)
    examefisico_sistema_digestorio = factory.Maybe('fill_examefisico', yes_declaration=factory.Faker(
        'paragraph', nb_sentences=2), no_declaration=None)
    examefisico_sistema_urinario = factory.Maybe('fill_examefisico', yes_declaration=factory.Faker(
        'paragraph', nb_sentences=2), no_declaration=None)
    examefisico_sistema_reprodutor = factory.Maybe('fill_examefisico', yes_declaration=factory.Faker(
        'paragraph', nb_sentences=2), no_declaration=None)
    examefisico_sistema_locomotor = factory.Maybe('fill_examefisico', yes_declaration=factory.Faker(
        'paragraph', nb_sentences=2), no_declaration=None)
    examefisico_sistema_neurologico = factory.Maybe(
        'fill_examefisico', yes_declaration=factory.Faker('paragraph', nb_sentences=2), no_declaration=None)
    examefisico_pele_anexos = factory.Maybe('fill_examefisico', yes_declaration=factory.Faker(
        'paragraph', nb_sentences=2), no_declaration=None)
    examefisico_olhos = factory.Maybe('fill_examefisico', yes_declaration=factory.Faker(
        'paragraph', nb_sentences=2), no_declaration=None)
    examefisico_ouvidos = factory.Maybe('fill_examefisico', yes_declaration=factory.Faker(
        'paragraph', nb_sentences=2), no_declaration=None)

    suspeitas_diagnosticas = factory.Faker('paragraph', nb_sentences=random.randint(
        1, 3), variable_nb_sentences=True, locale='pt_BR')
    exames_complementares_solicitados = factory.Maybe('needs_exams', yes_declaration=factory.Faker(
        'sentence', nb_words=random.randint(3, 8)), no_declaration=None)
    diagnostico_definitivo = factory.Maybe('has_definitive_diagnosis', yes_declaration=factory.Faker(
        'sentence', nb_words=random.randint(2, 5)), no_declaration=None)
    tratamento_prescrito = factory.Maybe('needs_treatment', yes_declaration=factory.Faker(
        'paragraph', nb_sentences=random.randint(1, 3)), no_declaration=None)
    procedimentos_realizados = factory.Maybe('had_procedures', yes_declaration=factory.Faker(
        'sentence', nb_words=random.randint(3, 7)), no_declaration=None)
    prognostico = factory.Faker('random_element', elements=[
                                "Bom", "Reservado", "Mau", "Favorável com tratamento", "Desfavorável"])
    instrucoes_para_tutor = factory.Faker('paragraph', nb_sentences=random.randint(
        2, 4), variable_nb_sentences=True, locale='pt_BR')
    data_proximo_retorno = factory.Maybe('needs_return_visit',
                                         yes_declaration=factory.LazyAttribute(
                                             lambda o: timezone.make_aware(
                                                 fake_pt_br.future_datetime(end_date=datetime.timedelta(days=120)))),
                                         no_declaration=None)

    @factory.post_generation
    def sintomas_apresentados(obj, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for sintoma in extracted:
                obj.sintomas_apresentados.add(sintoma)
        else:
            if Sintoma.objects.exists():
                num_sintomas_a_adicionar = random.randint(
                    0, min(Sintoma.objects.count(), 3))
                if num_sintomas_a_adicionar > 0:
                    sintomas_disponiveis = list(Sintoma.objects.all())
                    sintomas_selecionados = random.sample(
                        sintomas_disponiveis, num_sintomas_a_adicionar)
                    for sintoma in sintomas_selecionados:
                        obj.sintomas_apresentados.add(sintoma)

    class Params:
        fill_anamnese = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=80))
        fill_examefisico = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=80))
        needs_exams = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=65))
        has_definitive_diagnosis = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=50))
        needs_treatment = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=75))
        had_procedures = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=25))
        needs_return_visit = factory.LazyAttribute(
            lambda o: fake_pt_br.boolean(chance_of_getting_true=55))
