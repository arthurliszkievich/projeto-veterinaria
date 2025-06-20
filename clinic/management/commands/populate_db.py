# clinic/management/commands/populate_db.py
from django.core.management.base import BaseCommand
from django.db import transaction
import random

# Importe suas factories
from clinic.factories import (
    TutorFactory,
    PacienteFactory,
    VeterinarioFactory,
    SintomaFactory,
    DoencaFactory,
    ConsultaFactory
)
# Importe seus modelos para a limpeza e lógica específica
from clinic.models import (
    Tutor,
    Paciente,
    Veterinario,
    Sintoma,
    Doenca,
    Consulta
)

# Defina o número de instâncias que você quer criar
NUM_SINTOMAS = 20
NUM_DOENCAS = 10
NUM_TUTORES = 15
NUM_PACIENTES_POR_TUTOR_MAX = 3
NUM_VETERINARIOS = 5
NUM_CONSULTAS = 30


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados fictícios para desenvolvimento e teste.'

    @transaction.atomic  # Garante que todas as operações são feitas em uma única transação
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
            'Iniciando a população do banco de dados...'))

        # --------------------------------------------------------------------------
        # SEÇÃO DE LIMPEZA DE DADOS ANTIGOS
        # Descomente as linhas abaixo se quiser limpar o banco antes de popular.
        # CUIDADO: SÓ USE EM AMBIENTE DE DESENVOLVIMENTO!
        # --------------------------------------------------------------------------
        self.stdout.write(self.style.WARNING(
            'Limpando dados antigos... (SE DESCOMENTADO)'))
        # A ordem é importante para evitar problemas com ForeignKeys protegidas.
        # Comece pelos modelos que dependem de outros.
        Consulta.objects.all().delete()
        # Doenças podem ter M2M com Sintomas. Deletar Doenca remove essas relações.
        Doenca.objects.all().delete()
        # Pacientes dependem de Tutores.
        Paciente.objects.all().delete()
        Sintoma.objects.all().delete()
        Tutor.objects.all().delete()
        Veterinario.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(
            'Dados antigos limpos com sucesso! (SE DESCOMENTADO)'))
        # --------------------------------------------------------------------------

        # # 1. Criar Sintomas
        # self.stdout.write(f'Criando {NUM_SINTOMAS} sintomas...')
        # sintomas_criados = [SintomaFactory() for _ in range(NUM_SINTOMAS)]
        # self.stdout.write(self.style.SUCCESS(
        #     f'{len(sintomas_criados)} sintomas criados.'))

        # # 2. Criar Doenças e associar sintomas
        # if not sintomas_criados:
        #     self.stdout.write(self.style.WARNING(
        #         'Nenhum sintoma criado. Pulando criação de doenças.'))
        #     doencas_criadas = []
        # else:
        #     self.stdout.write(
        #         f'Criando {NUM_DOENCAS} doenças e associando sintomas...')
        #     doencas_criadas = []
        #     for _ in range(NUM_DOENCAS):
        #         doenca = DoencaFactory()
        #         # Associar um número aleatório de sintomas (1 a 5) a cada doença
        #         # Garante que não tentamos pegar mais amostras do que existem
        #         max_sintomas_para_doenca = min(5, len(sintomas_criados))
        #         if max_sintomas_para_doenca > 0:  # Só associa se houver sintomas e limite > 0
        #             num_sintomas_para_doenca = random.randint(
        #                 1, max_sintomas_para_doenca)
        #             sintomas_para_associar = random.sample(
        #                 sintomas_criados, num_sintomas_para_doenca)
        #             doenca.sintomas_associados.set(sintomas_para_associar)
        #         doencas_criadas.append(doenca)
        #     self.stdout.write(self.style.SUCCESS(
        #         f'{len(doencas_criadas)} doenças criadas.'))

        # # 3. Criar Veterinários
        # self.stdout.write(f'Criando {NUM_VETERINARIOS} veterinários...')
        # veterinarios_criados = [VeterinarioFactory()
        #                         for _ in range(NUM_VETERINARIOS)]
        # self.stdout.write(self.style.SUCCESS(
        #     f'{len(veterinarios_criados)} veterinários criados.'))

        # # 4. Criar Tutores e seus Pacientes
        # self.stdout.write(f'Criando {NUM_TUTORES} tutores e seus pacientes...')
        # tutores_criados = []
        # pacientes_criados_total = []
        # for _ in range(NUM_TUTORES):
        #     tutor = TutorFactory()
        #     tutores_criados.append(tutor)
        #     num_pacientes_para_este_tutor = random.randint(
        #         0, NUM_PACIENTES_POR_TUTOR_MAX)
        #     for _ in range(num_pacientes_para_este_tutor):
        #         pacientes_criados_total.append(PacienteFactory(tutor=tutor))
        # self.stdout.write(self.style.SUCCESS(
        #     f'{len(tutores_criados)} tutores e {len(pacientes_criados_total)} pacientes criados.'))

        # # 5. Criar Consultas (se houver pacientes, veterinários, sintomas e doenças)
        # if pacientes_criados_total and veterinarios_criados and sintomas_criados:
        #     self.stdout.write(f'Criando {NUM_CONSULTAS} consultas...')
        #     consultas_criadas_total = []
        #     for _ in range(NUM_CONSULTAS):
        #         paciente_aleatorio = random.choice(pacientes_criados_total)
        #         veterinario_aleatorio = random.choice(veterinarios_criados)

        #         # Adiciona alguns sintomas apresentados aleatoriamente
        #         # Garante que não tentamos pegar mais amostras do que existem
        #         max_sint_apresentados = min(4, len(sintomas_criados))
        #         sint_apresentados_objs = []
        #         if max_sint_apresentados > 0:  # Só associa se houver sintomas e limite > 0
        #             num_sint_apresentados = random.randint(
        #                 0, max_sint_apresentados)
        #             if num_sint_apresentados > 0:
        #                 sint_apresentados_objs = random.sample(
        #                     sintomas_criados, num_sint_apresentados)

        #         # Cria a consulta. A lógica de sugestão de diagnóstico (se integrada no save do model
        #         # ou via signals no ViewSet) será acionada aqui se sintomas_apresentados forem definidos.
        #         consulta = ConsultaFactory(
        #             paciente=paciente_aleatorio,
        #             veterinario_responsavel=veterinario_aleatorio,
        #             sintomas_apresentados=sint_apresentados_objs
        #             # Se você quiser simular diagnósticos suspeitos e definitivos já preenchidos
        #             # pela factory, você pode adicionar lógica aqui ou nos Params da ConsultaFactory:
        #             # add_diagnosticos_suspeitos=True (se configurado na factory)
        #             # ou passar uma lista de objetos Doenca diretamente.
        #         )
        #         consultas_criadas_total.append(consulta)
        #     self.stdout.write(self.style.SUCCESS(
        #         f'{len(consultas_criadas_total)} consultas criadas.'))
        # else:
        #     self.stdout.write(self.style.WARNING(
        #         'Não foi possível criar consultas (faltam pacientes, veterinários ou sintomas).'))

        # self.stdout.write(self.style.SUCCESS(
        #     'Banco de dados populado com sucesso!'))
