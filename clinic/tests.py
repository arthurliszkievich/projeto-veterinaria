# clinic/tests.py
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
import datetime
import decimal  # Para comparar Decimals

from .models import Tutor, Paciente, Veterinario, Sintoma, Consulta
from .factories import (
    TutorFactory, PacienteFactory, VeterinarioFactory, SintomaFactory, ConsultaFactory
)
from .serializers import (  # Importar todos os serializers que você pode querer usar para comparações
    TutorSerializer, PacienteSerializer, VeterinarioSerializer, SintomaSerializer, ConsultaSerializer
)

# --- Classe Base para Testes de API Autenticados ---


class AuthenticatedAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='testveterinario', email='testvet@example.com', password='testpassword123')
        # Autentica o cliente de teste
        self.client.force_authenticate(user=self.user)


# --- Testes para a API de Tutor ---
class TutorAPITests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.list_create_url = reverse('tutor-list')
        self.tutor1 = TutorFactory(
            # CPF de exemplo
            nome_completo="Ana Carolina", email="ana.carolina@example.com", cpf="111.111.111-11")
        self.tutor2 = TutorFactory(nome_completo="Carlos Alberto",
                                   email="carlos.alberto@example.com", cpf="222.222.222-22")
        self.detail_url_tutor1 = reverse(
            'tutor-detail', kwargs={'pk': self.tutor1.pk})

    def test_listar_tutores(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_criar_tutor_valido(self):
        from validate_docbr import CPF  # Para gerar CPF válido para o teste
        cpf_gen = CPF()
        valid_cpf_for_test = cpf_gen.generate(True)

        data = {
            "nome_completo": "Fernanda Lima",
            "cpf": valid_cpf_for_test,
            "email": "fernanda.lima@example.com",
            "telefone_principal": "21987654321",
            "endereco_rua": "Rua das Palmeiras", "endereco_numero": "123",
            "endereco_bairro": "Botafogo", "endereco_cidade": "Rio de Janeiro", "endereco_uf": "RJ", "endereco_cep": "22270-000"
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Tutor.objects.filter(
            email="fernanda.lima@example.com").exists())

    def test_criar_tutor_cpf_invalido_pela_validacao_do_serializer(self):
        # Este teste depende de você ter uma validação de CPF no TutorSerializer
        data = {"nome_completo": "Teste CPF Inválido",
                "cpf": "000.000.000-00", "email": "cpf.invalido@example.com"}
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cpf', response.data)  # Espera erro no campo CPF

    def test_criar_tutor_cpf_duplicado(self):
        data = {"nome_completo": "Outra Ana",
                "cpf": self.tutor1.cpf, "email": "outra.ana@example.com"}
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cpf', response.data)

    def test_recuperar_detalhe_tutor(self):
        response = self.client.get(self.detail_url_tutor1)
        serializer_esperado = TutorSerializer(self.tutor1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Compare campos chave
        self.assertEqual(
            response.data['nome_completo'], serializer_esperado.data['nome_completo'])

    def test_atualizar_tutor_patch(self):
        data_parcial = {"telefone_principal": "11912345678",
                        "observacoes": "Cliente VIP"}
        response = self.client.patch(
            self.detail_url_tutor1, data_parcial, format='json')
        self.tutor1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.tutor1.telefone_principal, "11912345678")
        self.assertEqual(self.tutor1.observacoes, "Cliente VIP")

    def test_deletar_tutor_sem_pacientes_associados(self):
        tutor_para_deletar = TutorFactory()  # Cria um tutor sem pacientes
        url_delecao = reverse(
            'tutor-detail', kwargs={'pk': tutor_para_deletar.pk})
        response = self.client.delete(url_delecao)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tutor.objects.filter(
            pk=tutor_para_deletar.pk).exists())

    def test_deletar_tutor_com_pacientes_protegidos_retorna_erro(self):
        # PacienteFactory cria um paciente associado ao self.tutor1 por padrão (via SubFactory)
        PacienteFactory(tutor=self.tutor1)
        response = self.client.delete(self.detail_url_tutor1)
        # Esperamos um erro porque Paciente.tutor tem on_delete=models.PROTECT
        # O DRF geralmente retorna 409 Conflict ou 400 Bad Request para ProtectedError.
        # Vamos verificar se o tutor ainda existe.
        self.assertIn(response.status_code, [
                      status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT])
        self.assertTrue(Tutor.objects.filter(pk=self.tutor1.pk).exists())


