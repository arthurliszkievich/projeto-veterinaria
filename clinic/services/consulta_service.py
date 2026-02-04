"""
Serviço de Consulta

Responsável pela orquestração de operações relacionadas a consultas veterinárias.
Coordena a criação, atualização e processamento de diagnósticos.

Princípios aplicados:
- SRP: Apenas responsável pela lógica de consultas
- DIP: Depende de abstrações (pode receber DiagnosticoService via injeção)
"""

import logging
from typing import List, Optional

from ..models import Consulta, Doenca, Sintoma

logger = logging.getLogger(__name__)


class ConsultaService:
    """
    Serviço para gerenciar operações de consultas veterinárias.

    Este serviço encapsula toda a lógica de negócio relacionada a consultas,
    incluindo processamento de diagnósticos automáticos baseados em sintomas.

    Attributes:
        diagnostico_service: Serviço responsável por cálculos de diagnóstico

    Example:
        >>> from clinic.services import ConsultaService, DiagnosticoService
        >>> consulta_service = ConsultaService()
        >>> consulta_service.processar_diagnosticos(consulta)
    """

    def __init__(self, diagnostico_service=None):
        """
        Inicializa o serviço de consulta.

        Args:
            diagnostico_service: Instância de DiagnosticoService (opcional).
                               Se None, cria uma nova instância automaticamente.
        """
        from .diagnostico_service import DiagnosticoService

        self.diagnostico_service = (
            diagnostico_service or DiagnosticoService()
        )

    def processar_diagnosticos(self, consulta: Consulta) -> List[Doenca]:
        """
        Processa e atualiza os diagnósticos suspeitos de uma consulta.

        Este método:
        1. Obtém os sintomas apresentados na consulta
        2. Calcula diagnósticos sugeridos usando o serviço de diagnóstico
        3. Atualiza o relacionamento diagnosticos_suspeitos da consulta
        4. Anexa a lista ordenada à instância para uso no serializer

        Args:
            consulta: Instância de Consulta a processar

        Returns:
            Lista ordenada de Doenca sugeridas (por score decrescente)

        Side Effects:
            - Atualiza consulta.diagnosticos_suspeitos no banco de dados
            - Anexa atributo _diagnosticos_sugeridos_ordenados à instância

        Example:
            >>> service = ConsultaService()
            >>> diagnosticos = service.processar_diagnosticos(consulta)
            >>> print([d.nome for d in diagnosticos])
        """
        logger.info(
            f"Processando diagnósticos para consulta ID: {consulta.id}"
        )

        # Obtém sintomas apresentados
        sintomas_apresentados = list(consulta.sintomas_apresentados.all())

        # Calcula diagnósticos
        doencas_sugeridas = self._calcular_diagnosticos_sugeridos(
            sintomas_apresentados
        )

        # Atualiza relacionamento no banco
        self._atualizar_diagnosticos_suspeitos(consulta, doencas_sugeridas)

        # Anexa lista ordenada à instância para o Serializer
        self._anexar_diagnosticos_ordenados(consulta, doencas_sugeridas)

        logger.info(
            f"Processamento concluído: {len(doencas_sugeridas)} diagnósticos sugeridos"
        )

        return doencas_sugeridas

    def criar_consulta_com_diagnosticos(
        self, consulta: Consulta, sintomas_ids: Optional[List[int]] = None
    ) -> Consulta:
        """
        Cria uma nova consulta e processa seus diagnósticos.

        Método de conveniência que encapsula a criação e processamento
        de diagnósticos em uma única operação.

        Args:
            consulta: Instância de Consulta (já salva no banco)
            sintomas_ids: Lista de IDs de sintomas a associar (opcional)

        Returns:
            Instância de Consulta atualizada com diagnósticos processados

        Example:
            >>> consulta = Consulta(paciente=paciente, ...)
            >>> consulta.save()
            >>> service.criar_consulta_com_diagnosticos(consulta, [1, 2, 3])
        """
        if sintomas_ids:
            consulta.sintomas_apresentados.set(sintomas_ids)

        self.processar_diagnosticos(consulta)

        logger.info(f"Nova consulta criada com ID: {consulta.id}")
        return consulta

    def atualizar_consulta_com_diagnosticos(self, consulta: Consulta) -> Consulta:
        """
        Atualiza uma consulta existente e recalcula seus diagnósticos.

        Args:
            consulta: Instância de Consulta (já atualizada no banco)

        Returns:
            Instância de Consulta com diagnósticos reprocessados

        Example:
            >>> consulta.queixa_principal_tutor = "Nova queixa"
            >>> consulta.save()
            >>> service.atualizar_consulta_com_diagnosticos(consulta)
        """
        self.processar_diagnosticos(consulta)

        logger.info(f"Consulta ID {consulta.id} atualizada")
        return consulta

    def _calcular_diagnosticos_sugeridos(
        self, sintomas: List[Sintoma]
    ) -> List[Doenca]:
        """
        Calcula diagnósticos usando o serviço de diagnóstico.

        Args:
            sintomas: Lista de objetos Sintoma

        Returns:
            Lista ordenada de Doenca sugeridas
        """
        if not sintomas:
            logger.debug("Nenhum sintoma apresentado")
            return []

        doencas_sugeridas = self.diagnostico_service.sugerir_diagnosticos(
            sintomas
        )

        logger.debug(
            f"DiagnosticoService retornou {len(doencas_sugeridas)} sugestões"
        )

        return doencas_sugeridas

    def _atualizar_diagnosticos_suspeitos(
        self, consulta: Consulta, doencas: List[Doenca]
    ) -> None:
        """
        Atualiza o relacionamento ManyToMany de diagnósticos suspeitos.

        Args:
            consulta: Instância de Consulta
            doencas: Lista de Doenca a associar
        """
        if doencas:
            consulta.diagnosticos_suspeitos.set(doencas)
            logger.debug(
                f"Salvos {len(doencas)} diagnósticos suspeitos no banco"
            )
        else:
            consulta.diagnosticos_suspeitos.clear()
            logger.debug("Diagnósticos suspeitos limpos (nenhum encontrado)")

    def _anexar_diagnosticos_ordenados(
        self, consulta: Consulta, doencas: List[Doenca]
    ) -> None:
        """
        Anexa lista ordenada de diagnósticos à instância da consulta.

        Este atributo temporário é usado pelo SerializerMethodField
        para garantir que a ordem por score seja preservada na resposta da API.

        Args:
            consulta: Instância de Consulta
            doencas: Lista ordenada de Doenca (com scores anexados)
        """
        setattr(consulta, "_diagnosticos_sugeridos_ordenados", doencas)
        logger.debug("Lista ordenada anexada à instância da consulta")
