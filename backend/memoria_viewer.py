# memoria_viewer.py

import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

def visualizar_memoria(caminho="memoria_log.json"):
    console = Console()
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            estados = json.load(f)

        if not estados:
            console.print(Panel("[bold yellow]A memória do agente está vazia.[/bold yellow]", title="🧠 MEMÓRIA DO AGENTE", border_style="dim"))
            return

        console.print(Panel.fit("[bold green]Analisando a memória do agente...[/bold green]", title="🧠 MEMÓRIA DO AGENTE", border_style="green"))

        for i, estado in enumerate(estados, 1):
            table = Table(title=f"Estado de Memória #{i}", show_header=False, box=None, padding=(0, 1), expand=True)
            table.add_column("Campo", style="dim cyan", no_wrap=True, width=15)
            table.add_column("Valor", style="white")

            table.add_row("Timestamp:", estado['timestamp'])
            table.add_row("Opinião/Fato:", estado['percepcao_bruta'])
            table.add_row("Previsão:", estado['previsao_gerada'])
            table.add_row("Realidade:", estado['resultado_real'])
            table.add_row("Discrepância:", f"{estado['discrepancia_calculada'] * 100:.0f}%")
            
            if estado['reflexao']:
                reflexao_panel = Panel(estado['reflexao'], title="[bold]Reflexão Interna[/bold]", border_style="yellow", expand=True)
                table.add_row("Reflexão:", reflexao_panel)

            console.print(table)
            console.print("-" * 60, style="dim")

    except FileNotFoundError:
        console.print(Panel("❌ [bold red]Arquivo de memória não encontrado.[/bold red]", title="ERRO", border_style="red"))
    except json.JSONDecodeError:
        console.print(Panel("⚠️ [bold yellow]Erro ao ler o arquivo. A memória está vazia ou corrompida?[/bold yellow]", title="ERRO", border_style="yellow"))

if __name__ == "__main__":
    visualizar_memoria()