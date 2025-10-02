# backend/memoria.py

import json
import random
from datetime import datetime
from typing import Optional, List, Dict

# A importação agora é relativa
from .estado_agora import EstadoAgora

class Memoria:
    """
    Gere a corrente de consciência da Shaula, armazenando todos os 'EstadoAgora'
    e fornecendo métodos para aceder e persistir essa memória.
    """
    def __init__(self):
        self.estados: List[EstadoAgora] = []

    def registrar_estado(self, estado: EstadoAgora):
        """Adiciona um novo 'momento' (EstadoAgora) à memória."""
        self.estados.append(estado)

    def atualizar_ultimo_estado_com_resposta(self, resposta_shaula: str, user_id: str):
        """
        Encontra o último estado de interação de um utilizador que ainda não tem uma
        resposta da Shaula e atualiza-o.
        """
        for estado in reversed(self.estados):
            if estado.user_id == user_id and not estado.resposta_shaula:
                estado.resposta_shaula = resposta_shaula
                return

    def obter_ultima_resposta_shaula(self, user_id: str) -> str:
        """Obtém a última frase dita pela Shaula para um utilizador específico."""
        for estado in reversed(self.estados):
            if estado.user_id == user_id and hasattr(estado, 'resposta_shaula') and estado.resposta_shaula:
                return estado.resposta_shaula
        return "Nós ainda não conversámos."

    def obter_ultimas_falas_usuario(self, num_falas: int, user_id: str) -> List[str]:
        """Obtém as últimas N frases ditas por um utilizador específico."""
        falas = []
        for estado in reversed(self.estados):
            if estado.user_id == user_id:
                if len(falas) >= num_falas:
                    break
                # Garante que estamos a pegar apenas em interações reais do utilizador
                if estado.percepcao_bruta == "Conversa reativa" and estado.resultado_real:
                    falas.append(estado.resultado_real)
        return list(reversed(falas))

    def obter_memoria_aleatoria_significativa(self, user_id: str) -> Optional[Dict[str, str]]:
        """Seleciona aleatoriamente uma interação completa e significativa da memória para reflexão."""
        memorias_significativas = [
            estado for estado in self.estados 
            if estado.user_id == user_id and estado.percepcao_bruta == "Conversa reativa" and hasattr(estado, 'resposta_shaula') and estado.resposta_shaula
        ]
        if not memorias_significativas:
            return None
        
        memoria_escolhida = random.choice(memorias_significativas)
        return {
            "fala_usuario": memoria_escolhida.resultado_real,
            "resposta_shaula": memoria_escolhida.resposta_shaula,
            "timestamp": memoria_escolhida.timestamp.isoformat()
        }

    def obter_ultima_interacao_completa(self, user_id: str) -> Optional[Dict[str, str]]:
        """Obtém a última interação completa (fala do utilizador e resposta da Shaula)."""
        for estado in reversed(self.estados):
            if estado.user_id == user_id and estado.resultado_real and estado.resposta_shaula:
                return {
                    "resultado_real": estado.resultado_real,
                    "resposta_shaula": estado.resposta_shaula,
                    "timestamp": estado.timestamp.isoformat()
                }
        return None

    def exportar_para_json(self, caminho_arquivo: str = "data/memoria_log.json"):
        """Exporta toda a memória para um ficheiro JSON."""
        # Delega a serialização para o método .para_dict() de cada objeto EstadoAgora
        dados_serializados = [estado.para_dict() for estado in self.estados]
        try:
            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                json.dump(dados_serializados, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Erro ao salvar o ficheiro de memória: {e}")

    def carregar_de_json(self, caminho_arquivo: str = "data/memoria_log.json"):
        """Carrega a memória a partir de um ficheiro JSON."""
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
            # Delega a desserialização para o método de classe .de_dict() de EstadoAgora
            self.estados = [EstadoAgora.de_dict(dado) for dado in dados]
        except (FileNotFoundError, json.JSONDecodeError):
            self.estados = [] # Se o ficheiro não existir ou estiver corrompido, começa com a memória vazia