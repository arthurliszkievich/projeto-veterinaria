import logging

from .models import Doenca

# Configurar logger para este módulo
logger = logging.getLogger(__name__)


def sugerir_diagnosticos(sintomas_apresentados_objs):
    """
    Sugere diagnósticos com base nos sintomas apresentados.

    Utiliza um algoritmo de score proporcional que calcula a correspondência
    entre os sintomas apresentados e os sintomas associados a cada doença.

    Args:
        sintomas_apresentados_objs (list): Lista de objetos Sintoma apresentados pelo paciente.

    Returns:
        list: Lista ordenada de objetos Doenca (da maior para menor probabilidade).
              Retorna lista vazia se nenhum sintoma foi fornecido ou nenhuma doença corresponde.

    Exemplo:
        >>> sintomas = [sintoma1, sintoma2, sintoma3]
        >>> diagnosticos = sugerir_diagnosticos(sintomas)
        >>> print([d.nome for d in diagnosticos[:3]])  # Top 3 diagnósticos
    """
    if not sintomas_apresentados_objs:
        logger.info("Nenhum sintoma fornecido para sugestão de diagnóstico")
        return []

    logger.info("=== INICIANDO SUGESTÃO DE DIAGNÓSTICOS ===")
    logger.debug(
        f"Sintomas apresentados: {[s.nome for s in sintomas_apresentados_objs]}"
    )

    suspeitas_com_score = []
    todas_doencas = Doenca.objects.prefetch_related("sintomas_associados").all()
    set_sintomas_apresentados = set(sintomas_apresentados_objs)

    for doenca in todas_doencas:
        set_sintomas_da_doenca = set(doenca.sintomas_associados.all())

        if not set_sintomas_da_doenca:
            continue

        sintomas_em_comum = set_sintomas_apresentados.intersection(
            set_sintomas_da_doenca
        )

        score_proporcional = 0
        if sintomas_em_comum:
            score_proporcional = len(sintomas_em_comum) / len(set_sintomas_da_doenca)

            logger.debug(
                f"Doença: {doenca.nome} | "
                f"Sintomas em comum: {len(sintomas_em_comum)} | "
                f"Total sintomas da doença: {len(set_sintomas_da_doenca)} | "
                f"SCORE: {score_proporcional:.4f}"
            )

            if score_proporcional > 0:
                suspeitas_com_score.append(
                    {
                        "doenca_obj": doenca,
                        "score": score_proporcional,
                        "doenca_nome_debug": doenca.nome,
                    }
                )

    logger.debug(
        f"Total de suspeitas encontradas (antes de ordenar): {len(suspeitas_com_score)}"
    )

    # Ordenar por score (maior para menor)
    suspeitas_ordenadas = sorted(
        suspeitas_com_score, key=lambda x: x["score"], reverse=True
    )

    if suspeitas_ordenadas:
        top_5 = [
            (s["doenca_nome_debug"], f"{s['score']:.2f}")
            for s in suspeitas_ordenadas[:5]
        ]
        logger.info(f"Top 5 suspeitas: {top_5}")
    else:
        logger.info("Nenhuma doença correspondente encontrada")

    return [item["doenca_obj"] for item in suspeitas_ordenadas]
