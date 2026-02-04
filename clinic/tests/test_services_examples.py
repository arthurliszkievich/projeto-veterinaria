"""
Exemplos de Testes Unitários para a Camada de Serviços

Este módulo demonstra como testar os serviços isoladamente,
sem dependências de Django, banco de dados ou rede.

Execute com: pytest clinic/tests/test_services_examples.py
"""

import unittest
from unittest.mock import Mock, MagicMock, patch

# Importar os serviços
from clinic.services import (
    DiagnosticoService,
    ConsultaService,
    TutorService,
)


class TestDiagnosticoService(unittest.TestCase):
    """
    Testes unitários para DiagnosticoService.
    
    Demonstra como testar lógica de negócio isoladamente,
    usando mocks para simular models do Django.
    """

    def setUp(self):
        """Executado antes de cada teste."""
        self.service = DiagnosticoService()

    def test_sugerir_diagnosticos_retorna_lista_vazia_sem_sintomas(self):
        """
        DADO: Nenhum sintoma fornecido
        QUANDO: Chamar sugerir_diagnosticos
        ENTÃO: Deve retornar lista vazia
        """
        # Arrange
        sintomas = []

        # Act
        resultado = self.service.sugerir_diagnosticos(sintomas)

        # Assert
        self.assertEqual(resultado, [])

    @patch("clinic.services.diagnostico_service.Doenca")
    def test_sugerir_diagnosticos_calcula_scores_corretamente(self, mock_doenca_class):
        """
        DADO: 2 sintomas apresentados e 2 doenças no banco
        QUANDO: Chamar sugerir_diagnosticos
        ENTÃO: Deve calcular scores e ordenar corretamente
        """
        # Arrange - Criar mocks de sintomas
        sintoma_tosse = Mock()
        sintoma_tosse.nome = "Tosse"
        sintoma_tosse.id = 1

        sintoma_febre = Mock()
        sintoma_febre.nome = "Febre"
        sintoma_febre.id = 2

        sintomas_apresentados = [sintoma_tosse, sintoma_febre]

        # Arrange - Criar mock de Doença 1 (100% match)
        doenca1 = Mock()
        doenca1.nome = "Gripe Canina"
        doenca1.sintomas_associados.all.return_value = [sintoma_tosse, sintoma_febre]

        # Arrange - Criar mock de Doença 2 (50% match)
        sintoma_vomito = Mock()
        sintoma_vomito.nome = "Vômito"
        sintoma_vomito.id = 3

        doenca2 = Mock()
        doenca2.nome = "Gastrite"
        doenca2.sintomas_associados.all.return_value = [sintoma_febre, sintoma_vomito]

        # Arrange - Mock do queryset
        mock_queryset = MagicMock()
        mock_queryset.prefetch_related.return_value.all.return_value = [
            doenca1,
            doenca2,
        ]
        mock_doenca_class.objects = mock_queryset

        # Act
        resultado = self.service.sugerir_diagnosticos(sintomas_apresentados)

        # Assert
        self.assertEqual(len(resultado), 2)
        self.assertEqual(resultado[0].nome, "Gripe Canina")  # 100% deve vir primeiro
        self.assertEqual(resultado[1].nome, "Gastrite")  # 50% vem depois

    def test_calcular_score_doenca_retorna_zero_para_doenca_sem_sintomas(self):
        """
        DADO: Uma doença sem sintomas associados
        QUANDO: Calcular score
        ENTÃO: Deve retornar 0.0
        """
        # Arrange
        doenca = Mock()
        doenca.sintomas_associados.all.return_value = []

        sintomas_set = set([Mock(), Mock()])

        # Act
        score = self.service._calcular_score_doenca(doenca, sintomas_set)

        # Assert
        self.assertEqual(score, 0.0)

    def test_calcular_score_doenca_retorna_score_proporcional(self):
        """
        DADO: Doença com 4 sintomas, paciente apresenta 2 deles
        QUANDO: Calcular score
        ENTÃO: Deve retornar 0.5 (2/4)
        """
        # Arrange
        sintoma1 = Mock()
        sintoma1.id = 1
        sintoma2 = Mock()
        sintoma2.id = 2
        sintoma3 = Mock()
        sintoma3.id = 3
        sintoma4 = Mock()
        sintoma4.id = 4

        doenca = Mock()
        doenca.sintomas_associados.all.return_value = [
            sintoma1,
            sintoma2,
            sintoma3,
            sintoma4,
        ]

        sintomas_apresentados_set = {sintoma1, sintoma2}

        # Act
        score = self.service._calcular_score_doenca(doenca, sintomas_apresentados_set)

        # Assert
        self.assertAlmostEqual(score, 0.5, places=2)


