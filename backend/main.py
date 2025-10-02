# backend/main.py (VERSÃO FINAL E CORRIGIDA)

import json
import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markup import escape
from typing import Callable, Dict, Optional

# --- CARREGAMENTO ROBUSTO DAS VARIÁVEIS DE AMBIENTE ---
try:
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError
except:
    print("AVISO: Ficheiro .env não encontrado ou chave OPENAI_API_KEY em falta.")

# --- Importações Relativas do Pacote 'backend' ---
from .agente import AgenteReflexivo
from .gerenciador_usuarios import GerenciadorDeUsuarios

def main():
    """
    Função principal para executar a interface de linha de comando (CLI) da Shaula.
    """
    console = Console()
    console.clear()
    console.print(Panel.fit("[bold #33ff57]=== Assistente Reflexiva Shaula - Interface de Comando ===[/bold #33ff57]"))
    
    try:
        gerenciador_de_usuarios = GerenciadorDeUsuarios(caminho_arquivo="data/usuarios.json")
        nome_usuario = console.input("👤 [bold yellow]Por favor, digite o seu nome para começar:[/bold yellow] ")
        usuario_atual = gerenciador_de_usuarios.obter_ou_criar_usuario_atual(nome_usuario)
        agente = AgenteReflexivo(usuario_atual=usuario_atual, gerenciador=gerenciador_de_usuarios, console_log=console)
    except Exception as e:
        console.print(f"[bold red]Erro fatal na inicialização: {e}[/bold red]")
        return

    console.print(f"🧠 [cyan]Memória carregada com {len(agente.memoria.estados)} registos.[/cyan]")
    console.print("[yellow]Comandos:[/yellow] 'analisar olist', 'sair', 'refletir'")
    console.print("-" * 60, style="dim")

    while True:
        try:
            prompt_usuario = f"🎤 [bold]{usuario_atual.nome}:[/bold] "
            entrada_usuario = console.input(prompt_usuario)
            
            if entrada_usuario.lower().strip() == 'sair':
                agente.executar_analise_de_sessao()
                gerenciador_de_usuarios.salvar_usuarios()
                break

            resposta_json, raciocinio = agente.processar_entrada_do_utilizador(entrada_usuario)
            
            if raciocinio:
                console.print(Panel(raciocinio, title="🧠 Raciocínio Lógico", border_style="grey50"))
            
            # --- LÓGICA DE PROCESSAMENTO DE AÇÃO CORRIGIDA ---
            if resposta_json:
                try:
                    acao = json.loads(resposta_json)
                    if acao.get("ferramenta") == "resposta_direta_streaming":
                        parametros = acao.get("parametros", {})
                        texto_final_para_exibir = ""

                        # Verifica se o agente já enviou o texto final
                        if "texto_final" in parametros:
                            texto_final_para_exibir = parametros["texto_final"]
                        # Se não, verifica se ele enviou um prompt para ser processado
                        elif "prompt" in parametros:
                            # Chama a LLM para obter o texto final
                            resposta_dict = agente.obter_resposta_llm(parametros["prompt"])
                            texto_final_para_exibir = resposta_dict.get("conteudo", "Erro ao gerar resposta final.")
                        
                        if texto_final_para_exibir:
                            console.print(Panel.fit("📢 Resposta da Shaula", border_style="magenta"))
                            console.print(escape(texto_final_para_exibir), style="bright_white")
                            agente.memoria.atualizar_ultimo_estado_com_resposta(texto_final_para_exibir, agente.usuario_atual.id)

                except Exception as e:
                    console.print(f"[red]Erro ao processar a ação da Shaula: {e}[/red]")
            
            console.print("\n" + "-" * 60, style="dim")
        except KeyboardInterrupt:
            agente.executar_analise_de_sessao()
            gerenciador_de_usuarios.salvar_usuarios()
            break
            
    agente.salvar_memoria()
    console.print("📝 [green]Sessão encerrada e memória salva com sucesso.[/green]")

if __name__ == "__main__":
    main()