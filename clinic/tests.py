from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .factories import (
    ConsultaFactory,
    DoencaFactory,
    PacienteFactory,
    SintomaFactory,
    TutorFactory,
    VeterinarioFactory,
)
from .models import Consulta, Paciente, Sintoma, Tutor, Veterinario
from .serializers import TutorSerializer
from .services import sugerir_diagnosticos

# --- Classe Base para Testes de API Autenticados ---


class AuthenticatedAPITestCase(APITestCase):
    """Classe base para testes que requerem autenticação"""

    def setUp(self):
        super().setUp()
        # Cria usuário de teste e autentica
        self.user = User.objects.create_user(
            username="testveterinario",
            email="testvet@example.com",
            password="testpassword123",
        )
        self.client.force_authenticate(user=self.user)


# --- Testes para a API de Tutor ---
class TutorAPITests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        # URL para listagem e criação
        self.list_create_url = reverse("tutor-list")
        # Cria dois tutores de exemplo com dados controlados
        self.tutor1 = TutorFactory(
            nome_completo="Ana Carolina",
            email="ana.carolina@example.com",
            cpf="111.111.111-11",
        )
        self.tutor2 = TutorFactory(
            nome_completo="Carlos Alberto",
            email="carlos.alberto@example.com",
            cpf="222.222.222-22",
        )
        self.detail_url_tutor1 = reverse("tutor-detail", kwargs={"pk": self.tutor1.pk})

    def test_listar_tutores(self):
        """Testa a listagem de todos os tutores"""
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verifica quantidade de resultados
        self.assertEqual(response.data["count"], 2)

    def test_criar_tutor_valido(self):
        """Testa a criação de um tutor com dados válidos"""
        from validate_docbr import CPF

        cpf_gen = CPF()
        valid_cpf_for_test = cpf_gen.generate(True)  # Gera CPF válido

        data = {
            "nome_completo": "Fernanda Lima",
            "cpf": valid_cpf_for_test,
            "email": "fernanda.lima@example.com",
            "telefone_principal": "21987654321",
            "endereco_rua": "Rua das Palmeiras",
            "endereco_numero": "123",
            "endereco_bairro": "Botafogo",
            "endereco_cidade": "Rio de Janeiro",
            "endereco_uf": "RJ",
            "endereco_cep": "22270-000",
        }
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Tutor.objects.filter(email="fernanda.lima@example.com").exists()
        )

    def test_criar_tutor_cpf_invalido_pela_validacao_do_serializer(self):
        """Testa validação de CPF inválido durante criação de tutor"""
        data = {
            "nome_completo": "Teste CPF Inválido",
            "cpf": "000.000.000-00",  # CPF inválido
            "email": "cpf.invalido@example.com",
        }
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Verifica mensagem de erro no campo
        self.assertIn("cpf", response.data)

    def test_criar_tutor_cpf_duplicado(self):
        """Testa tentativa de criar tutor com CPF já existente"""
        data = {
            "nome_completo": "Outra Ana",
            "cpf": self.tutor1.cpf,  # CPF duplicado
            "email": "outra.ana@example.com",
        }
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cpf", response.data)  # Verifica mensagem de erro

    def test_recuperar_detalhe_tutor(self):
        """Testa a recuperação de detalhes de um tutor específico"""
        response = self.client.get(self.detail_url_tutor1)
        serializer_esperado = TutorSerializer(self.tutor1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Compara dados importantes
        self.assertEqual(
            response.data["nome_completo"], serializer_esperado.data["nome_completo"]
        )

    def test_atualizar_tutor_patch(self):
        """Testa atualização parcial de um tutor"""
        data_parcial = {
            "telefone_principal": "11912345678",
            "observacoes": "Cliente VIP",
        }
        response = self.client.patch(
            self.detail_url_tutor1, data_parcial, format="json"
        )
        self.tutor1.refresh_from_db()  # Atualiza objeto do banco
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.tutor1.telefone_principal, "11912345678")
        self.assertEqual(self.tutor1.observacoes, "Cliente VIP")

    def test_deletar_tutor_sem_pacientes_associados(self):
        """Testa exclusão de tutor sem pacientes associados"""
        tutor_para_deletar = TutorFactory()  # Cria tutor sem pacientes
        url_delecao = reverse("tutor-detail", kwargs={"pk": tutor_para_deletar.pk})
        response = self.client.delete(url_delecao)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tutor.objects.filter(pk=tutor_para_deletar.pk).exists())

    def test_deletar_tutor_com_pacientes_protegidos_retorna_erro(self):
        """Testa proteção contra exclusão de tutor com pacientes associados"""
        PacienteFactory(tutor=self.tutor1)  # Associa paciente ao tutor
        response = self.client.delete(self.detail_url_tutor1)
        # Verifica se retorna erro (400 ou 409)
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT],
        )
        self.assertTrue(Tutor.objects.filter(pk=self.tutor1.pk).exists())


