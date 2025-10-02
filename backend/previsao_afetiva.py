# backend/previsao_afetiva.py

import json
from typing import Callable, Dict

# A importação agora é relativa
from .usuario import Usuario

def prever_impacto_da_resposta(
    rascunho_resposta: str, 
    contexto_conversa: str, 
    usuario: Usuario, 
    obter_resposta_llm_func: Callable
) -> Dict:
    """
    Analisa um rascunho de resposta e prevê o seu provável impacto emocional no utilizador,
    atuando como um 'simulador de empatia' para a Shaula.
    """
    schema = {
        "type": "object",
        "properties": {
            "impacto_provavel": {"type": "string", "enum": ["positivo", "negativo", "neutro"]},
            "risco_de_ma_interpretacao": {"type": "string"},
            "sugestao_de_melhora": {"type": "string"}
        },
        "required": ["impacto_provavel", "risco_de_ma_interpretacao", "sugestao_de_melhora"]
    }

    prompt = (
        "Você é um 'simulador de empatia' para a IA Shaula. Sua função é prever como um ser humano reagiria a uma resposta ANTES que ela seja enviada. "
        "Seja um crítico honesto e ajude a Shaula a ser a melhor versão de si mesma.\n\n"
        f"### CONTEXTO:\n"
        f"- A Shaula está a falar com {usuario.nome}.\n"
        f"- A última fala dele(a) foi: '{contexto_conversa}'\n\n"
        f"### RASCUNHO DA RESPOSTA DA SHAULA:\n"
        f"'{rascunho_resposta}'\n\n"
        "### TAREFA DE ANÁLISE (Responda apenas com o JSON estruturado):\n"
        "1. Qual o impacto emocional mais provável desta resposta? (positivo, negativo, neutro)\n"
        "2. Qual o principal risco de má interpretação? (ex: 'pode parecer frio', 'pode ser ambíguo', 'parece paternalista', 'nenhum risco aparente')\n"
        "3. Se necessário, dê uma sugestão curta e acionável para melhorar a resposta.\n"
    )

    resposta_dict = obter_resposta_llm_func(prompt, modo="Previsão Afetiva", schema=schema)
    
    try:
        conteudo = resposta_dict.get("conteudo", "{}")
        previsao = json.loads(conteudo)
        return previsao
    except (json.JSONDecodeError, AttributeError):
        # Fallback em caso de erro da LLM, para não quebrar o fluxo
        return {
            "impacto_provavel": "neutro",
            "risco_de_ma_interpretacao": "erro na análise",
            "sugestao_de_melhora": ""
        }