# run_meta_reflexao.py

from agente import AgenteReflexivo
from main import obter_resposta_llm # Reutilizamos a função de chamada da API
from rich.console import Console

def executar_reflexao_profunda():
    """
    Script dedicado para executar a meta-reflexão da Shaula.
    Isso pode ser executado periodicamente para 'treiná-la' sem
    atrapalhar a conversa em tempo real.
    """
    console = Console()
    console.rule("[bold yellow]Iniciando Sessão de Meta-Reflexão Profunda[/bold yellow]")
    
    agente = AgenteReflexivo()
    agente.carregar_memoria()
    
    if len(agente.memoria.estados) < 5:
        console.print("Ainda não há memórias suficientes para uma reflexão profunda.")
        return

    # O método do agente agora é chamado diretamente por este script
    agente.executar_meta_reflexao(obter_resposta_llm)
    
    console.rule("[bold green]Sessão de Meta-Reflexão Concluída[/bold green]")

if __name__ == "__main__":
    executar_reflexao_profunda()