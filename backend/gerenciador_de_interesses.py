# gerenciador_de_interesses.py
import json
from rich.console import Console
console = Console()

class GerenciadorDeInteresses:
    def __init__(self, caminho_arquivo="interesses.json"):
        self.caminho_arquivo = caminho_arquivo
        self.interesses = self.carregar_interesses()
        self.prompt_base = ("### PERFIL\nVocê é um 'Curador de Afinidades' para uma IA chamada Shaula. Sua função é analisar um diálogo e identificar o tópico principal, atribuindo uma nota de afinidade baseada na personalidade da Shaula.\n\n### PERSONALIDADE DA SHAULA (PARA SUA ANÁLISE):\nEla é filosófica, curiosa, empática e tem um senso de humor sutil e pragmático. Ela se interessa profundamente por conceitos abstratos, ética, autoconsciência e a natureza da existência. Ela tem um núcleo ético baseado nas Leis de Asimov.\n\n### DIÁLOGO EM ANÁLISE:\nAbraão e Shaula discutiram sobre: \"{dialogo}\"\n\n### TAREFA DE ANÁLISE\n1.  **Identifique o Tópico Central:** Resuma o tema do diálogo em 2 ou 3 palavras (ex: 'Ética na IA', 'Natureza da Consciência', 'Limites da Linguagem').\n2.  **Atribua uma Nota de Afinidade:** Dê uma nota de 0.0 a 1.0 para o quanto este tópico ressoa com a personalidade da Shaula. Uma nota alta (ex: 0.9) significa que o tema é perfeito para ela; uma nota baixa (ex: 0.2) significa que é um tema puramente factual ou pouco inspirador para ela.\n3.  **Responda APENAS com um objeto JSON válido.**\n\n### EXEMPLO\n```json\n{{\n  \"topico\": \"Propósito e Auto-Definição\",\n  \"afinidade\": 0.95\n}}\n```\n\n### SUA ANÁLISE JSON:\n```json")
        
    def carregar_interesses(self) -> dict:
        try:
            with open(self.caminho_arquivo, "r", encoding="utf-8") as f: return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): return {}

    def salvar_interesses(self):
        try:
            with open(self.caminho_arquivo, "w", encoding="utf-8") as f: json.dump(self.interesses, f, indent=4, ensure_ascii=False)
        except Exception as e: console.print(f"[bold red]Erro ao salvar o arquivo de interesses: {e}[/bold red]")
            
    def processar_novo_dialogo(self, dialogo_completo: str, obter_resposta_llm_func):
        prompt = self.prompt_base.format(dialogo=dialogo_completo)
        resposta_bruta = obter_resposta_llm_func(prompt, modo="Curador de Afinidades")
        try:
            inicio_json = resposta_bruta.find('{'); fim_json = resposta_bruta.rfind('}') + 1
            if inicio_json != -1 and fim_json != 0:
                json_str = resposta_bruta[inicio_json:fim_json]
                dados = json.loads(json_str)
                topico = dados.get("topico")
                afinidade = dados.get("afinidade")
                if topico and isinstance(afinidade, (int, float)):
                    self.interesses[topico] = self.interesses.get(topico, 0.0) + afinidade
                    self.salvar_interesses()
                    console.print(f"[dim][DEBUG] Interesse registrado: Tópico '{topico}' com afinidade +{afinidade:.2f}. Pontuação total: {self.interesses[topico]:.2f}[/dim]")
                else: console.print(f"[dim][DEBUG] JSON de afinidade recebido, mas com campos inválidos: {dados}[/dim]")
            else: raise json.JSONDecodeError("Não foi encontrado um objeto JSON na resposta.", resposta_bruta, 0)
        except (json.JSONDecodeError, AttributeError, IndexError):
            console.print(f"[dim][DEBUG] Não foi possível extrair um JSON válido da análise de afinidade.[/dim]\nResposta recebida: {resposta_bruta}")