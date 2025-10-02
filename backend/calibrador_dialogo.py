# calibrador_dialogo.py
import json
from typing import Callable, Dict

def analisar_equilibrio_conversacional(
    fala_usuario: str, 
    resposta_shaula: str, 
    obter_resposta_llm_func: Callable
) -> Dict | None:
    """
    Analisa os dois últimos turnos de uma conversa para avaliar o equilíbrio,
    a relevância e a complexidade da resposta da Shaula.
    """
    if not fala_usuario or not resposta_shaula:
        return None

    # Cálculo simples de proporção para dar um dado quantitativo à LLM
    ratio_fala = round(len(resposta_shaula) / len(fala_usuario), 1) if len(fala_usuario) > 0 else 10.0

    schema_json = {
        "type": "object",
        "properties": {
            "relevancia_resposta": {"type": "string", "enum": ["direta", "indireta", "desconectada"], "description": "A resposta da Shaula aborda diretamente o ponto do usuário?"},
            "excesso_verbosidade": {"type": "boolean", "description": "True se a resposta da Shaula foi excessivamente longa ou verborrágica para o contexto."},
            "complexidade_linguagem": {"type": "string", "enum": ["simples", "moderada", "alta"], "description": "O nível de complexidade da linguagem usada pela Shaula."},
            "feedback_implicito_usuario": {"type": "string", "description": "Qual o feedback implícito na fala do usuário? (ex: 'confusão', 'interesse', 'pressa', 'nenhum')"}
        },
        "required": ["relevancia_resposta", "excesso_verbosidade", "complexidade_linguagem", "feedback_implicito_usuario"]
    }

    prompt = (
        "Você é um especialista em análise do discurso e pragmática da comunicação. A sua função é analisar a qualidade de uma resposta de uma IA (Shaula) a um humano.\n"
        "Seja crítico e objetivo.\n\n"
        f"### CONTEXTO DA CONVERSA:\n"
        f"- O Humano disse: '{fala_usuario}'\n"
        f"- A Shaula respondeu: '{resposta_shaula}'\n"
        f"- (Análise Quantitativa: A resposta da Shaula foi {ratio_fala} vezes maior que a fala do humano.)\n\n"
        "### TAREFA DE ANÁLISE:\n"
        "Com base no contexto, avalie a resposta da Shaula de acordo com o esquema JSON fornecido. Responda apenas com o JSON estruturado."
    )

    resposta_dict = obter_resposta_llm_func(prompt, modo="Análise Conversacional", schema=schema_json)

    if resposta_dict and resposta_dict.get("tipo") == "texto":
        try:
            conteudo_json_str = resposta_dict.get("conteudo")
            if not conteudo_json_str:
                return None
            
            analise = json.loads(conteudo_json_str)
            # Adicionamos o ratio_fala à análise para uso posterior
            analise['ratio_fala'] = ratio_fala
            print(f"[CALIBRADOR DE DIÁLOGO] Análise gerada: {analise}")
            return analise
        except (json.JSONDecodeError, KeyError):
            return None
    
    return None