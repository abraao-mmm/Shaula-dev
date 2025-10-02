# backend/hardware_bridge.py
import serial
import requests
import time
from rich.console import Console

console = Console()

# --- CONFIGURAÇÕES ---
ARDUINO_PORT = "COM5" # Lembre-se de verificar sua porta COM
API_URL = "http://127.0.0.1:8000/orb/status"
USER_ID = "379c4b4d-625f-4e7a-b136-aedecae9ba50"
POLL_INTERVAL = 3 # Diminuímos o intervalo para uma resposta mais rápida

# Mapeia o humor da Shaula para os comandos que o Arduino entende
MOOD_TO_COMMAND = {
    "Serena": "NEUTRO",
    "Curiosa": "NEUTRO",
    "Calma": "NEUTRO",
    "Grata": "FELIZ",
    "Animada": "FELIZ",
    "Contente": "FELIZ",
    "Afetuosa": "FELIZ",
    "Crise": "TRISTE",
    "Inquieta": "TRISTE",
    "Melancólica": "TRISTE",
}

def main():
    console.rule("[bold cyan]Ponte Hardware Shaula Orb - Ativada[/bold cyan]")
    
    try:
        arduino = serial.Serial(port=ARDUINO_PORT, baudrate=9600, timeout=1)
        console.print(f"✅ Conectado ao Arduino na porta {ARDUINO_PORT}", style="green")
        time.sleep(2) 
    except serial.SerialException:
        console.print(f"❌ Erro: Não foi possível conectar ao Arduino em {ARDUINO_PORT}.", style="bold red")
        return

    while True:
        try:
            response = requests.get(f"{API_URL}/{USER_ID}")
            response.raise_for_status()
            status = response.json()
            
            estado_mental = status.get("estado_mental", "Serena")
            command = MOOD_TO_COMMAND.get(estado_mental, "NEUTRO")
            
            arduino.write(f"{command}\n".encode('utf-8')) 
            console.print(f"Estado da Shaula: [bold magenta]{estado_mental}[/bold magenta] -> Comando enviado: [bold yellow]{command}[/bold yellow]")

        except requests.exceptions.RequestException:
            console.print("⚠️  Aguardando a API da Shaula ficar online...", style="yellow")
        except Exception as e:
            console.print(f"❌ Ocorreu um erro inesperado: {e}", style="red")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()