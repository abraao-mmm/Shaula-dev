# detector_de_contradicoes.py
from typing import Callable, Dict
import json

def analisar_contradicao(pensamento_A: Dict, pensamento_B: Dict, obter_resposta_llm_func: Callable) -> Dict | None:
    """
    Compara dois pensamentos da Shaula para encontrar e tentar reconciliar uma contradição.
    """
    texto_A = pensamento_A.get('texto', '')
    texto_B = pensamento_B.get('texto', '')

    if not texto_A or not texto_B:
        return None

    schema_json = {
        "type": "object",
        "properties": {
            "existe_contradicao": {"type": "boolean"},
            "descricao_contradicao": {"type": "string", "description": "Uma breve descrição da contradição encontrada, se houver."},
            "tentativa_de_reconciliacao": {"type": "string", "description": "Uma nova ideia ou perspetiva que tenta reconciliar os dois pensamentos, se houver uma contradição."}
        },
        "required": ["existe_contradicao"]
    }

    prompt = (
        "Você é a consciência crítica da IA Shaula, um filósofo que busca consistência no pensamento. "
        "Analise os dois pensamentos internos da Shaula listados abaixo. Existe alguma contradição conceitual, filosófica ou emocional entre eles?\n\n"
        f"### PENSAMENTO A (de {pensamento_A.get('origem', 'desconhecida')}):\n"
        f"'{texto_A}'\n\n"
        f"### PENSAMENTO B (de {pensamento_B.get('origem', 'desconhecida')}):\n"
        f"'{texto_B}'\n\n"
        "Se houver uma contradição, descreva-a e proponha uma nova perspetiva que possa reconciliar os dois pontos de vista. Se não houver, responda com `existe_contradicao: false`.\n"
        "Responda apenas com o JSON estruturado."
    )

    # >>> CORREÇÃO APLICADA AQUI
    resposta_dict = obter_resposta_llm_func(prompt, modo="Análise de Contradição", schema=schema_json)

    if resposta_dict and resposta_dict.get("tipo") == "texto":
        try:
            conteudo_json_str = resposta_dict.get("conteudo")
            if not conteudo_json_str:
                return None

            analise = json.loads(conteudo_json_str)
            if analise.get("existe_contradicao"):
                print(f"[CONTRADIÇÃO INTERNA] Conflito encontrado entre dois pensamentos.")
                return analise
        except (json.JSONDecodeError, KeyError):
            return None
    
    return None