class TestConsultaService(unittest.TestCase):
    """
    Testes unitários para ConsultaService.
    
    Demonstra como testar orquestração de serviços com injeção de dependências.
    """

    def setUp(self):
        """Executado antes de cada teste."""
        # Criar mock do DiagnosticoService
        self.mock_diagnostico_service = Mock(spec=DiagnosticoService)

        # Injetar o mock no ConsultaService
        self.service = ConsultaService(
            diagnostico_service=self.mock_diagnostico_service
        )

    def test_processar_diagnosticos_sem_sintomas_limpa_diagnosticos_suspeitos(self):
        """
        DADO: Consulta sem sintomas apresentados
        QUANDO: Processar diagnósticos
        ENTÃO: Deve limpar diagnosticos_suspeitos
        """
        # Arrange
        mock_consulta = Mock()
        mock_consulta.id = 123
        mock_consulta.sintomas_apresentados.all.return_value = []

        # Act
        resultado = self.service.processar_diagnosticos(mock_consulta)

        # Assert
        mock_consulta.diagnosticos_suspeitos.clear.assert_called_once()
        self.assertEqual(resultado, [])

    def test_processar_diagnosticos_com_sintomas_chama_diagnostico_service(self):
        """
        DADO: Consulta com sintomas apresentados
        QUANDO: Processar diagnósticos
        ENTÃO: Deve chamar DiagnosticoService.sugerir_diagnosticos
        """
        # Arrange
        sintoma1 = Mock()
        sintoma1.nome = "Tosse"

        sintoma2 = Mock()
        sintoma2.nome = "Febre"

        mock_consulta = Mock()
        mock_consulta.id = 123
        mock_consulta.sintomas_apresentados.all.return_value = [sintoma1, sintoma2]

        doenca_sugerida = Mock()
        doenca_sugerida.nome = "Gripe"

        self.mock_diagnostico_service.sugerir_diagnosticos.return_value = [
            doenca_sugerida
        ]

        # Act
        resultado = self.service.processar_diagnosticos(mock_consulta)

        # Assert
        self.mock_diagnostico_service.sugerir_diagnosticos.assert_called_once_with(
            [sintoma1, sintoma2]
        )
        mock_consulta.diagnosticos_suspeitos.set.assert_called_once_with(
            [doenca_sugerida]
        )
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].nome, "Gripe")

    def test_processar_diagnosticos_anexa_lista_ordenada_na_instancia(self):
        """
        DADO: Diagnósticos calculados
        QUANDO: Processar diagnósticos
        ENTÃO: Deve anexar atributo _diagnosticos_sugeridos_ordenados
        """
        # Arrange
        mock_consulta = Mock()
        mock_consulta.id = 123
        mock_consulta.sintomas_apresentados.all.return_value = [Mock()]

        doenca1 = Mock()
        doenca1.nome = "Doenca A"
        doenca2 = Mock()
        doenca2.nome = "Doenca B"

        self.mock_diagnostico_service.sugerir_diagnosticos.return_value = [
            doenca1,
            doenca2,
        ]

        # Act
        self.service.processar_diagnosticos(mock_consulta)

        # Assert
        self.assertTrue(
            hasattr(mock_consulta, "_diagnosticos_sugeridos_ordenados")
        )
        diagnosticos_anexados = mock_consulta._diagnosticos_sugeridos_ordenados
        self.assertEqual(len(diagnosticos_anexados), 2)


