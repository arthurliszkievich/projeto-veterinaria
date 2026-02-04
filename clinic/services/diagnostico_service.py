"""
Serviço de Diagnóstico

Responsável pela lógica de sugestão de diagnósticos baseada em sintomas.
Implementa algoritmos de correspondência e scoring entre sintomas e doenças.

Princípios aplicados:
- SRP: Apenas responsável por cálculos de diagnóstico
- Open/Closed: Permite extensão através de strategies sem modificação
"""

import logging
from typing import List

from ..models import Doenca, Sintoma

logger = logging.getLogger(__name__)


class DiagnosticoService:
    """
    Serviço para sugestão de diagnósticos baseados em sintomas.

    Este serviço encapsula toda a lógica de análise de sintomas e
    correspondência com doenças, utilizando um algoritmo de score proporcional.

    Attributes:
        Nenhum atributo de instância (stateless por design)

    Example:
        >>> service = DiagnosticoService()
        >>> sintomas = Sintoma.objects.filter(id__in=[1, 2, 3])
        >>> diagnosticos = service.sugerir_diagnosticos(sintomas)
        >>> print([d.nome for d in diagnosticos[:3]])
    """

    def sugerir_diagnosticos(
        self, sintomas_apresentados: List[Sintoma]
    ) -> List[Doenca]:
        """
        Sugere diagnósticos com base nos sintomas apresentados.

        Utiliza um algoritmo de score proporcional que calcula a correspondência
        entre os sintomas apresentados e os sintomas associados a cada doença.

        O score é calculado como:
            score = sintomas_em_comum / total_sintomas_da_doenca

        Args:
            sintomas_apresentados: Lista de objetos Sintoma do paciente

        Returns:
            Lista ordenada de objetos Doenca (maior para menor probabilidade)
            Lista vazia se nenhum sintoma fornecido ou nenhuma correspondência

        Raises:
            TypeError: Se sintomas_apresentados não for uma lista/queryset
        """
        if not sintomas_apresentados:
            logger.info("Nenhum sintoma fornecido para sugestão de diagnóstico")
            return []

        logger.info("=== INICIANDO SUGESTÃO DE DIAGNÓSTICOS ===")
        logger.debug(
            f"Sintomas apresentados: {[s.nome for s in sintomas_apresentados]}"
        )

        suspeitas = self._calcular_scores(sintomas_apresentados)
        diagnosticos_ordenados = self._ordenar_por_score(suspeitas)

        self._log_resultados(diagnosticos_ordenados)

        return diagnosticos_ordenados

    def _calcular_scores(
        self, sintomas_apresentados: List[Sintoma]
    ) -> List[dict]:
        """
        Calcula scores de correspondência para todas as doenças.

        Args:
            sintomas_apresentados: Lista de sintomas do paciente

        Returns:
            Lista de dicionários com estrutura:
            {
                'doenca_obj': Doenca,
                'score': float,
                'doenca_nome_debug': str
            }
        """
        suspeitas_com_score = []
        todas_doencas = Doenca.objects.prefetch_related("sintomas_associados").all()
        set_sintomas_apresentados = set(sintomas_apresentados)

        for doenca in todas_doencas:
            score = self._calcular_score_doenca(
                doenca, set_sintomas_apresentados
            )

            if score > 0:
                suspeitas_com_score.append(
                    {
                        "doenca_obj": doenca,
                        "score": score,
                        "doenca_nome_debug": doenca.nome,
                    }
                )

        logger.debug(
            f"Total de suspeitas encontradas: {len(suspeitas_com_score)}"
        )

        return suspeitas_com_score

    def _calcular_score_doenca(
        self, doenca: Doenca, sintomas_apresentados_set: set
    ) -> float:
        """
        Calcula o score de correspondência para uma doença específica.

        Utiliza uma fórmula balanceada que considera:
        1. Cobertura: % dos sintomas da doença que o paciente apresenta
        2. Precisão: % dos sintomas do paciente que estão na doença
        3. Quantidade: número absoluto de sintomas em comum (desempate)

        Args:
            doenca: Objeto Doenca a ser analisado
            sintomas_apresentados_set: Set de sintomas apresentados

        Returns:
            Score composto (0.0 a 100.0+) indicando probabilidade
        """
        sintomas_da_doenca = set(doenca.sintomas_associados.all())

        if not sintomas_da_doenca:
            return 0.0

        sintomas_em_comum = sintomas_apresentados_set.intersection(
            sintomas_da_doenca
        )

        if not sintomas_em_comum:
            return 0.0

        # Cobertura: % dos sintomas da doença que o paciente tem
        cobertura = len(sintomas_em_comum) / len(sintomas_da_doenca)
        
        # Precisão: % dos sintomas do paciente que pertencem à doença
        precisao = len(sintomas_em_comum) / len(sintomas_apresentados_set)
        
        # Score balanceado usando média harmônica (F1-Score)
        # Prioriza casos onde ambos cobertura e precisão são altos
        if cobertura + precisao == 0:
            score = 0.0
        else:
            f1_score = 2 * (cobertura * precisao) / (cobertura + precisao)
            # Multiplica por 100 para ter valores mais legíveis
            # Adiciona um pequeno bônus pela quantidade absoluta de sintomas
            score = (f1_score * 100) + (len(sintomas_em_comum) * 0.1)

        logger.debug(
            f"Doença: {doenca.nome} | "
            f"Sintomas em comum: {len(sintomas_em_comum)} | "
            f"Cobertura: {cobertura:.2f} | "
            f"Precisão: {precisao:.2f} | "
            f"SCORE: {score:.2f}"
        )

        return score

    def _ordenar_por_score(self, suspeitas: List[dict]) -> List[Doenca]:
        """
        Ordena as suspeitas por score (maior para menor) e anexa o score a cada doença.

        Args:
            suspeitas: Lista de dicionários com scores calculados

        Returns:
            Lista ordenada de objetos Doenca (com atributo _score anexado)
        """
        suspeitas_ordenadas = sorted(
            suspeitas, key=lambda x: x["score"], reverse=True
        )

        # Anexa o score como atributo temporário em cada doença
        doencas_com_score = []
        for item in suspeitas_ordenadas:
            doenca = item["doenca_obj"]
            setattr(doenca, "_score", item["score"])
            doencas_com_score.append(doenca)

        return doencas_com_score

    def _log_resultados(self, diagnosticos: List[Doenca]) -> None:
        """
        Registra os resultados do diagnóstico no log.

        Args:
            diagnosticos: Lista ordenada de doenças sugeridas
        """
        if diagnosticos:
            # Nota: Precisaríamos manter os scores para este log,
            # mas por simplicidade vamos apenas logar os nomes
            top_5_nomes = [d.nome for d in diagnosticos[:5]]
            logger.info(f"Top 5 suspeitas: {top_5_nomes}")
        else:
            logger.info("Nenhuma doença correspondente encontrada")
