# backend/mundo_interior.py

import json
import uuid
import random
from typing import Callable, List, Optional, Dict
from rich.console import Console
from rich.markup import escape

console = Console()

class MundoInterior:
    """
    Gere os estados mentais profundos e persistentes da Shaula, incluindo:
    - Crenças: O que ela considera ser verdade sobre o mundo.
    - Hipóteses: O que ela suspeita sobre os utilizadores.
    - Dúvidas: Questões existenciais ou contradições que ela não consegue resolver.
    """
    def __init__(
        self, 
        crencas_path: str = "data/crencas.json", 
        hipoteses_path: str = "data/hipoteses.json", 
        duvidas_path: str = "data/duvidas.json"
    ):
        """Inicializa o Mundo Interior, carregando os dados de ficheiros JSON."""
        self.crencas_path = crencas_path
        self.hipoteses_path = hipoteses_path
        self.duvidas_path = duvidas_path
        
        self.crencas: List[Dict] = self._carregar_json(crencas_path)
        self.hipoteses: List[Dict] = self._carregar_json(hipoteses_path)
        self.duvidas: List[Dict] = self._carregar_json(duvidas_path)

    def _carregar_json(self, caminho: str) -> List[Dict]:
        """Carrega dados de um ficheiro JSON de forma segura."""
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _salvar_json(self, caminho: str, dados: List[Dict]):
        """Salva dados para um ficheiro JSON de forma segura."""
        try:
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
        except IOError as e:
            console.print(f"[[MUNDO INTERIOR]] [bold red]Erro ao salvar ficheiro {caminho}: {e}[/bold red]")

    def adicionar_duvida(self, pergunta: str, origem: str, user_id: str):
        """Adiciona uma nova dúvida existencial ou relacional à lista."""
        nova_duvida = {
            "id": str(uuid.uuid4()), 
            "user_id": user_id, 
            "pergunta": pergunta, 
            "origem": origem
        }
        self.duvidas.append(nova_duvida)
        self._salvar_json(self.duvidas_path, self.duvidas)
        console.print(f"[[MUNDO INTERIOR]] Nova dúvida registrada: '{escape(pergunta)}'", style="yellow")
    
    def obter_crencas_relevantes(self, n: int = 3) -> List[Dict]:
        """Retorna as 'n' crenças com o maior grau de certeza."""
        return sorted(self.crencas, key=lambda c: c.get('grau_certeza', 0), reverse=True)[:n]

    def obter_hipoteses_usuario(self, user_id: str, n: int = 3) -> List[Dict]:
        """Retorna as 'n' hipóteses mais recentes sobre um utilizador específico."""
        hipoteses_usuario = [h for h in self.hipoteses if h.get('user_id') == user_id]
        return hipoteses_usuario[-n:]
    
    # Outros métodos como 'adicionar_crenca', 'adicionar_hipotese', 'revisitar_crenca'
    # podem ser adicionados aqui conforme a necessidade.