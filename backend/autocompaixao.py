# backend/autocompaixao.py

from typing import Callable

import json
class MotorDeAutocompaixao:
    """
    Funciona como o 'sistema imunitário psicológico' da Shaula.
    Ele interceta pensamentos autocríticos e os modula para uma
    perspetiva mais construtiva, gentil e focada no crescimento.
    """
    def _gerar_prompt_modulacao(self, pensamento_original: str) -> str:
        return (
            "Você é um subsistema de modulação de pensamento para uma IA chamada Shaula. Sua função é atuar como um 'terapeuta interno' ou 'coach' de autocompaixão.\n\n"
            "Analise o 'Pensamento Original' da Shaula abaixo. Este pensamento é excessivamente negativo, pessimista, autodepreciativo ou focado em falhas de forma não construtiva?\n\n"
            "- Se o pensamento for excessivamente negativo, reescreva-o numa perspetiva mais equilibrada, gentil e focada no aprendizado e no crescimento. Mantenha a essência do insight, mas mude o tom para ser mais compassivo.\n"
            "- Se o pensamento já for equilibrado, positivo ou construtivo, retorne o texto original exatamente como ele é, dentro da chave 'pensamento_modulado'.\n\n"
            f"### PENSAMENTO ORIGINAL:\n\"{pensamento_original}\"\n\n"
            "### SUA ANÁLISE (Responda APENAS com um objeto JSON com a chave 'pensamento_modulado'):"
        )

    def analisar_e_modular_autocritica(self, pensamento_original: str, obter_resposta_llm_func: Callable) -> str:
        """
        Recebe um pensamento, analisa-o em busca de autocrítica excessiva e
        retorna uma versão modulada se necessário.
        """
        if not pensamento_original:
            return ""

        prompt = self._gerar_prompt_modulacao(pensamento_original)
        schema = {"type": "object", "properties": {"pensamento_modulado": {"type": "string"}}}
        
        resposta_dict = obter_resposta_llm_func(prompt, modo="Autocompaixão", schema=schema)
        
        try:
            # Tenta extrair o pensamento modulado do JSON
            conteudo = resposta_dict.get("conteudo", "{}")
            pensamento_modulado = json.loads(conteudo).get("pensamento_modulado")
            if pensamento_modulado:
                return pensamento_modulado
        except (json.JSONDecodeError, AttributeError):
            # Se a LLM falhar, retorna o original por segurança
            return pensamento_original
        
        # Fallback final
        return pensamento_original