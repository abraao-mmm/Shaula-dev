# backend/api_rapina.py (VERSÃO COM IMPORTAÇÕES CORRIGIDAS)

import uvicorn
import base64
import cv2
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rich.console import Console

# --- CORREÇÃO APLICADA AQUI ---
# Adicionamos um '.' para indicar que são importações locais dentro do pacote 'backend'
from .agente import AgenteReflexivo
from .gerenciador_usuarios import GerenciadorDeUsuarios
from .main import obter_resposta_llm

# --- Inicialização ---
app = FastAPI(title="API do Projeto Rapina (Shaula)", version="1.0")
console = Console()

try:
    gerenciador = GerenciadorDeUsuarios(caminho_arquivo="data/usuarios.json")
    console.log("[bold green]Gerenciador de Utilizadores carregado.[/bold green]")
except Exception as e:
    console.log(f"[bold red]Erro ao carregar Gerenciador de Utilizadores: {e}[/bold red]")
    gerenciador = GerenciadorDeUsuarios(caminho_arquivo="data/usuarios.json")

class RapinaRequest(BaseModel):
    imagem_base64: str
    pergunta: str
    user_id: str

@app.post("/rapina/analisar", summary="Analisa uma imagem com a Shaula")
async def analisar_visao(request: RapinaRequest):
    console.log(f"Recebida requisição de análise visual do utilizador: {request.user_id}")
    console.log(f"Pergunta: [yellow]'{request.pergunta}'[/yellow]")

    usuario_atual = gerenciador.obter_usuario_por_id(request.user_id)
    if not usuario_atual:
        raise HTTPException(status_code=404, detail=f"Utilizador com ID {request.user_id} não encontrado.")
    
    agente_shaula = AgenteReflexivo(usuario_atual=usuario_atual, gerenciador=gerenciador, console_log=console)
    console.log(f"Agente Shaula instanciado para '{usuario_atual.nome}'.")

    try:
        # Chama o novo método do agente que retorna um dicionário
        respostas_finais = agente_shaula.processar_interacao_visual(
            imagem_base64=request.imagem_base64,
            pergunta_usuario=request.pergunta,
            obter_resposta_llm_func=obter_resposta_llm
        )
        
        console.log(f"Resposta Visual Gerada: [cyan]'{respostas_finais.get('resposta_visual')}'[/cyan]")
        console.log(f"Resposta de Áudio Gerada: [green]'{respostas_finais.get('resposta_audio')}'[/green]")
        
        # Retorna o objeto JSON completo para o cliente
        return respostas_finais

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro interno ao processar a tua visão: {e}")

if __name__ == "__main__":
    console.print("[bold cyan]Iniciando o servidor da API da Shaula para o Projeto Rapina...[/bold cyan]")
    uvicorn.run("backend.api_rapina:app", host="127.0.0.1", port=8000, reload=True)