# --- Testes para a API de Paciente ---
# (Esqueleto similar ao TutorAPITests, você precisará preencher com testes específicos)
class PacienteAPITests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.list_create_url = reverse('paciente-list')
        self.tutor_base = TutorFactory()
        self.paciente1 = PacienteFactory(
            nome="Rex", tutor=self.tutor_base, especie="CANINO", raca="Labrador")
        self.paciente2 = PacienteFactory(
            nome="Mimi", tutor=self.tutor_base, especie="FELINO", raca="Siamês")
        self.detail_url_paciente1 = reverse(
            'paciente-detail', kwargs={'pk': self.paciente1.pk})

    def test_listar_pacientes(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_criar_paciente_valido(self):
        data = {
            "nome": "Bolinha", "tutor": self.tutor_base.pk, "especie": "CANINO",
            "raca": "Poodle", "sexo": "MC",
            # 2 anos atrás
            "data_nascimento": (timezone.now() - timezone.timedelta(days=365*2)).strftime('%Y-%m-%d'),
            "peso_kg": "12.500"
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Paciente.objects.filter(nome="Bolinha").exists())

    def test_criar_paciente_sem_tutor_retorna_erro(self):
        data = {"nome": "Fantasma", "especie": "OUTRO"}
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('tutor', response.data)

    def test_filtrar_pacientes_por_especie_e_raca(self):
        PacienteFactory(tutor=self.tutor_base,
                        especie="CANINO", raca="Golden Retriever")
        response = self.client.get(self.list_create_url, {
                                   'especie': 'CANINO', 'raca__icontains': 'Labrador'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['nome'], "Rex")


# --- Testes para a API de Veterinario ---
class VeterinarioAPITests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.list_create_url = reverse('veterinario-list')
        self.vet1 = VeterinarioFactory(
            nome_completo="Dr. Dolittle", crmv="CRMV-SP-00001")
        self.vet2 = VeterinarioFactory(
            nome_completo="Dr. John", crmv="CRMV-RJ-00002")
        self.detail_url_vet1 = reverse(
            'veterinario-detail', kwargs={'pk': self.vet1.pk})

    def test_listar_veterinarios(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_criar_veterinario(self):
        data = {"nome_completo": "Dra. Lisa", "crmv": "CRMV-MG-12345"}
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Veterinario.objects.filter(
            crmv="CRMV-MG-12345").exists())


# --- Testes para a API de Sintoma (como já tínhamos, com pequenas melhorias) ---
class SintomaAPITests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.list_create_url = reverse('sintoma-list')
        self.sintoma_febre = SintomaFactory(
            nome="Febre", descricao="Temperatura corporal elevada.")
        self.sintoma_tosse = SintomaFactory(
            nome="Tosse Seca", descricao="Tosse sem expectoração.")
        self.sintoma_apatia = SintomaFactory(
            nome="Apatia", descricao="Falta de energia e interesse.")
        self.detail_url_febre = reverse(
            'sintoma-detail', kwargs={'pk': self.sintoma_febre.pk})

    # (Mantenha os testes de Sintoma que você já tinha e adicione mais se necessário)
    def test_listar_sintomas(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_criar_sintoma_valido(self):
        data = {'nome': 'Vômito Agudo',
                'descricao': 'Expulsão do conteúdo estomacal de forma súbita.'}
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Sintoma.objects.filter(nome='Vômito Agudo').exists())

    def test_filtrar_sintomas_por_nome_exato(self):
        response = self.client.get(self.list_create_url, {'nome': 'Febre'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results']
                         [0]['id'], self.sintoma_febre.id)


# --- Testes para a API de Consulta (como já tínhamos, com pequenas melhorias) ---
class ConsultaAPITests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.tutor1 = TutorFactory(nome_completo="Carlos Silva")
        self.paciente_rex = PacienteFactory(
            tutor=self.tutor1, nome="Rex", especie="CANINO")
        self.vet1 = VeterinarioFactory(nome_completo="Dr. House")
        self.sintoma_febre_consulta = SintomaFactory(
            nome="Febre Consulta")  # Nome único para este teste
        self.sintoma_tosse_consulta = SintomaFactory(nome="Tosse Consulta")

        self.list_create_url = reverse('consulta-list')

        self.consulta_rex = ConsultaFactory(
            paciente=self.paciente_rex,
            veterinario_responsavel=self.vet1,
            tipo_consulta='ROTINA',
            data_hora_agendamento=timezone.make_aware(
                datetime.datetime(2023, 1, 10, 10, 0, 0)),
            sintomas_apresentados=[self.sintoma_febre_consulta]
        )
        self.detail_url_consulta_rex = reverse(
            'consulta-detail', kwargs={'pk': self.consulta_rex.pk})

    def test_listar_consultas(self):
        ConsultaFactory()  # Cria mais uma
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_criar_consulta_com_todos_os_campos_texto_anamnese_exame(self):
        """ Testa a criação de uma consulta preenchendo todos os campos de texto opcionais."""
        paciente_novo = PacienteFactory()
        data = {
            "paciente": paciente_novo.pk,
            "veterinario_responsavel": self.vet1.pk,
            "data_hora_agendamento": timezone.now().isoformat(),
            "tipo_consulta": "EMERGENCIA",
            "queixa_principal_tutor": "Animal muito quieto e não come.",
            "historico_doenca_atual": "Começou ontem à noite, piorou hoje.",
            "anamnese_sistema_respiratorio": "Respiração normal.",
            "anamnese_sistema_cardiovascular": "Sem histórico de problemas cardíacos.",
            "anamnese_sistema_digestorio": "Recusa alimentar, bebeu pouca água.",
            # ... adicione valores para TODOS os outros campos de anamnese e exame físico ...
            "examefisico_ouvidos": "Limpos, sem secreção.",
            "temperatura_celsius": "39.1",
            "frequencia_cardiaca_bpm": 120,
            "observacoes_exame_fisico_geral": "Animal apático, mucosas levemente pálidas.",
            "sintoma_ids_para_escrita": [self.sintoma_febre_consulta.pk, self.sintoma_tosse_consulta.pk],
            "suspeitas_diagnosticas": "Virose ou infecção bacteriana.",
            "tratamento_prescrito": "Observação, fluidoterapia se necessário."
        }
        response = self.client.post(self.list_create_url, data, format='json')
        # print(response.content) # Descomente para depurar se houver erro
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Consulta.objects.filter(
            pk=response.data['id']).exists())
        nova_consulta = Consulta.objects.get(pk=response.data['id'])
        self.assertEqual(nova_consulta.anamnese_sistema_digestorio,
                         "Recusa alimentar, bebeu pouca água.")
        self.assertEqual(nova_consulta.sintomas_apresentados.count(), 2)

    def test_decimal_field_validation_consulta(self):
        """Testa validação de campo decimal (ex: temperatura)."""
        data = {
            "paciente": self.paciente_rex.pk,
            "tipo_consulta": "ROTINA",
            "temperatura_celsius": "MUITO ALTA"  # Valor inválido para DecimalField
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('temperatura_celsius', response.data)
