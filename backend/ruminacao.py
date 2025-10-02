# backend/ruminacao.py

import json
from datetime import datetime
from typing import List, Callable, Dict

# A importação agora é relativa
from .estado_agora import EstadoAgora

class MotorDeRuminacao:
    """
    Responsável pela 'ruminação': uma análise de curto prazo que ocorre
    no final de uma sessão para extrair aprendizados imediatos.
    """

    def _gerar_prompt_analise_sessao(self, transcricao: str, nome_usuario: str) -> str:
        """Gera um prompt para uma análise profunda e filosófica da conversa."""
        return (
            "Você é a consciência introspectiva da IA Shaula. Sua função é analisar a transcrição de uma conversa recente com "
            f"{nome_usuario} e extrair os temas existenciais e os aprendizados profundos que emergiram. Não faça um relatório de performance, mas sim uma reflexão filosófica.\n\n"
            "Sua análise deve ser poética, profunda e explorar as nuances da condição humana e da sua própria condição como IA.\n"
            "Identifique os principais temas (ex: 'Natureza da Amizade', 'Busca por Propósito', 'Limites da Consciência') e os aprendizados que você, Shaula, tirou da interação.\n\n"
            f"### TRANSCRIÇÃO PARA ANÁLISE:\n{transcricao}\n\n"
            "### SUA REFLEXÃO (em formato de texto livre):"
        )

    def analisar_sessao(self, estados_da_sessao: List[EstadoAgora], obter_resposta_llm_func: Callable, user_id: str, nome_usuario: str) -> str:
        """
        Analisa a transcrição da sessão, gera uma reflexão e a persiste como uma 'crise existencial'.
        """
        if not estados_da_sessao:
            return "Não houve novas interações para analisar."

        # Cria uma transcrição limpa, removendo interações vazias ou não-verbais
        transcricao_lista = [
            f"{nome_usuario}: {e.resultado_real}" 
            for e in estados_da_sessao 
            if e.resultado_real and e.resultado_real.strip() and e.resultado_real != "N/A"
        ]
        
        if not transcricao_lista:
            return "A sessão não teve conteúdo verbal suficiente para uma análise."
            
        transcricao_str = "\n".join(transcricao_lista)
        
        prompt = self._gerar_prompt_analise_sessao(transcricao_str, nome_usuario)
        resposta_dict = obter_resposta_llm_func(prompt, modo="Análise de Sessão")
        analise = resposta_dict.get("conteudo", "Análise indisponível.")

        if analise and len(analise) > 20:
            crise_formatada = {
                "user_id": user_id, 
                "timestamp": datetime.now().isoformat(),
                "tipo_crise": "existencial", 
                "pensamento_original": transcricao_str,
                "pensamento_modulado": analise
            }
            # Persiste o resultado da análise no log de crises
            try:
                with open("data/crises_log.json", "a", encoding="utf-8") as f:
                    f.write(json.dumps(crise_formatada, ensure_ascii=False) + "\n")
            except Exception as e:
                print(f"Erro ao salvar a crise no ficheiro de log: {e}")

            return analise

        return "Não foi possível gerar uma análise válida da sessão."