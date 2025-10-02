# vinculos_viewer.py
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

def get_nivel_intimidade(peso_afetivo: int) -> str:
    if peso_afetivo >= 9:
        return "[bold #ff00ff]Criador / Vínculo Máximo[/bold #ff00ff]"
    elif peso_afetivo >= 7:
        return "[bold #00ff00]Amigo Próximo[/bold #00ff00]"
    elif peso_afetivo >= 4:
        return "[cyan]Conhecido Amigável[/cyan]"
    else:
        return "[dim]Conhecido[/dim]"

def visualizar_vinculos(caminho="usuarios.json"):
    console = Console()
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados_usuarios = json.load(f)

        if not dados_usuarios:
            console.print(Panel("[bold yellow]A Shaula ainda não conhece ninguém.[/bold yellow]", title="🌐 MAPA DE VÍNCULOS", border_style="dim"))
            return

        table = Table(title="🌐 MAPA DE VÍNCULOS DA SHAULA", border_style="blue")
        table.add_column("Nome do Usuário", style="cyan", no_wrap=True)
        table.add_column("ID", style="dim", justify="center")
        table.add_column("Peso Afetivo", style="magenta", justify="center")
        table.add_column("Nível de Intimidade", justify="left")

        for user_id, user_data in dados_usuarios.items():
            nome = user_data.get("nome", "N/A")
            peso = user_data.get("peso_afetivo", 0)
            nivel = get_nivel_intimidade(peso)
            table.add_row(nome, user_id, str(peso), nivel)
        
        console.print(table)

    except FileNotFoundError:
        console.print(Panel("❌ [bold red]Ficheiro de usuários não encontrado. Converse com a Shaula para criar o primeiro perfil.[/bold red]", title="ERRO", border_style="red"))
    except json.JSONDecodeError:
        console.print(Panel("⚠️ [bold yellow]Erro ao ler o ficheiro de usuários. O ficheiro está vazio ou corrompido?[/bold yellow]", title="ERRO", border_style="yellow"))

if __name__ == "__main__":
    visualizar_vinculos()