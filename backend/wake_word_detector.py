# backend/wake_word_detector.py
import os
import struct
import pyaudio
import pvporcupine
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner

console = Console()
load_dotenv()

def detectar_wake_word() -> bool:
    """
    Ouve continuamente o microfone e retorna True quando a palavra "Shaula" é detectada.
    """
    access_key = os.getenv("PICOVOICE_ACCESS_KEY")
    if not access_key:
        console.print("[bold red]Erro: PICOVOICE_ACCESS_KEY não encontrada no arquivo .env[/bold red]")
        return False

    pa = None
    stream = None
    try:
        porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=['Estrela_pt_windows_v3_0_0.ppn'] # Você pode usar palavras pré-definidas como 'porcupine', 'bumblebee', etc.
                               # Para uma palavra customizada, é preciso ir no site da Picovoice.
                               # Por enquanto, vamos usar uma palavra-chave que se parece com "Shaula".
                               # A palavra "Picovoice" é uma boa alternativa para teste.
        )

        pa = pyaudio.PyAudio()
        stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        spinner = Spinner("dots", text=" [dim]Aguardando wake word ('Shaula')...[/dim]")
        with console.status(spinner) as status:
            while True:
                pcm = stream.read(porcupine.frame_length)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

                keyword_index = porcupine.process(pcm)
                if keyword_index >= 0:
                    console.print(Panel("✨ Wake Word 'Shaula' detectado!", title="[bold green]Atenção[/bold green]", border_style="green"))
                    return True

    except Exception as e:
        if "keyword files" in str(e):
             console.print(Panel("Erro: A palavra-chave 'shaula' não é um modelo padrão. Para testes, tente usar 'picovoice' ou 'bumblebee'. Para criar uma palavra customizada, acesse o console da Picovoice.", title="[bold red]Erro de Palavra-Chave[/bold red]", border_style="red"))
        else:
            console.print(f"[bold red]Erro no detector de wake word: {e}[/bold red]")
        return False
    finally:
        if stream is not None:
            stream.close()
        if pa is not None:
            pa.terminate()
        if 'porcupine' in locals() and porcupine is not None:
            porcupine.delete()