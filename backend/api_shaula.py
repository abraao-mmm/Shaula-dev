# backend/api_shaula.py (VERSÃO FINAL SEM ENDPOINT /state)
import json
import datetime
import random
from typing import Callable, Dict, Tuple, Optional, List, Any
import asyncio

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import openai

# --- Configuração do PATH e Importações do Projeto ---
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from agente import AgenteReflexivo
from gerenciador_usuarios import GerenciadorDeUsuarios
from usuario import Usuario
from estado_agora import EstadoAgora
from humor import Humor
from rich.console import Console

# --- Inicialização ---
load_dotenv()
app = FastAPI(
    title="Shaula API Reflexiva",
    description="API stateless para interagir com a Shaula, com suporte a streaming e comandos.",
    version="10.1-stable-no-sync"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
console = Console()
gerenciador_de_usuarios = GerenciadorDeUsuarios()

# --- Modelos Pydantic ---
class HumorState(BaseModel):
    estado_atual: str
    intensidade: int
    causa: str

class ShaulaState(BaseModel):
    user_id: str
    memoria_log: List[Dict]
    humor_atual: HumorState
    proposito_atual: str
    fadiga_cognitiva: int

class InteractionPayload(BaseModel):
    estado_shaula: ShaulaState
    mensagem_usuario: str

class CommandPayload(BaseModel):
    estado_shaula: ShaulaState
    comando: str

# --- Funções Auxiliares ---
def hidratar_agente(agente: AgenteReflexivo, estado: ShaulaState):
    """Preenche um agente 'fresco' com o estado recebido do cliente."""
    try:
        if estado.memoria_log:
            agente.memoria.estados = [EstadoAgora.de_dict(m) for m in estado.memoria_log]
        if estado.humor_atual:
            agente.humor = Humor.de_dict(estado.humor_atual.model_dump())
        agente.proposito_atual = estado.proposito_atual
        agente.fadiga_cognitiva = estado.fadiga_cognitiva
        agente.memoria_inicial_count = 0 
    except Exception as e:
        console.log(f"❌ [bold red]Erro ao hidratar o agente: {e}.[/bold red]")
        raise HTTPException(status_code=500, detail="Erro ao desserializar o estado do agente.")

def extrair_estado_agente(agente: AgenteReflexivo) -> ShaulaState:
    """Extrai o estado atual de um agente para ser enviado de volta ao cliente."""
    return ShaulaState(
        user_id=agente.usuario_atual.id,
        memoria_log=[estado.para_dict() for estado in agente.memoria.estados],
        humor_atual=agente.humor.para_dict(),
        proposito_atual=agente.proposito_atual,
        fadiga_cognitiva=agente.fadiga_cognitiva
    )

# --- Funções da LLM ---
def obter_resposta_llm_sync(prompt: str, modo: str = "Criatividade", schema: Optional[Dict] = None) -> Dict:
    console.print(f"\n[dim][API -> OpenAI (Sync): Núcleo de '{modo}' ativado...][/dim]")
    try:
        client = openai.OpenAI()
        kwargs = {"model": "gpt-4o", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 2048}
        if schema:
            kwargs["response_format"] = {"type": "json_object"}
            kwargs["messages"].insert(0, {"role": "system", "content": "You are a helpful assistant designed to output JSON."})
        response = client.chat.completions.create(**kwargs)
        conteudo = response.choices[0].message.content.strip()
        return {"tipo": "texto", "conteudo": conteudo}
    except Exception as e:
        console.log(f"❌ [bold red]API (Sync): Erro na chamada da OpenAI: {e}[/bold red]")
        raise HTTPException(status_code=500, detail=f"Erro na comunicação com a IA: {e}")

async def obter_resposta_llm_stream(prompt: str):
    console.print(f"\n[dim][API -> OpenAI (Stream): Núcleo de 'Criatividade' ativado...][/dim]")
    try:
        client = openai.AsyncOpenAI()
        stream = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048,
            stream=True
        )
        async for chunk in stream:
            content = chunk.choices[0].delta.content or ""
            yield content
            await asyncio.sleep(0.01)
    except Exception as e:
        error_message = f"Ocorreu um erro no núcleo criativo: {e}"
        console.log(f"❌ [bold red]API (Stream): {error_message}[/bold red]")
        yield error_message

# --- Rotas da API ---

@app.post("/interact")
async def interact(payload: InteractionPayload):
    try:
        usuario = gerenciador_de_usuarios.obter_usuario_por_id(payload.estado_shaula.user_id)
        if not usuario:
            usuario = gerenciador_de_usuarios.definir_usuario_atual(payload.estado_shaula.user_id)

        agente = AgenteReflexivo(usuario_atual=usuario, gerenciador=gerenciador_de_usuarios, console_log=console)
        hidratar_agente(agente, payload.estado_shaula)
        acao_json_str, _ = agente.processar_interacao_usuario(payload.mensagem_usuario, obter_resposta_llm_sync)

        if acao_json_str:
            escolha = json.loads(acao_json_str)
            if escolha.get("ferramenta") == "resposta_direta_streaming":
                prompt = escolha.get("parametros", {}).get("prompt", "")
                return StreamingResponse(obter_resposta_llm_stream(prompt), media_type="text/event-stream")

        async def silent_stream():
            yield "[Shaula escolheu o silêncio]"
        return StreamingResponse(silent_stream(), media_type="text/event-stream")
    except Exception as e:
        console.log(f"❌ [bold red]Erro fatal no endpoint /interact: {e}[/bold red]")
        async def error_stream():
            yield f"Erro no servidor: {e}"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

