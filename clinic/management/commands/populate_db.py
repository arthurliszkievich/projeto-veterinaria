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
# Importe seus modelos se precisar de lógica mais específica
from clinic.models import Sintoma, Doenca, Consulta

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

        # Limpar dados antigos (CUIDADO: SÓ EM AMBIENTE DE DESENVOLVIMENTO!)
        # Se você quiser limpar antes de popular:
        # self.stdout.write('Limpando dados antigos...')
        # Consulta.objects.all().delete()
        # Doenca.objects.all().delete()
        # Sintoma.objects.all().delete()
        # Paciente.objects.all().delete()
        # Tutor.objects.all().delete()
        # Veterinario.objects.all().delete()

        # 1. Criar Sintomas
        self.stdout.write(f'Criando {NUM_SINTOMAS} sintomas...')
        sintomas_criados = []
        for _ in range(NUM_SINTOMAS):
            sintomas_criados.append(SintomaFactory())
        self.stdout.write(self.style.SUCCESS(
            f'{len(sintomas_criados)} sintomas criados.'))

        # 2. Criar Doenças e associar sintomas
        self.stdout.write(
            f'Criando {NUM_DOENCAS} doenças e associando sintomas...')
        doencas_criadas = []
        for _ in range(NUM_DOENCAS):
            doenca = DoencaFactory()
            # Associar um número aleatório de sintomas (1 a 5) a cada doença
            num_sintomas_para_doenca = random.randint(
                1, min(5, len(sintomas_criados)))
            sintomas_para_associar = random.sample(
                sintomas_criados, num_sintomas_para_doenca)
            doenca.sintomas_associados.set(sintomas_para_associar)
            doencas_criadas.append(doenca)
        self.stdout.write(self.style.SUCCESS(
            f'{len(doencas_criadas)} doenças criadas.'))

        # 3. Criar Veterinários
        self.stdout.write(f'Criando {NUM_VETERINARIOS} veterinários...')
        veterinarios_criados = [VeterinarioFactory()
                                for _ in range(NUM_VETERINARIOS)]
        self.stdout.write(self.style.SUCCESS(
            f'{len(veterinarios_criados)} veterinários criados.'))

        # 4. Criar Tutores e seus Pacientes
        self.stdout.write(f'Criando {NUM_TUTORES} tutores e seus pacientes...')
        tutores_criados = []
        pacientes_criados = []
        for _ in range(NUM_TUTORES):
            tutor = TutorFactory()
            tutores_criados.append(tutor)
            num_pacientes = random.randint(0, NUM_PACIENTES_POR_TUTOR_MAX)
            for _ in range(num_pacientes):
                pacientes_criados.append(PacienteFactory(tutor=tutor))
        self.stdout.write(self.style.SUCCESS(
            f'{len(tutores_criados)} tutores e {len(pacientes_criados)} pacientes criados.'))

        # 5. Criar Consultas (se houver pacientes e veterinários)
        if pacientes_criados and veterinarios_criados and sintomas_criados and doencas_criadas:
            self.stdout.write(f'Criando {NUM_CONSULTAS} consultas...')
            consultas_criadas = []
            for _ in range(NUM_CONSULTAS):
                paciente_aleatorio = random.choice(pacientes_criados)
                veterinario_aleatorio = random.choice(veterinarios_criados)

                # Adiciona alguns sintomas apresentados aleatoriamente
                num_sint_apresentados = random.randint(
                    0, min(4, len(sintomas_criados)))
                sint_apresentados_objs = []
                if num_sint_apresentados > 0:
                    sint_apresentados_objs = random.sample(
                        sintomas_criados, num_sint_apresentados)

                # Usando a factory de Consulta, que pode ter lógica para add_sintomas_apresentados
                # Ou você pode definir aqui:
                consulta = ConsultaFactory(
                    paciente=paciente_aleatorio,
                    veterinario_responsavel=veterinario_aleatorio,
                    # Se sua factory já tem o Params para add_sintomas_apresentados, pode confiar nela
                    # ou definir explicitamente
                    sintomas_apresentados=sint_apresentados_objs
                    # Deixe os campos de diagnóstico serem preenchidos pela lógica do ViewSet/Signal
                    # ou preencha-os aqui se quiser simular o processo completo.
                )
                consultas_criadas.append(consulta)
            self.stdout.write(self.style.SUCCESS(
                f'{len(consultas_criadas)} consultas criadas.'))
        else:
            self.stdout.write(self.style.WARNING(
                'Não foi possível criar consultas (faltam pacientes, veterinários, sintomas ou doenças).'))

        self.stdout.write(self.style.SUCCESS(
            'Banco de dados populado com sucesso!'))
