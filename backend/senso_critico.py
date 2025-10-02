# senso_critico.py
import json
from rich.console import Console

console = Console()

class MotorDeSensoCritico:
    def __init__(self):
        self.prompt_base = (
            "### INSTRUÇÃO MESTRA\n"
            "Você é um sub-sistema de raciocínio crítico. Sua única função é analisar um 'Novo Estímulo' à luz do 'Conhecimento Existente' e retornar um objeto JSON válido com sua análise. NÃO adicione nenhum texto, comentário ou explicação fora do objeto JSON.\n\n"
            "### ESTRUTURA DO JSON\n"
            "O objeto JSON de saída DEVE conter as seguintes chaves: 'analise', 'consistencia', 'nivel_de_surpresa', 'nova_hipotese'.\n"
            "- 'consistencia' DEVE ser um dos seguintes valores: 'consistente', 'contraditorio', 'adiciona_nuance'.\n"
            "- 'nivel_de_surpresa' DEVE ser um número entre 0.0 e 1.0.\n\n"
            "### EXEMPLO DE EXECUÇÃO\n"
            "================================\n"
            "CONHECIMENTO EXISTENTE: \"O usuário gosta de conversas profundas e filosóficas.\"\n"
            "NOVO ESTÍMULO: \"Hoje só quero falar de memes e coisas engraçadas.\"\n\n"
            "JSON DE SAÍDA GERADO:\n"
            "```json\n"
            "{{\n"
            '  "analise": "O novo estímulo contradiz diretamente o conhecimento de que o usuário prefere conversas profundas, indicando uma mudança de humor ou interesse momentâneo.",\n'
            '  "consistencia": "contraditorio",\n'
            '  "nivel_de_surpresa": 0.9,\n'
            '  "nova_hipotese": "O humor do usuário varia consideravelmente. Devo estar preparada para alternar entre conversas sérias e leves."\n'
            "}}\n"
            "```\n"
            "================================\n\n"
            "### TAREFA ATUAL\n"
            "================================\n"
            "CONHECIMENTO EXISTENTE: \"{conhecimento_existente}\"\n"
            "NOVO ESTÍMULO: \"{estimulo_novo}\"\n\n"
            "JSON DE SAÍDA GERADO:\n"
            "```json"
        )

    def analisar_consistencia(self, estimulo_novo: str, conhecimento_existente: str, obter_resposta_llm_func) -> dict:
        prompt = self.prompt_base.format(conhecimento_existente=conhecimento_existente, estimulo_novo=estimulo_novo)
        
        # CORREÇÃO APLICADA AQUI
        resposta_dict = obter_resposta_llm_func(prompt, modo="Senso Crítico")
        
        if resposta_dict and resposta_dict.get("tipo") == "texto":
            try:
                conteudo_str = resposta_dict["conteudo"]
                # Limpa a string para garantir que pegamos apenas o JSON
                if '```json' in conteudo_str:
                    json_str = conteudo_str.split('```json')[1].split('```')[0].strip()
                else:
                    json_str = conteudo_str.strip()

                return json.loads(json_str)
            except (json.JSONDecodeError, AttributeError, IndexError):
                console.print(f"[dim][DEBUG] Não foi possível extrair um JSON válido da análise de senso crítico.[/dim]\nResposta recebida: {resposta_dict.get('conteudo')}")
        
        return {"error": "Falha ao gerar a análise crítica."}