class TestTutorService(unittest.TestCase):
    """
    Testes unitários para TutorService.
    
    Demonstra como testar validações de negócio isoladamente.
    """

    def setUp(self):
        """Executado antes de cada teste."""
        self.service = TutorService()

    def test_limpar_cpf_remove_pontuacao(self):
        """
        DADO: CPF com formatação
        QUANDO: Limpar CPF
        ENTÃO: Deve remover pontos e traços
        """
        # Arrange
        cpf_formatado = "123.456.789-00"

        # Act
        cpf_limpo = self.service._limpar_cpf(cpf_formatado)

        # Assert
        self.assertEqual(cpf_limpo, "12345678900")

    def test_limpar_cpf_remove_espacos(self):
        """
        DADO: CPF com espaços
        QUANDO: Limpar CPF
        ENTÃO: Deve remover espaços
        """
        # Arrange
        cpf_com_espacos = " 123.456.789-00 "

        # Act
        cpf_limpo = self.service._limpar_cpf(cpf_com_espacos)

        # Assert
        self.assertEqual(cpf_limpo, "12345678900")

    @patch.object(TutorService, "_validar_cpf")
    @patch.object(TutorService, "_formatar_cpf")
    def test_validar_e_formatar_cpf_valido_retorna_true_e_formatado(
        self, mock_formatar, mock_validar
    ):
        """
        DADO: CPF válido
        QUANDO: Validar e formatar
        ENTÃO: Deve retornar (True, cpf_formatado)
        """
        # Arrange
        mock_validar.return_value = True
        mock_formatar.return_value = "123.456.789-00"

        # Act
        is_valid, cpf_formatado = self.service.validar_e_formatar_cpf("12345678900")

        # Assert
        self.assertTrue(is_valid)
        self.assertEqual(cpf_formatado, "123.456.789-00")
        mock_validar.assert_called_once()
        mock_formatar.assert_called_once()

    @patch.object(TutorService, "_validar_cpf")
    def test_validar_e_formatar_cpf_invalido_retorna_false_e_vazio(
        self, mock_validar
    ):
        """
        DADO: CPF inválido
        QUANDO: Validar e formatar
        ENTÃO: Deve retornar (False, "")
        """
        # Arrange
        mock_validar.return_value = False

        # Act
        is_valid, cpf_formatado = self.service.validar_e_formatar_cpf("00000000000")

        # Assert
        self.assertFalse(is_valid)
        self.assertEqual(cpf_formatado, "")

    def test_validar_cpf_metodo_de_conveniencia(self):
        """
        DADO: CPF para validar
        QUANDO: Chamar validar_cpf (sem formatação)
        ENTÃO: Deve retornar apenas boolean
        """
        # Arrange & Act
        # Nota: Este teste vai falhar se o CPF não for válido de verdade
        # Para testes unitários puros, deveria mockar o validate_docbr
        resultado = self.service.validar_cpf("123.456.789-00")

        # Assert
        self.assertIsInstance(resultado, bool)


# ============================================================================
# EXEMPLOS DE TESTES DE INTEGRAÇÃO
# ============================================================================


class TestConsultaServiceIntegration(unittest.TestCase):
    """
    EXEMPLO de teste de integração (não unitário).
    
    Testa ConsultaService com DiagnosticoService REAL,
    mas ainda mockando o banco de dados.
    """

    def setUp(self):
        """Setup com serviço real (não mock)."""
        self.service = ConsultaService()  # DiagnosticoService real

    @patch("clinic.services.diagnostico_service.Doenca")
    def test_processar_diagnosticos_integracao_completa(self, mock_doenca_class):
        """
        Teste de integração entre ConsultaService e DiagnosticoService.
        
        DADO: Consulta com sintomas
        QUANDO: Processar diagnósticos (usando serviços reais)
        ENTÃO: Deve calcular e salvar diagnósticos corretamente
        """
        # Arrange - Sintomas
        sintoma_tosse = Mock()
        sintoma_tosse.nome = "Tosse"
        sintoma_tosse.id = 1

        sintoma_febre = Mock()
        sintoma_febre.nome = "Febre"
        sintoma_febre.id = 2

        # Arrange - Doença
        doenca_gripe = Mock()
        doenca_gripe.nome = "Gripe Canina"
        doenca_gripe.sintomas_associados.all.return_value = [
            sintoma_tosse,
            sintoma_febre,
        ]

        # Arrange - Mock do banco
        mock_queryset = MagicMock()
        mock_queryset.prefetch_related.return_value.all.return_value = [doenca_gripe]
        mock_doenca_class.objects = mock_queryset

        # Arrange - Consulta
        mock_consulta = Mock()
        mock_consulta.id = 999
        mock_consulta.sintomas_apresentados.all.return_value = [
            sintoma_tosse,
            sintoma_febre,
        ]

        # Act
        diagnosticos = self.service.processar_diagnosticos(mock_consulta)

        # Assert
        self.assertEqual(len(diagnosticos), 1)
        self.assertEqual(diagnosticos[0].nome, "Gripe Canina")
        mock_consulta.diagnosticos_suspeitos.set.assert_called_once()


# ============================================================================
# COMO EXECUTAR ESTES TESTES
# ============================================================================

if __name__ == "__main__":
    """
    Execute com:
    
        python -m pytest clinic/tests/test_services_examples.py -v
    
    Ou:
    
        python clinic/tests/test_services_examples.py
    
    Para cobertura:
    
        pytest --cov=clinic.services clinic/tests/test_services_examples.py
    """
    unittest.main()
