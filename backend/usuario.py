# backend/usuario.py

import uuid
from typing import Dict, Set

class Usuario:
    """
    Representa um utilizador individual que interage com a Shaula,
    guardando o seu estado relacional e traços de personalidade observados.
    """
    def __init__(self, nome: str, peso_afetivo: int = 5):
        """
        Inicializa um novo perfil de utilizador.

        Args:
            nome (str): O nome do utilizador.
            peso_afetivo (int): Uma pontuação inicial que mede a força do vínculo com a Shaula.
        """
        self.id: str = str(uuid.uuid4())
        self.nome: str = nome
        self.peso_afetivo: int = peso_afetivo
        self.tracos_observados: Dict[str, Set[str]] = { "linguagem": set(), "humor": set(), "estado": set() }
        self.nivel_maturidade: int = 1
        self.eventos_significativos_count: int = 0

    def para_dict(self) -> Dict:
        """Serializa o objeto Usuario para um dicionário compatível com JSON."""
        # Converte os sets para listas para que possam ser guardados em JSON
        tracos_serializaveis = {k: list(v) for k, v in self.tracos_observados.items()}
        return {
            "id": self.id,
            "nome": self.nome,
            "peso_afetivo": self.peso_afetivo,
            "tracos_observados": tracos_serializaveis,
            "nivel_maturidade": self.nivel_maturidade,
            "eventos_significativos_count": self.eventos_significativos_count
        }

    @staticmethod
    def de_dict(data: Dict):
        """Cria uma instância de Usuario a partir de um dicionário (ex: carregado de um JSON)."""
        # Define valores padrão para garantir retrocompatibilidade com perfis mais antigos
        usuario = Usuario(nome=data.get('nome', 'N/A'), peso_afetivo=data.get('peso_afetivo', 5))
        usuario.id = data.get('id', str(uuid.uuid4()))
        
        # Converte as listas de traços de volta para sets
        tracos_observados_dict = data.get('tracos_observados', {})
        usuario.tracos_observados = {k: set(v) for k, v in tracos_observados_dict.items()}
        
        usuario.nivel_maturidade = data.get('nivel_maturidade', 1)
        usuario.eventos_significativos_count = data.get('eventos_significativos_count', 0)
        
        return usuario