# --- Testes para a API de Paciente ---
class PacienteAPITests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        # URL para listagem e criação
        self.list_create_url = reverse("paciente-list")
        self.tutor_base = TutorFactory()  # Tutor base para pacientes
        # Cria dois pacientes de exemplo
        self.paciente1 = PacienteFactory(
            nome="Rex", tutor=self.tutor_base, especie="CANINO", raca="Labrador"
        )
        self.paciente2 = PacienteFactory(
            nome="Mimi", tutor=self.tutor_base, especie="FELINO", raca="Siamês"
        )
        self.detail_url_paciente1 = reverse(
            "paciente-detail", kwargs={"pk": self.paciente1.pk}
        )

    def test_listar_pacientes(self):
        """Testa listagem de todos os pacientes"""
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)  # Verifica quantidade

    def test_criar_paciente_valido(self):
        """Testa criação de paciente com dados válidos"""
        data = {
            "nome": "Bolinha",
            "tutor": self.tutor_base.pk,
            "especie": "CANINO",
            "raca": "Poodle",
            "sexo": "MC",
            "data_nascimento": (
                timezone.now() - timezone.timedelta(days=365 * 2)
            ).strftime("%Y-%m-%d"),
            "peso_kg": "12.500",
        }
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Paciente.objects.filter(nome="Bolinha").exists())

    def test_criar_paciente_sem_tutor_retorna_erro(self):
        """Testa tentativa de criar paciente sem tutor associado"""
        data = {"nome": "Fantasma", "especie": "OUTRO"}
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("tutor", response.data)  # Verifica mensagem de erro

    def test_filtrar_pacientes_por_especie_e_raca(self):
        """Testa filtros combinados por espécie e raça"""
        # Cria mais um paciente canino
        PacienteFactory(
            tutor=self.tutor_base, especie="CANINO", raca="Golden Retriever"
        )

        # Filtra por espécie canino e raça contendo 'Labrador'
        response = self.client.get(
            self.list_create_url, {"especie": "CANINO", "raca__icontains": "Labrador"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)  # Deve encontrar apenas 1
        self.assertEqual(response.data["results"][0]["nome"], "Rex")  # Verifica nome


# --- Testes para a API de Veterinario ---
class VeterinarioAPITests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        # URL para listagem e criação
        self.list_create_url = reverse("veterinario-list")
        # Cria dois veterinários de exemplo
        self.vet1 = VeterinarioFactory(
            nome_completo="Dr. Dolittle", crmv="CRMV-SP-00001"
        )
        self.vet2 = VeterinarioFactory(nome_completo="Dr. John", crmv="CRMV-RJ-00002")
        self.detail_url_vet1 = reverse(
            "veterinario-detail", kwargs={"pk": self.vet1.pk}
        )

    def test_listar_veterinarios(self):
        """Testa listagem de todos os veterinários"""
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)  # Verifica quantidade

    def test_criar_veterinario(self):
        """Testa criação de veterinário com dados válidos"""
        data = {
            "nome_completo": "Dra. Lisa",
            "crmv": "CRMV-MG-12345",  # CRMV único
        }
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Veterinario.objects.filter(crmv="CRMV-MG-12345").exists())


