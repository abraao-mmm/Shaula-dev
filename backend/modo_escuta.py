# modo_escuta.py
import sounddevice as sd
from scipy.io.wavfile import write
import openai
import os
from rich.console import Console
from rich.panel import Panel

# Configurações de áudio
TAXA_AMOSTRAGEM = 44100  # Taxa de amostragem em Hz
DURACAO_SEGUNDOS = 5      # Duração da gravação
NOME_ARQUIVO_TEMP = "temp_audio_input.wav"

console = Console()

def gravar_audio() -> str:
    """Grava áudio do microfone padrão e salva como um arquivo .wav temporário."""
    try:
        console.print(Panel(f"🎤 Comece a falar... Gravando por {DURACAO_SEGUNDOS} segundos.", title="[bold yellow]Modo de Escuta Ativado[/bold yellow]", border_style="yellow"))
        
        # Gravação do áudio
        gravacao = sd.rec(int(DURACAO_SEGUNDOS * TAXA_AMOSTRAGEM), samplerate=TAXA_AMOSTRAGEM, channels=1, dtype='int16')
        sd.wait()  # Espera a gravação terminar

        # Salva o arquivo de áudio
        write(NOME_ARQUIVO_TEMP, TAXA_AMOSTRAGEM, gravacao)
        
        console.print("[yellow]Gravação finalizada. Transcrevendo áudio...[/yellow]")
        return NOME_ARQUIVO_TEMP
    except Exception as e:
        console.print(Panel(f"❌ Erro ao tentar gravar o áudio: {e}\nVerifique se você tem um microfone conectado e se as permissões estão corretas.", title="Erro de Gravação", border_style="red"))
        return None

def transcrever_audio_openai(caminho_arquivo_audio: str) -> str:
    """Envia o arquivo de áudio para a API Whisper da OpenAI e retorna a transcrição."""
    if not caminho_arquivo_audio:
        return None
        
    try:
        client = openai.OpenAI() # A chave é lida do ambiente (.env)
        
        with open(caminho_arquivo_audio, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
              model="whisper-1", 
              file=audio_file
            )
        return transcript.text
        
    except Exception as e:
        console.print(Panel(f"❌ Erro na transcrição com a API da OpenAI: {e}", title="Erro de API", border_style="red"))
        return None
    finally:
        # Garante que o arquivo de áudio temporário seja sempre removido
        if os.path.exists(NOME_ARQUIVO_TEMP):
            os.remove(NOME_ARQUIVO_TEMP)

def ouvir_e_transcrever() -> str:
    """Orquestra o processo de gravação e transcrição."""
    caminho_audio = gravar_audio()
    if caminho_audio:
        texto_transcrito = transcrever_audio_openai(caminho_audio)
        if texto_transcrito:
            console.print(Panel(f"Você disse: [italic cyan]{texto_transcrito}[/italic cyan]", title="Texto Reconhecido", border_style="green", expand=False))
            return texto_transcrito
    return None