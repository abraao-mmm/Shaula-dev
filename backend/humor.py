# backend/humor.py

from typing import Dict

class Humor:
    """
    Simula o estado de humor da Shaula, que é influenciado por eventos
    e decai gradualmente com o tempo de volta a um estado de equilíbrio.
    """
    # Constantes para a taxa de decaimento, melhorando a legibilidade
    DECAIMENTO_NORMAL = 1
    DECAIMENTO_ACELERADO = 2
    
    def __init__(self):
        """Inicializa o estado de humor da Shaula."""
        self.estado_base: str = "Serena"
        self.estado_atual: str = self.estado_base
        self.intensidade: int = 0
        self.causa: str = "Estado inicial de equilíbrio."

    def influenciar(self, novo_estado: str, intensidade_evento: int, causa_evento: str):
        """
        Altera o humor da Shaula com base num evento.
        Apenas eventos com intensidade igual ou maior que a atual podem mudar o estado.
        """
        if intensidade_evento >= self.intensidade:
            self.estado_atual = novo_estado
            self.intensidade = min(10, intensidade_evento) # Limita a intensidade a 10
            self.causa = causa_evento
        else:
            # Se o evento for mais fraco, ele apenas influencia a "causa" sem mudar o estado
            self.causa = f"Levemente influenciada por '{causa_evento}' enquanto se sentia '{self.estado_atual}'."

    def decaimento(self):
        """
        Simula a passagem do tempo, fazendo o humor voltar gradualmente ao estado base.
        O decaimento é mais rápido para humores muito intensos.
        """
        if self.intensidade > 0:
            taxa = self.DECAIMENTO_ACELERADO if self.intensidade > 7 else self.DECAIMENTO_NORMAL
            self.intensidade -= taxa
        
        # Se a intensidade chegar a zero, volta ao estado base de equilíbrio
        if self.intensidade <= 0:
            self.intensidade = 0
            if self.estado_atual != self.estado_base:
                self.estado_atual = self.estado_base
                self.causa = "Retorno ao equilíbrio."

    def obter_estado_para_prompt(self) -> Dict:
        """Retorna um dicionário simples para ser injetado no prompt da personalidade."""
        # Apenas reporta o humor se ele for significativo (intensidade > 2)
        if self.intensidade > 2:
            return {"estado": self.estado_atual, "intensidade": self.intensidade}
        return {}

    def para_dict(self) -> Dict:
        """Serializa o objeto Humor para um dicionário."""
        return self.__dict__

    @staticmethod
    def de_dict(data: Dict):
        """Cria uma instância de Humor a partir de um dicionário."""
        h = Humor()
        h.estado_base = data.get('estado_base', 'Serena')
        h.estado_atual = data.get('estado_atual', h.estado_base)
        h.intensidade = data.get('intensidade', 0)
        h.causa = data.get('causa', 'Estado inicial.')
        return h