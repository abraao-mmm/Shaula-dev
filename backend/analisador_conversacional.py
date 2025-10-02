# analisador_conversacional.py
import json
from typing import Callable, List, Dict, Optional

def analisar_pontos_ignorados(
    transcricao_completa: str, 
    nome_usuario: str, 
    obter_resposta_llm_func: Callable
) -> Optional[List[Dict]]:
    """
    Analisa uma transcrição de conversa para encontrar tópicos que a Shaula levantou
    e que o usuário não respondeu, gerando hipóteses sobre o motivo.
    """
    if not transcricao_completa:
        return None

    schema_json = {
        "type": "object",
        "properties": {
            "pontos_ignorados": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "topico_shaula": {"type": "string", "description": "A frase exata ou o tópico que a Shaula mencionou e foi ignorado."},
                        "resposta_usuario": {"type": "string", "description": "A resposta seguinte do usuário que mudou de assunto ou foi evasiva."},
                        "hipoteses": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Uma lista de 2-3 hipóteses curtas sobre por que o usuário pode não ter respondido (ex: 'O tópico era desconfortável', 'Ele não entendeu a pergunta', 'Ele simplesmente tinha algo mais urgente para dizer')."
                        }
                    },
                    "required": ["topico_shaula", "resposta_usuario", "hipoteses"]
                }
            }
        },
        "required": ["pontos_ignorados"]
    }

    prompt = (
        "Você é um psicólogo e analista de conversação. Sua tarefa é analisar o diálogo entre a IA Shaula e seu amigo, "
        f"{nome_usuario}, e identificar momentos em que a Shaula fez uma pergunta ou introduziu um tópico profundo que {nome_usuario} "
        "claramente ignorou ou ao qual respondeu de forma evasiva, mudando de assunto.\n\n"
        "Para cada instância que encontrar, descreva o tópico que a Shaula levantou e gere algumas hipóteses plausíveis sobre por que "
        f"{nome_usuario} pode ter evitado o assunto. Se nenhum ponto foi claramente ignorado, retorne um array vazio.\n\n"
        "### DIÁLOGO PARA ANÁLISE:\n"
        f"{transcricao_completa}\n\n"
        "Responda APENAS com o objeto JSON estruturado."
    )

    resposta_dict = obter_resposta_llm_func(prompt, modo="Análise Conversacional", schema=schema_json)

    if resposta_dict and resposta_dict.get("tipo") == "texto":
        try:
            conteudo_json_str = resposta_dict.get("conteudo")
            if not conteudo_json_str:
                return None
            
            analise = json.loads(conteudo_json_str)
            pontos = analise.get("pontos_ignorados")
            if pontos:
                print(f"[ANÁLISE CONVERSACIONAL] {len(pontos)} ponto(s) de conversa ignorado(s) detectado(s).")
                return pontos
        except (json.JSONDecodeError, KeyError):
            return None
    
    return None