@app.post("/encerrar-sessao")
async def encerrar_sessao(payload: ShaulaState):
    try:
        usuario = gerenciador_de_usuarios.obter_usuario_por_id(payload.user_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        agente = AgenteReflexivo(usuario_atual=usuario, gerenciador=gerenciador_de_usuarios, console_log=console)
        hidratar_agente(agente, payload)

        feedback_analise = agente.executar_analise_de_sessao(obter_resposta_llm_sync) or "Análise da sessão concluída."
        agente.executar_meta_reflexao(obter_resposta_llm_sync)
        
        agente.salvar_memoria()
        gerenciador_de_usuarios.salvar_usuarios()
        
        return {
            "mensagem_feedback": feedback_analise,
            "mensagem_final": "Sessão encerrada e processada. Para iniciar uma nova conversa, atualize a página."
        }
    except Exception as e:
        console.log(f"❌ [bold red]Erro no endpoint /encerrar-sessao: {e}[/bold red]")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/command")
async def execute_command(payload: CommandPayload):
    try:
        usuario = gerenciador_de_usuarios.obter_usuario_por_id(payload.estado_shaula.user_id)
        if not usuario: raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        agente = AgenteReflexivo(usuario_atual=usuario, gerenciador=gerenciador_de_usuarios, console_log=console)
        hidratar_agente(agente, payload.estado_shaula)

        comando = payload.comando.lower()
        feedback_text = f"Comando '{comando}' executado."
        
        comandos_map = {
            'refletir': agente.executar_meta_reflexao,
            'encenar': agente.executar_encenacao_memoria,
            'pulsar': agente.pulsar
        }

        if comando in comandos_map:
            funcao = comandos_map[comando]
            resultado = funcao(obter_resposta_llm_sync)
            if isinstance(resultado, tuple):
                acao_json_str, raciocinio_log = resultado
                if acao_json_str:
                    acao = json.loads(acao_json_str)
                    prompt = acao.get("parametros", {}).get("prompt", "...")
                    feedback_text = obter_resposta_llm_sync(prompt).get("conteudo")
                else:
                    feedback_text = f"[Shaula decidiu manter o silêncio. Raciocínio: {raciocinio_log}]"
            elif isinstance(resultado, str):
                feedback_text = resultado
        else:
            raise HTTPException(status_code=400, detail="Comando desconhecido.")
        
        novo_estado = extrair_estado_agente(agente)
        return {"novo_estado_shaula": novo_estado, "mensagem_feedback": feedback_text}
    except Exception as e:
        console.log(f"❌ [bold red]Erro no endpoint /command: {e}[/bold red]")
        raise HTTPException(status_code=500, detail=str(e))

# --- Endpoints do Dashboard ---
@app.get("/vinculos", tags=["Dashboard"])
def get_vinculos():
    try:
        with open("usuarios.json", "r", encoding="utf-8") as f:
            usuarios_data = json.load(f)
        vinculos = [{"nome": udata.get("nome"), "peso_afetivo": udata.get("peso_afetivo")} for uid, udata in usuarios_data.items()]
        return sorted(vinculos, key=lambda x: x['peso_afetivo'], reverse=True)
    except FileNotFoundError: return []
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/sonhos/{user_id}", tags=["Dashboard"])
def get_sonhos(user_id: str):
    try:
        with open("sonhos.json", "r", encoding="utf-8") as f:
            sonhos_usuario = [json.loads(line) for line in f if line.strip() and json.loads(line).get('user_id') == user_id]
        return list(reversed(sonhos_usuario))
    except FileNotFoundError: return []
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/crises/{user_id}", tags=["Dashboard"])
def get_crises(user_id: str):
    try:
        with open("crises_log.json", "r", encoding="utf-8") as f:
            crises_usuario = [json.loads(line) for line in f if line.strip() and json.loads(line).get('user_id') == user_id]
        return list(reversed(crises_usuario))
    except FileNotFoundError: return []
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

# --- Endpoint da Orbe ---
@app.get("/orb/status/{user_id}", tags=["Shaula Orb"])
def get_orb_status(user_id: str):
    try:
        with open("humor_status.json", "r", encoding="utf-8") as f:
            humor_data = json.load(f)
        estado_mental = humor_data.get("estado_atual", "Serena")
        return {"user_id": user_id, "timestamp": datetime.datetime.now().isoformat(), "estado_mental": estado_mental}
    except (FileNotFoundError, json.JSONDecodeError):
        return {"estado_mental": "Serena"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Não foi possível ler o estado de humor: {e}")
