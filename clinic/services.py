from .models import Doenca


def sugerir_diagnosticos(sintomas_apresentados_objs):
    if not sintomas_apresentados_objs:
        return []

    print(f"\n--- INICIANDO SUGESTÃO ---")
    print(
        f"Sintomas Apresentados (formulário): {[s.nome for s in sintomas_apresentados_objs]}")

    suspeitas_com_score = []
    todas_doencas = Doenca.objects.prefetch_related(
        'sintomas_associados').all()
    set_sintomas_apresentados = set(sintomas_apresentados_objs)

    for doenca in todas_doencas:
        set_sintomas_da_doenca = set(doenca.sintomas_associados.all())

        if not set_sintomas_da_doenca:
            continue

        sintomas_em_comum = set_sintomas_apresentados.intersection(
            set_sintomas_da_doenca)

        score_proporcional = 0
        if sintomas_em_comum:
            score_proporcional = len(sintomas_em_comum) / \
                len(set_sintomas_da_doenca)

            # DEBUG PRINT PARA CADA DOENÇA COM SCORE > 0
            print(f"  Doença: {doenca.nome} | Sint. Comum: {len(sintomas_em_comum)} | Total Sint. Doença: {len(set_sintomas_da_doenca)} | SCORE: {score_proporcional:.4f}")

            if score_proporcional > 0:
                suspeitas_com_score.append(
                    {'doenca_obj': doenca, 'score': score_proporcional,
                        'doenca_nome_debug': doenca.nome}  # Adicionado nome para debug
                )

    print(
        f"\n--- SUSPEITAS ANTES DE ORDENAR ({len(suspeitas_com_score)} itens) ---")
    for item in suspeitas_com_score:
        print(
            f"  Nome: {item['doenca_nome_debug']}, Score: {item['score']:.4f}")

    suspeitas_ordenadas = sorted(
        suspeitas_com_score, key=lambda x: x['score'], reverse=True
    )

    print(
        f"\n--- SUSPEITAS DEPOIS DE ORDENAR ({len(suspeitas_ordenadas)} itens) ---")
    for item in suspeitas_ordenadas:
        print(
            f"  Nome: {item['doenca_nome_debug']}, Score: {item['score']:.4f}")

    return [item['doenca_obj'] for item in suspeitas_ordenadas]
