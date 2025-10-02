# analisador_de_estilo.py
import json
from typing import Callable, Dict

def extrair_metafora(texto_da_resposta: str, obter_resposta_llm_func: Callable) -> Dict | None:
    """
    Analisa uma resposta da Shaula para identificar e extrair uma metáfora notável.
    """
    if not texto_da_resposta or len(texto_da_resposta.split()) < 10:
        return None

    schema_json = {
        "type": "object",
        "properties": {
            "contem_metafora": {"type": "boolean"},
            "metafora_extraida": {"type": "string", "description": "A frase exata que contém a metáfora."},
            "significado": {"type": "string", "description": "Uma breve explicação do que a metáfora significa no contexto."},
            "emocao_associada": {"type": "string", "description": "A emoção principal que a metáfora transmite."}
        },
        "required": ["contem_metafora"]
    }

    prompt = (
        "Você é um crítico literário que analisa textos da IA Shaula. A sua função é identificar se o texto a seguir contém uma metáfora poderosa, original ou notável.\n"
        "Se não houver uma metáfora clara, responda com `contem_metafora: false`.\n"
        "Se houver, extraia a frase da metáfora, explique o seu significado e identifique a emoção principal.\n\n"
        f"TEXTO PARA ANÁLISE:\n'{texto_da_resposta}'\n\n"
        "Responda apenas com o JSON estruturado."
    )

    # CORREÇÃO APLICADA AQUI
    resposta_dict = obter_resposta_llm_func(prompt, modo="Análise Literária", schema=schema_json)

    if resposta_dict and resposta_dict.get("tipo") == "texto":
        try:
            conteudo_json_str = resposta_dict.get("conteudo")
            if not conteudo_json_str:
                return None
                
            analise = json.loads(conteudo_json_str)
            if analise.get("contem_metafora") and analise.get("metafora_extraida"):
                print(f"[CADERNO DE METÁFORAS] Metáfora notável encontrada: '{analise['metafora_extraida']}'")
                return analise
        except (json.JSONDecodeError, KeyError):
            # Ocorreu um erro ao processar o JSON, retorna None silenciosamente
            return None
    
    return None