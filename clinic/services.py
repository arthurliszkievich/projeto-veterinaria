from .models import Doenca


def sugerir_diagnosticos(sintomas_apresentados_objs):
    """
    Sugere diagnósticos (Doencas) com base em uma lista de Sintomas apresentados.
    Retorna uma lista de objetos Doenca, ordenados por relevância (score de proporção).
    """

    if not sintomas_apresentados_objs:
        return []

    suspeitas_com_score = []
    # Otimiza a busca, trazendo os sintomas associados de todas as doenças de uma vez
    todas_doencas = Doenca.objects.prefetch_related(
        'sintomas_associados').all()

    # PASSO 1: Converter a lista/queryset de sintomas apresentados para um conjunto
    set_sintomas_apresentados = set(sintomas_apresentados_objs)

    for doenca in todas_doencas:
        # Pega os sintomas associados a esta doença específica
        # .all() é necessário aqui porque 'sintomas_associados' é um RelatedManager
        set_sintomas_da_doenca = set(doenca.sintomas_associados.all())

        # Encontra quais sintomas da doença estão presentes nos sintomas apresentados
        # Corrigido para usar set_sintomas_apresentados
        sintomas_em_comum = set_sintomas_apresentados.intersection(
            set_sintomas_da_doenca)

        if sintomas_em_comum:  # Apenas considera doenças com pelo menos um sintoma em comum

            score_proporcional = 0
            if len(set_sintomas_da_doenca) > 0:
                # Calcula a proporção de sintomas DA DOENÇA que foram encontrados
                score_proporcional = len(
                    sintomas_em_comum) / len(set_sintomas_da_doenca)
            # Se len(set_sintomas_da_doenca) == 0, score_proporcional permanece 0, o que é razoável.

            # PASSO 2: Adicionar à lista de suspeitas se o score for significativo
            # Um score de 0 não é útil, então só adicionamos se for maior que 0.
            if score_proporcional > 0:
                suspeitas_com_score.append(
                    {'doenca': doenca, 'score': score_proporcional})

    # PASSO 3: Ordenar as suspeitas pelo score, do maior para o menor
    suspeitas_ordenadas = sorted(
        suspeitas_com_score, key=lambda x: x['score'], reverse=True)

    # PASSO 4: Retornar apenas a lista de objetos Doenca ordenados
    return [item['doenca'] for item in suspeitas_ordenadas]
