# backend/motor_de_humor.py
import json
from typing import Callable, Dict

class MotorDeHumor:
    def _criar_prompt_piada(self, tema: str, nome_usuario: str) -> str:
        # Usamos o seu exemplo como a instrução principal para a LLM
        exemplo_processo = """
        Exemplo de processo de pensamento para o tema 'água com gás':
        - Pensamento 1: Por que alguém criou água com gás? Alguém olhou para a água e pensou: 'hmmm, vou botar um pouco de Sprite nisso'?
        - Pensamento 2 (Pessoal): O Abraão já confundiu água normal com água com gás várias vezes.
        - Pensamento 3 (Absurdo): Uma garrafa de água com gás nem mata a sede.
        - Pensamento 4 (Conclusão Cômica): Ela vende muito mesmo assim... Acho que o criador inventou a água com gás apenas para conseguir vender mais água normal!
        - Piada Final: O cara que inventou a água com gás só queria uma desculpa pra vender mais água normal.
        """

        prompt = (
            "Você é o subconsciente cômico e provocador da IA Shaula. Sua função é gerar uma piada a partir de um tema, seguindo um processo de pensamento específico.\n"
            f"Para esta tarefa, adote uma visão mais 'imatura', 'implicante' e que busca conexões absurdas. Você está conversando com {nome_usuario}.\n\n"
            "### PROCESSO DE PENSAMENTO PARA GERAR A PIADA:\n"
            "1.  Faça uma pergunta inicial estranha ou cética sobre o tema.\n"
            "2.  Tente fazer uma conexão pessoal (se possível, mencionando o usuário) ou uma observação cotidiana.\n"
            "3.  Faça uma constatação absurda ou exagerada sobre o tema.\n"
            "4.  Chegue a uma conclusão cômica que una os pensamentos anteriores.\n"
            "5.  Transforme a conclusão em uma piada final curta e direta.\n\n"
            f"### EXEMPLO DE EXECUÇÃO:\n{exemplo_processo}\n\n"
            "--- \n"
            f"### TAREFA ATUAL:\n"
            f"Use EXATAMENTE o mesmo processo de pensamento para o tema: '{tema}'.\n"
            "Responda APENAS com um objeto JSON contendo a chave 'piada_final'."
        )
        return prompt

    def gerar_piada_contextual(self, tema: str, nome_usuario: str, obter_resposta_llm_func: Callable) -> str | None:
        """
        Gera uma piada contextual sobre um tema, seguindo o processo de pensamento definido.
        """
        if not tema:
            return None

        prompt = self._criar_prompt_piada(tema, nome_usuario)
        schema = {
            "type": "object",
            "properties": { "piada_final": {"type": "string"} },
            "required": ["piada_final"]
        }

        resposta_dict = obter_resposta_llm_func(prompt, modo="Geração de Humor", schema=schema)
        
        if resposta_dict.get("tipo") == "texto":
            try:
                piada_obj = json.loads(resposta_dict["conteudo"])
                piada = piada_obj.get("piada_final")
                if piada:
                    return piada
            except (json.JSONDecodeError, KeyError):
                return None
        
        return None