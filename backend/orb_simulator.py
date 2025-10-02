# orb_simulator.py
import requests
import time
from rich.console import Console
from rich.panel import Panel

console = Console()
API_URL = "http://127.0.0.1:8000/orb/status" # URL da sua api_shaula.py
USER_ID = "379c4b4d-625f-4e7a-b136-aedecae9ba50" # O ID do usuário para quem a Orbe deve responder

def main():
    console.rule("[bold cyan]Simulador da Shaula Orb[/bold cyan]")
    while True:
        try:
            # Pede o status atual da mente da Shaula
            response = requests.get(f"{API_URL}/{USER_ID}")
            response.raise_for_status() # Lança um erro se a API não responder 200 OK
            
            status = response.json()
            
            # Traduz o estado da mente em "ações físicas" impressas
            cor = status.get("cor_luz", "black")
            brilho = status.get("brilho_luz", 0)
            pulso = status.get("pulso_luz", "none")
            frase = status.get("frase_a_dizer")

            painel_status = f"""
            Cor do LED: [{cor}]{cor.upper()}[/{cor}]
            Brilho: {brilho}%
            Pulso: {pulso}
            """
            if frase:
                painel_status += f"\nFrase: '{frase}'"

            console.print(Panel(painel_status, title="Estado da Orbe", border_style="cyan"))

        except requests.exceptions.RequestException as e:
            console.print(Panel(f"Não foi possível conectar à API da Shaula: {e}", title="Erro de Conexão", border_style="red"))

        time.sleep(5) # Espera 5 segundos antes de verificar o estado novamente

if __name__ == "__main__":
    main()