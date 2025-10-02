# backend/gerenciador_usuarios.py

import json
from rich.console import Console
from typing import Dict, Optional

# A importação agora é relativa, pois 'usuario' está no mesmo pacote 'backend'
from .usuario import Usuario

console = Console()

class GerenciadorDeUsuarios:
    """
    Responsável por carregar, salvar e gerir os perfis de todos os utilizadores
    que interagem com a Shaula.
    """
    def __init__(self, caminho_arquivo: str = "data/usuarios.json"):
        """
        Inicializa o gestor de utilizadores.

        Args:
            caminho_arquivo (str): O caminho para o ficheiro JSON onde os perfis são guardados.
        """
        self.caminho_arquivo: str = caminho_arquivo
        self.usuarios: Dict[str, Usuario] = self._carregar_usuarios()
        self.usuario_atual: Optional[Usuario] = None

    def _carregar_usuarios(self) -> Dict[str, Usuario]:
        """Carrega os perfis de utilizador a partir do ficheiro JSON."""
        try:
            with open(self.caminho_arquivo, 'r', encoding='utf-8') as f:
                dados_usuarios = json.load(f)
                # Usa o método de classe 'de_dict' para recriar os objetos Usuario
                return {uid: Usuario.de_dict(udata) for uid, udata in dados_usuarios.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def salvar_usuarios(self):
        """Salva todos os perfis de utilizador atuais no ficheiro JSON."""
        # Usa o método 'para_dict' de cada objeto Usuario para a serialização
        dados_para_salvar = {uid: u.para_dict() for uid, u in self.usuarios.items()}
        try:
            with open(self.caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_para_salvar, f, indent=4, ensure_ascii=False)
        except IOError as e:
            console.print(f"[bold red]Erro ao salvar o ficheiro de utilizadores: {e}[/bold red]")

    def obter_ou_criar_usuario_atual(self, nome_usuario: str) -> Usuario:
        """
        Procura um utilizador pelo nome. Se existir, define-o como o atual e retorna-o.
        Se não existir, cria um novo perfil, salva-o e retorna-o.
        """
        # Procura por um utilizador existente (ignorando maiúsculas/minúsculas)
        for usuario in self.usuarios.values():
            if usuario.nome.lower() == nome_usuario.lower():
                self.usuario_atual = usuario
                console.print(f"Perfil encontrado. Bem-vindo de volta, [cyan]{usuario.nome}[/cyan]!")
                return usuario
        
        # Se não encontrou, cria um novo
        console.print(f"Perfil para '{nome_usuario}' não encontrado. A criar novo perfil.")
        novo_usuario = Usuario(nome=nome_usuario)
        
        # O primeiro utilizador a ser criado tem um peso afetivo máximo por defeito
        if not self.usuarios:
            novo_usuario.peso_afetivo = 10 
            
        self.usuarios[novo_usuario.id] = novo_usuario
        self.usuario_atual = novo_usuario
        self.salvar_usuarios()
        console.print(f"Novo perfil para [cyan]{novo_usuario.nome}[/cyan] criado com sucesso.")
        return novo_usuario

    def obter_usuario_por_id(self, user_id: str) -> Optional[Usuario]:
        """Retorna um objeto de utilizador com base no seu ID."""
        return self.usuarios.get(user_id)