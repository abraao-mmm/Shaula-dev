# backend/analisador_de_intencao.py (VERSÃO 2.0 - COM FEW-SHOT LEARNING)

import json
from typing import Callable, Dict

def identificar_intencao(entrada_usuario: str, obter_resposta_llm_func: Callable) -> Dict:
    """
    Usa uma chamada à LLM com exemplos (Few-Shot) para classificar a intenção
    do utilizador de forma muito mais precisa.
    """
    schema = {
        "type": "object",
        "properties": {
            "intencao": { "type": "string", "enum": ["analise_de_dados", "conversa_geral", "comando_sistema", "pergunta_pessoal"] },
            "dataset_mencionado": { "type": "string" },
            "comando_especifico": { "type": "string" }
        },
        "required": ["intencao"]
    }

    prompt = (
        "Você é um classificador de intenções NLU (Natural Language Understanding) de alta precisão. Analise a frase do utilizador e classifique-a de acordo com o schema JSON fornecido, baseando-se nos exemplos abaixo.\n\n"
        "**Exemplo 1: Análise de Dados**\n"
        "Frase: 'shaula, analisa o dataset olist que eu coloquei na sua DATA'\n"
        "JSON: {\"intencao\": \"analise_de_dados\", \"dataset_mencionado\": \"olist\"}\n\n"
        "**Exemplo 2: Análise de Dados**\n"
        "Frase: 'podes verificar uns ficheiros pra mim?'\n"
        "JSON: {\"intencao\": \"analise_de_dados\", \"dataset_mencionado\": null}\n\n"
        "**Exemplo 3: Comando do Sistema**\n"
        "Frase: 'refletir'\n"
        "JSON: {\"intencao\": \"comando_sistema\", \"comando_especifico\": \"refletir\"}\n\n"
        "**Exemplo 4: Conversa Geral**\n"
        "Frase: 'o que é a consciência?'\n"
        "JSON: {\"intencao\": \"conversa_geral\"}\n\n"
        "--- TAREFA ATUAL ---\n"
        f"**Frase do Utilizador para Analisar:**\n\"{entrada_usuario}\"\n\n"
        "Responda APENAS com o objeto JSON."
    )
    
    resposta_dict = obter_resposta_llm_func(prompt, modo="Análise de Intenção", schema=schema)
    
    try:
        return json.loads(resposta_dict.get("conteudo", "{}"))
    except json.JSONDecodeError:
        return {"intencao": "conversa_geral"} # Fallback seguro