# --- Testes para a API de Sintoma ---
class SintomaAPITests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        # URL para listagem e criação
        self.list_create_url = reverse("sintoma-list")
        # Cria sintomas de exemplo
        self.sintoma_febre = SintomaFactory(
            nome="Febre", descricao="Temperatura corporal elevada."
        )
        self.sintoma_tosse = SintomaFactory(
            nome="Tosse Seca", descricao="Tosse sem expectoração."
        )
        self.sintoma_apatia = SintomaFactory(
            nome="Apatia", descricao="Falta de energia e interesse."
        )
        self.detail_url_febre = reverse(
            "sintoma-detail", kwargs={"pk": self.sintoma_febre.pk}
        )

    def test_listar_sintomas(self):
        """Testa listagem de todos os sintomas"""
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)  # Verifica quantidade

    def test_criar_sintoma_valido(self):
        """Testa criação de sintoma com dados válidos"""
        data = {
            "nome": "Vômito Agudo",
            "descricao": "Expulsão do conteúdo estomacal de forma súbita.",
        }
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Sintoma.objects.filter(nome="Vômito Agudo").exists())

    def test_filtrar_sintomas_por_nome_exato(self):
        """Testa filtro de sintomas por nome exato"""
        response = self.client.get(self.list_create_url, {"nome": "Febre"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)  # Deve encontrar apenas 1
        self.assertEqual(
            response.data["results"][0]["id"], self.sintoma_febre.id
        )  # Verifica ID


# --- Testes para a API de Consulta ---
class ConsultaAPITests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        # Cria dados relacionados necessários para todos os testes de Consulta
        self.tutor1 = TutorFactory(nome_completo="Carlos Silva TesteAPI")
        self.paciente_rex = PacienteFactory(
            tutor=self.tutor1, nome="Rex TesteAPI", especie="CANINO"
        )
        self.vet1 = VeterinarioFactory(nome_completo="Dr. House TesteAPI")

        # Sintomas e Doenças para testar a sugestão de diagnóstico
        self.sintoma_febre_api = SintomaFactory(nome="Febre API Teste")
        self.sintoma_tosse_api = SintomaFactory(nome="Tosse API Teste")
        self.sintoma_apatia_api = SintomaFactory(nome="Apatia API Teste")

        self.doenca_gripe_api = DoencaFactory(nome="Gripe API Teste")
        self.doenca_gripe_api.sintomas_associados.set(
            [self.sintoma_febre_api, self.sintoma_tosse_api]
        )

        self.doenca_virose_api = DoencaFactory(nome="Virose API Teste")
        self.doenca_virose_api.sintomas_associados.set(
            [self.sintoma_febre_api, self.sintoma_apatia_api]
        )

        self.doenca_nao_relacionada_api = DoencaFactory(nome="Outra Doença API Teste")
        self.doenca_nao_relacionada_api.sintomas_associados.set(
            [SintomaFactory(nome="Coceira API Teste")]
        )

        # URL para listagem e criação
        self.list_create_url = reverse("consulta-list")

    def test_listar_consultas(self):
        """Testa listagem de todas as consultas."""
        # Cria uma consulta com dados específicos do setUp para garantir contexto
        ConsultaFactory(paciente=self.paciente_rex, veterinario_responsavel=self.vet1)

        # Cria uma segunda consulta com dados genéricos da factory
        ConsultaFactory()

        # Faz a requisição GET para listar as consultas
        response = self.client.get(self.list_create_url)

        # Verifica se o status da resposta é 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verifica se a contagem de resultados na resposta da API é 2
        # (assumindo que não há outras consultas no banco de dados antes deste teste
        # ou que o ambiente de teste é limpo para cada método)
        self.assertEqual(response.data["count"], 2)

        # Opcional: Verificar se o número de resultados na lista 'results' também é 2
        if "results" in response.data:
            self.assertEqual(len(response.data["results"]), 2)

    def test_criar_consulta_com_todos_os_campos_texto_anamnese_exame(self):
        """Testa criação de consulta com todos os campos preenchidos e sugestão automática."""
        paciente_novo = PacienteFactory()

        # 1. CRIE OS SINTOMAS
        sint_api_1 = SintomaFactory(nome="Sintoma API 1 para Teste Específico")
        sint_api_2 = SintomaFactory(nome="Sintoma API 2 para Teste Específico")

        # 2. CRIE A DOENÇA ESPERADA E ASSOCIE OS SINTOMAS A ELA *ANTES* DO POST
        doenca_esperada_sugerida = DoencaFactory(
            nome="Doença Alvo para Sintomas API 1 e 2"
        )
        doenca_esperada_sugerida.sintomas_associados.set([sint_api_1, sint_api_2])

        # (Opcional) Você pode criar outra doença não relacionada para garantir que apenas a correta é sugerida
        _ = DoencaFactory(
            nome="Doença Não Relacionada Neste Teste",
            sintomas_associados=[SintomaFactory(nome="Outro Sintoma Avulso")],
        )

        # 3. PREPARE O PAYLOAD
        data = {
            "paciente": paciente_novo.pk,
            "veterinario_responsavel": self.vet1.pk,  # self.vet1 é do setUp da classe
            "data_hora_agendamento": timezone.now().isoformat(),
            "tipo_consulta": "EMERGENCIA",
            "queixa_principal_tutor": "Animal muito quieto e não come (teste de sugestão).",
            "historico_doenca_atual": "Começou ontem à noite, piorou hoje (teste de sugestão).",
            # Mantendo seu valor
            "anamnese_sistema_respiratorio": "Respiração normal (teste completo).",
            "anamnese_sistema_cardiovascular": "Sem histórico de problemas cardíacos.",
            "anamnese_sistema_digestorio": "Recusa alimentar, bebeu pouca água.",
            "examefisico_ouvidos": "Limpos, sem secreção.",
            "temperatura_celsius": "39.1",
            "frequencia_cardiaca_bpm": 120,
            "observacoes_exame_fisico_geral": "Animal apático, mucosas levemente pálidas.",
            # Envia os PKs dos sintomas
            "sintomas_apresentados_ids": [sint_api_1.pk, sint_api_2.pk],
            "diagnosticos_definitivos_ids": [],
            "tratamento_prescrito": "Observação, fluidoterapia se necessário.",
        }

        # 4. EXECUTE A REQUISIÇÃO
        response = self.client.post(self.list_create_url, data, format="json")

        # 5. VERIFIQUE AS RESPOSTAS E O ESTADO DO BANCO
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            f"Falha ao criar consulta: {response.data}",
        )

        nova_consulta = Consulta.objects.get(pk=response.data["id"])

        # Verificar se o campo de texto foi salvo corretamente (se este ainda for um problema)
        self.assertEqual(
            nova_consulta.anamnese_sistema_respiratorio,
            "Respiração normal (teste completo).",
        )

        self.assertEqual(nova_consulta.sintomas_apresentados.count(), 2)

        # VERIFICAR DIAGNÓSTICOS SUSPEITOS GERADOS AUTOMATICAMENTE
        self.assertEqual(
            nova_consulta.diagnosticos_suspeitos.count(),
            1,
            f"Esperava 1 diagnóstico suspeito, obteve {nova_consulta.diagnosticos_suspeitos.count()}. Suspeitos: {list(nova_consulta.diagnosticos_suspeitos.all())}",
        )

        self.assertIn(
            doenca_esperada_sugerida,
            nova_consulta.diagnosticos_suspeitos.all(),
            "A doença esperada não está entre os diagnósticos suspeitos da consulta.",
        )

        # Verificar na resposta da API
        diagnosticos_suspeitos_resp = response.data.get("diagnosticos_suspeitos", [])
        self.assertIsNotNone(
            diagnosticos_suspeitos_resp,
            "O campo 'diagnosticos_suspeitos' não deve ser None na resposta.",
        )
        self.assertEqual(
            len(diagnosticos_suspeitos_resp),
            1,
            "A resposta da API deveria conter 1 diagnóstico suspeito.",
        )

        # Assumindo que seu serializer retorna detalhes da doença, incluindo 'id'
        if (
            diagnosticos_suspeitos_resp
        ):  # Verifica se a lista não está vazia antes de tentar acessar o índice
            ids_sugeridos_resp = [d["id"] for d in diagnosticos_suspeitos_resp]
            self.assertIn(
                doenca_esperada_sugerida.pk,
                ids_sugeridos_resp,
                f"PK da doença esperada ({doenca_esperada_sugerida.pk}) não encontrado nos IDs sugeridos na resposta API: {ids_sugeridos_resp}",
            )
        else:
            self.fail(
                "A lista de diagnosticos_suspeitos_resp está vazia, mas esperava um item."
            )

    def test_decimal_field_validation_consulta(self):
        """Testa validação de campo decimal (temperatura)."""

        # Dados para a requisição. Inclui os campos obrigatórios (FKs)
        # e o campo que queremos testar com um valor inválido.
        data = {
            "paciente": self.paciente_rex.pk,
            "veterinario_responsavel": self.vet1.pk,
            "tipo_consulta": "ROTINA",
            "temperatura_celsius": "MUITO ALTA",  # Valor inválido para um campo DecimalField
        }

        # Envia a requisição POST para o endpoint de criação
        response = self.client.post(self.list_create_url, data, format="json")

        # 1. Verifica se a API retornou o status correto de erro (Bad Request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 2. Verifica se a resposta de erro contém a chave do campo problemático
        self.assertIn("temperatura_celsius", response.data)

        # 3. (Opcional, mas recomendado) Verifica a mensagem de erro específica
        #    Isso torna o teste mais robusto.
        self.assertEqual(
            str(response.data["temperatura_celsius"][0]),
            "Um número válido é necessário.",
        )

    def test_patch_consulta_removendo_todos_sintomas_limpa_diagnosticos_suspeitos_api(
        self,
    ):
        """Testa se PATCH na consulta removendo todos os sintomas limpa diagnosticos_suspeitos."""
        consulta_inicial = ConsultaFactory(
            paciente=self.paciente_rex,
            veterinario_responsavel=self.vet1,
            sintomas_apresentados=[self.sintoma_febre_api, self.sintoma_tosse_api],
        )
        # Inicialmente, deve ter a Gripe como suspeita.

        detail_url = reverse("consulta-detail", kwargs={"pk": consulta_inicial.pk})
        payload_atualizacao = {
            "sintomas_apresentados_ids": []  # Remove todos os sintomas
        }
        response = self.client.patch(detail_url, payload_atualizacao, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        diagnosticos_suspeitos_resp = response.data.get("diagnosticos_suspeitos", [])
        self.assertEqual(
            len(diagnosticos_suspeitos_resp),
            0,
            "Diagnósticos suspeitos deveriam estar vazios.",
        )

        consulta_db = Consulta.objects.get(pk=consulta_inicial.pk)
        self.assertEqual(consulta_db.diagnosticos_suspeitos.count(), 0)


class DiagnosticoSuggestionServiceTests(TestCase):
    """
    Testes unitários para a função de serviço 'sugerir_diagnosticos'.
    Foca na lógica de sugestão baseada nos sintomas e score proporcional.
    """

    def test_sugere_doencas_ordenadas_por_score_proporcional(self):
        """
        Verifica se as doenças são sugeridas e ordenadas corretamente
        com base no score proporcional (sintomas_em_comum / total_sintomas_da_doenca).
        """
        # --- ARRANGE (Preparar o cenário) ---
        sint_febre = SintomaFactory(nome="Febre")
        sint_tosse = SintomaFactory(nome="Tosse")
        sint_apatia = SintomaFactory(nome="Apatia")
        sint_coriza = SintomaFactory(nome="Coriza")

        doenca_A_gripe_comum = DoencaFactory(nome="Gripe Comum")
        doenca_A_gripe_comum.sintomas_associados.set(
            [sint_febre, sint_tosse]
        )  # Score: 2/2 = 1.0 para [F, T]

        doenca_B_gripe_forte = DoencaFactory(nome="Gripe Forte")
        doenca_B_gripe_forte.sintomas_associados.set(
            # Score: 2/3 = ~0.66 para [F, T]
            [sint_febre, sint_tosse, sint_apatia]
        )

        doenca_C_febre_isolada = DoencaFactory(nome="Febre Isolada")
        doenca_C_febre_isolada.sintomas_associados.set(
            [sint_febre]
        )  # Score: 1/1 = 1.0 para [F, T] ou [F]

        DoencaFactory(
            nome="Rinite", sintomas_associados=[sint_coriza]
        )  # Não deve aparecer para [F,T]

        sintomas_paciente_1 = [sint_febre, sint_tosse]

        # --- ACT ---
        sugestoes_1 = sugerir_diagnosticos(sintomas_paciente_1)

        # --- ASSERT ---
        self.assertEqual(len(sugestoes_1), 3)
        # Scores: A=1.0, C=0.5 (1 sintoma em comum de 1 da doença, mas só 1 dos 2 do paciente), B=0.66
        # CORREÇÃO DO SCORE PARA C com [Febre, Tosse]:
        # Doença C (Febre Isolada) sintomas_associados=[sint_febre]
        # sintomas_em_comum com [sint_febre, sint_tosse] é [sint_febre] -> len = 1
        # len(set_sintomas_da_doenca_C) = 1
        # Score C = 1/1 = 1.0

        # Portanto, A (1.0) e C (1.0) têm scores iguais. B (0.66) vem depois.
        # Deve estar entre os 2 primeiros
        self.assertIn(doenca_A_gripe_comum, sugestoes_1[:2])
        # Deve estar entre os 2 primeiros
        self.assertIn(doenca_C_febre_isolada, sugestoes_1[:2])
        self.assertNotEqual(
            sugestoes_1[0],
            sugestoes_1[1],
            "Os dois primeiros devem ser diferentes se houver 2 com score máximo.",
        )
        self.assertEqual(sugestoes_1[2], doenca_B_gripe_forte)

        # Cenário 2: Paciente com apenas Febre
        sintomas_paciente_2 = [sint_febre]
        sugestoes_2 = sugerir_diagnosticos(sintomas_paciente_2)

        # Scores para [Febre]:
        # A (Gripe Comum: F, T): 1/2 = 0.5
        # B (Gripe Forte: F, T, A): 1/3 = ~0.33
        # C (Febre Isolada: F): 1/1 = 1.0
        self.assertEqual(len(sugestoes_2), 3)
        self.assertEqual(sugestoes_2[0], doenca_C_febre_isolada)  # Score 1.0
        self.assertEqual(sugestoes_2[1], doenca_A_gripe_comum)  # Score 0.5
        self.assertEqual(sugestoes_2[2], doenca_B_gripe_forte)  # Score ~0.33

    def test_nenhuma_sugestao_para_sintomas_nao_mapeados(self):
        sint_febre = SintomaFactory(nome="Febre Comum")
        DoencaFactory(nome="Doença Conhecida", sintomas_associados=[sint_febre])
        sint_raro1 = SintomaFactory(nome="Mancha Estelar")
        sint_raro2 = SintomaFactory(nome="Canto Melódico")
        sugestoes = sugerir_diagnosticos([sint_raro1, sint_raro2])
        self.assertEqual(len(sugestoes), 0)

    def test_nenhuma_sugestao_para_lista_vazia_de_sintomas_apresentados(self):
        DoencaFactory(
            nome="Doença Existente",
            sintomas_associados=[SintomaFactory(nome="Sintoma Qualquer")],
        )
        sugestoes = sugerir_diagnosticos([])
        self.assertEqual(len(sugestoes), 0)

    def test_doenca_sem_sintomas_associados_nao_e_sugerida(self):
        sint_febre = SintomaFactory(nome="Febre")
        doenca_fantasma = DoencaFactory(nome="Doença Fantasma")
        doenca_fantasma.sintomas_associados.clear()  # Garante que não tem sintomas

        doenca_real = DoencaFactory(nome="Doença Real")
        doenca_real.sintomas_associados.set([sint_febre])

        sugestoes = sugerir_diagnosticos([sint_febre])
        self.assertEqual(len(sugestoes), 1)
        self.assertEqual(sugestoes[0], doenca_real)
        self.assertNotIn(doenca_fantasma, sugestoes)

    def test_ordem_com_multiplos_sintomas_e_scores_variados(self):
        """Testa ordenação correta quando múltiplas doenças têm scores diferentes"""
        s1 = SintomaFactory(nome="S1")
        s2 = SintomaFactory(nome="S2")
        s3 = SintomaFactory(nome="S3")
        s4 = SintomaFactory(nome="S4")

        d_all = DoencaFactory(nome="D_All")  # S1,S2,S3,S4 -> 4 sintomas
        d_all.sintomas_associados.set([s1, s2, s3, s4])

        d_half = DoencaFactory(nome="D_Half")  # S1,S2 -> 2 sintomas
        d_half.sintomas_associados.set([s1, s2])

        d_quarter = DoencaFactory(nome="D_Quarter")  # S1 -> 1 sintoma
        d_quarter.sintomas_associados.set([s1])

        d_three_quarters = DoencaFactory(
            nome="D_ThreeQuarters"
        )  # S1,S2,S3 -> 3 sintomas
        d_three_quarters.sintomas_associados.set([s1, s2, s3])

        sintomas_paciente = [s1, s2]  # Paciente apresenta S1 e S2

        # Scores esperados para sintomas_paciente = [s1, s2]:
        # d_all (S1,S2,S3,S4): sintomas_em_comum=[s1,s2] (len=2). total_sintomas_doenca=4. Score = 2/4 = 0.5
        # d_half (S1,S2): sintomas_em_comum=[s1,s2] (len=2). total_sintomas_doenca=2. Score = 2/2 = 1.0
        # d_quarter (S1): sintomas_em_comum=[s1] (len=1). total_sintomas_doenca=1. Score = 1/1 = 1.0
        # d_three_quarters (S1,S2,S3): sintomas_em_comum=[s1,s2] (len=2). total_sintomas_doenca=3. Score = 2/3 = ~0.66

        sugestoes = sugerir_diagnosticos(sintomas_paciente)

        self.assertEqual(len(sugestoes), 4)
        # Ordem esperada: D_Half (1.0), D_Quarter (1.0) -> (ordem entre elas pode variar)
        #                D_ThreeQuarters (~0.66)
        #                D_All (0.5)

        self.assertIn(sugestoes[0], [d_half, d_quarter])
        self.assertIn(sugestoes[1], [d_half, d_quarter])
        self.assertNotEqual(
            sugestoes[0],
            sugestoes[1],
            "Os dois primeiros devem ser diferentes pois são duas doenças distintas com score máximo.",
        )
        self.assertEqual(sugestoes[2], d_three_quarters)
        self.assertEqual(sugestoes[3], d_all)


# ==================== TESTES DE INTEGRAÇÃO ====================


class ConsultaIntegrationTests(AuthenticatedAPITestCase):
    """
    Testes de integração para o fluxo completo de consultas.

    Testa a integração entre:
    - Criação de consulta
    - Registro de sintomas
    - Geração automática de sugestões de diagnóstico
    - Atualização de diagnósticos definitivos
    """

    def setUp(self):
        """Configura dados de teste para os testes de integração"""
        super().setUp()

        # Criar dados base
        self.tutor = TutorFactory(nome_completo="João Silva")
        self.paciente = PacienteFactory(nome="Rex", tutor=self.tutor)
        self.veterinario = VeterinarioFactory(nome_completo="Dra. Maria")

        # Criar sintomas
        self.febre = SintomaFactory(nome="Febre")
        self.tosse = SintomaFactory(nome="Tosse")
        self.apatia = SintomaFactory(nome="Apatia")
        self.vomito = SintomaFactory(nome="Vômito")

        # Criar doenças com sintomas associados
        self.cinomose = DoencaFactory(nome="Cinomose")
        self.cinomose.sintomas_associados.set([self.febre, self.tosse, self.apatia])

        self.gastrite = DoencaFactory(nome="Gastrite")
        self.gastrite.sintomas_associados.set([self.vomito, self.apatia])

        self.gripe = DoencaFactory(nome="Gripe Canina")
        self.gripe.sintomas_associados.set([self.febre, self.tosse])

        self.url_list = reverse("consulta-list")

    def test_criar_consulta_com_sintomas_gera_diagnosticos_automaticamente(self):
        """Testa que criar uma consulta com sintomas gera sugestões automáticas"""
        data = {
            "paciente": self.paciente.id,
            "veterinario_responsavel": self.veterinario.id,
            "tipo_consulta": "ROTINA",
            "queixa_principal_tutor": "Animal com febre e tosse",
            "sintomas_apresentados_ids": [self.febre.id, self.tosse.id],
        }

        response = self.client.post(self.url_list, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar que a consulta foi criada
        consulta_id = response.data["id"]
        consulta = Consulta.objects.get(id=consulta_id)

        # Verificar que os sintomas foram associados
        self.assertEqual(consulta.sintomas_apresentados.count(), 2)

        # Verificar que diagnósticos suspeitos foram gerados
        self.assertGreater(consulta.diagnosticos_suspeitos.count(), 0)

        # Verificar que gripe está nas sugestões (febre + tosse = 100% match)
        diagnosticos_ids = list(
            consulta.diagnosticos_suspeitos.values_list("id", flat=True)
        )
        self.assertIn(self.gripe.id, diagnosticos_ids)

    def test_atualizar_sintomas_recalcula_diagnosticos(self):
        """Testa que atualizar sintomas recalcula as sugestões de diagnóstico"""
        # Criar consulta inicial com febre e tosse
        consulta = ConsultaFactory(
            paciente=self.paciente, veterinario_responsavel=self.veterinario
        )
        consulta.sintomas_apresentados.set([self.febre, self.tosse])

        # Verificar estado inicial
        diagnosticos_iniciais = list(consulta.diagnosticos_suspeitos.all())

        # Atualizar para incluir vômito
        url_detail = reverse("consulta-detail", kwargs={"pk": consulta.pk})
        data = {
            "paciente": self.paciente.id,
            "veterinario_responsavel": self.veterinario.id,
            "tipo_consulta": consulta.tipo_consulta,
            "sintomas_apresentados_ids": [self.febre.id, self.tosse.id, self.vomito.id],
        }

        response = self.client.put(url_detail, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Recarregar consulta
        consulta.refresh_from_db()

        # Verificar que sintomas foram atualizados
        self.assertEqual(consulta.sintomas_apresentados.count(), 3)

        # Verificar que diagnósticos foram recalculados
        diagnosticos_atualizados = list(consulta.diagnosticos_suspeitos.all())
        self.assertNotEqual(diagnosticos_iniciais, diagnosticos_atualizados)

    def test_fluxo_completo_diagnostico(self):
        """
        Testa o fluxo completo de diagnóstico:
        1. Criar consulta com sintomas
        2. Sistema sugere diagnósticos
        3. Veterinário confirma diagnóstico definitivo
        """
        # 1. Criar consulta com sintomas de cinomose
        data_create = {
            "paciente": self.paciente.id,
            "veterinario_responsavel": self.veterinario.id,
            "tipo_consulta": "ROTINA",
            "queixa_principal_tutor": "Animal prostrado, com febre e tosse",
            "sintomas_apresentados_ids": [self.febre.id, self.tosse.id, self.apatia.id],
        }

        response_create = self.client.post(self.url_list, data_create, format="json")
        self.assertEqual(response_create.status_code, status.HTTP_201_CREATED)

        consulta_id = response_create.data["id"]
        consulta = Consulta.objects.get(id=consulta_id)

        # 2. Verificar que cinomose foi sugerida (100% match)
        diagnosticos_suspeitos = list(consulta.diagnosticos_suspeitos.all())
        self.assertIn(self.cinomose, diagnosticos_suspeitos)

        # 3. Veterinário confirma o diagnóstico
        url_detail = reverse("consulta-detail", kwargs={"pk": consulta_id})
        data_update = {
            "paciente": self.paciente.id,
            "veterinario_responsavel": self.veterinario.id,
            "tipo_consulta": "ROTINA",
            "sintomas_apresentados_ids": [self.febre.id, self.tosse.id, self.apatia.id],
            "diagnosticos_definitivos_ids": [self.cinomose.id],
            "tratamento_prescrito": "Tratamento de suporte e sintomático",
        }

        response_update = self.client.patch(url_detail, data_update, format="json")
        self.assertEqual(response_update.status_code, status.HTTP_200_OK)

        # Verificar diagnóstico definitivo foi salvo
        consulta.refresh_from_db()
        self.assertEqual(consulta.diagnosticos_definitivos.count(), 1)
        self.assertEqual(consulta.diagnosticos_definitivos.first(), self.cinomose)

    def test_paginacao_lista_consultas(self):
        """Testa que a paginação funciona corretamente na listagem de consultas"""
        # Criar 25 consultas
        for i in range(25):
            ConsultaFactory(
                paciente=self.paciente, veterinario_responsavel=self.veterinario
            )

        # Requisitar primeira página
        response = self.client.get(self.url_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 25)
        # Tamanho padrão da página é 20 (configurado em constants.py)
        self.assertEqual(len(response.data["results"]), 20)

    def test_filtro_por_paciente(self):
        """Testa filtro de consultas por paciente"""
        # Criar outro paciente e consulta
        outro_paciente = PacienteFactory(nome="Buddy", tutor=self.tutor)
        ConsultaFactory(
            paciente=outro_paciente, veterinario_responsavel=self.veterinario
        )

        # Criar consulta para o paciente principal
        ConsultaFactory(
            paciente=self.paciente, veterinario_responsavel=self.veterinario
        )

        # Filtrar por paciente
        response = self.client.get(self.url_list, {"paciente": self.paciente.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["paciente"], self.paciente.id)
