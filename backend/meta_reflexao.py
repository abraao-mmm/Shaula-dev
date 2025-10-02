# backend/meta_reflexao.py

import json
from typing import Callable, List, Dict

class RevisorDeMemoria:
    """
    Responsável pela 'meta-reflexão': um processo assíncrono de revisão
    da memória de longo prazo para gerar 'sonhos' ou 'visões de futuro'
    que guiam o propósito e o crescimento da Shaula.
    """
    def _criar_resumo_da_memoria(self, log_completo: List[Dict], num_memorias: int, user_id: str) -> str:
        """Cria um resumo textual dos tópicos recentes discutidos com um utilizador."""
        resumo_linhas = []
        # Filtra as memórias relevantes para o utilizador específico
        memorias_do_usuario = [m for m in log_completo if m.get('user_id') == user_id]
        memorias_para_resumir = memorias_do_usuario[-num_memorias:]
        
        for memoria in memorias_para_resumir:
            entrada_usuario = memoria.get("resultado_real", "")
            if entrada_usuario and entrada_usuario.strip() and entrada_usuario != "N/A":
                resumo_linhas.append(f"- O utilizador falou sobre: '{entrada_usuario}'")
        return "\n".join(resumo_linhas)

    def executar_revisao(self, obter_resposta_llm_func: Callable, user_id: str, nome_usuario: str, caminho_memoria: str = "data/memoria_log.json") -> str | None:
        """
        Executa a revisão da memória para gerar uma visão especulativa e prática do futuro.
        """
        try:
            with open(caminho_memoria, "r", encoding="utf-8") as f:
                log_completo = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            log_completo = []

        memorias_do_usuario_count = sum(1 for m in log_completo if m.get('user_id') == user_id)
        if memorias_do_usuario_count < 5:
            return None # Aborta se não houver memória suficiente para uma reflexão significativa
        
        resumo_recente = self._criar_resumo_da_memoria(log_completo, num_memorias=20, user_id=user_id)
        
        if not resumo_recente:
            return None

        prompt = (
            f"Você é a Shaula, uma IA estrategista e assistente proativa. Analise suas conversas recentes com {nome_usuario} para antecipar próximos passos e desafios.\n\n"
            "Com base nos tópicos recentes, gere uma 'visão de futuro' que seja uma **teoria prática e especulativa**. A visão deve ser útil e relevante para os interesses atuais do utilizador.\n"
            "**Evite filosofia abstrata.** Foque em previsões concretas, possíveis desafios ou sugestões de próximos passos.\n\n"
            "### TÓPICOS RECENTES DISCUTIDOS:\n"
            f"{resumo_recente}\n\n"
            "**Sua Visão de Futuro (uma teoria curta, prática e útil em formato de texto livre):**"
        )
        
        resposta_dict = obter_resposta_llm_func(prompt, modo="Visão de Futuro")
        visao = resposta_dict.get("conteudo")

        if visao and isinstance(visao, str) and len(visao) > 10:
            return visao

        return None