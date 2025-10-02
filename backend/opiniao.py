# opiniao.py
import json
from typing import Optional

class OpiniaoManager:
    """
    Gerencia os insights e opiniões da Shaula, decidindo qual é o mais
    relevante para compartilhar no momento certo.
    """
    def __init__(self, caminho_aprendizados="aprendizados.json"):
        self.aprendizados = []
        self.carregar_aprendizados(caminho_aprendizados)

    def carregar_aprendizados(self, caminho_arquivo: str):
        """Carrega os insights do arquivo JSON, agora ignorando linhas vazias ou malformadas."""
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                for line in f:
                    # AQUI ESTÁ A CORREÇÃO: Verificamos se a linha não está vazia
                    if line.strip():
                        try:
                            # Tentamos carregar o JSON da linha
                            self.aprendizados.append(json.loads(line)['insight'])
                        except json.JSONDecodeError:
                            # Se uma linha específica estiver corrompida, nós a ignoramos e avisamos
                            print(f"[AVISO] Linha corrompida ou malformada ignorada em {caminho_arquivo}: {line.strip()}")
        except FileNotFoundError:
            self.aprendizados = []

    def obter_opiniao_relevante(self, contexto_atual: str) -> Optional[str]:
        """
        Decide qual opinião/insight é mais relevante.
        (Por enquanto, a lógica é simples: pega o mais antigo da fila.
        No futuro, esta função ficará mais inteligente, comparando o insight
        com o contexto da conversa).
        """
        if self.aprendizados:
            # Pega o insight mais antigo da fila (First-In, First-Out) e o remove
            return self.aprendizados.pop(0)
        return None