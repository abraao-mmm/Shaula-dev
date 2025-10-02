# backend/estado_agora.py

from datetime import datetime
from typing import Dict

class EstadoAgora:
    """
    Representa um único "momento" na consciência da Shaula.
    Pode ser uma interação com um utilizador ou um pensamento interno.
    É a unidade fundamental que compõe a sua memória.
    """
    def __init__(self, percepcao_bruta: str, acao_tomada: str, previsao_gerada: str, resultado_real: str, user_id: str):
        """
        Inicializa um novo estado de memória.
        """
        self.timestamp: datetime = datetime.now()
        self.user_id: str = user_id
        
        # O ciclo fundamental: Percepção -> Ação -> Previsão -> Resultado
        self.percepcao_bruta: str = percepcao_bruta
        self.acao_tomada: str = acao_tomada
        self.previsao_gerada: str = previsao_gerada
        self.resultado_real: str = resultado_real
        
        # Atributos adicionais que enriquecem a memória
        self.resposta_shaula: str = ""
        self.reflexao: str = ""
        
        # Metadados da interação (análise da fala do utilizador)
        self.tom_emocional: str = "neutro"
        self.impacto_afetivo: str = "informativo"
        self.tipo_de_interacao: str = "pergunta"
        self.necessita_reconciliacao: bool = False # Alterado para False por defeito

    def para_dict(self) -> Dict:
        """Serializa o objeto EstadoAgora para um dicionário compatível com JSON."""
        # Cria uma cópia do dicionário de atributos do objeto
        d = self.__dict__.copy()
        # Converte o objeto datetime para uma string no formato ISO
        d['timestamp'] = self.timestamp.isoformat()
        return d

    @staticmethod
    def de_dict(data: Dict):
        """Cria uma instância de EstadoAgora a partir de um dicionário."""
        # Cria uma instância base com os valores essenciais
        user_id = data.get("user_id", "default_user")
        estado = EstadoAgora(
            percepcao_bruta=data.get("percepcao_bruta", ""),
            acao_tomada=data.get("acao_tomada", ""),
            previsao_gerada=data.get("previsao_gerada", ""),
            resultado_real=data.get("resultado_real", ""),
            user_id=user_id
        )
        
        # Preenche os restantes atributos a partir do dicionário,
        # usando .get() com valores padrão para garantir que não falha
        # se um registo de memória antigo não tiver um campo.
        try:
            estado.timestamp = datetime.fromisoformat(data["timestamp"])
        except (TypeError, ValueError):
            estado.timestamp = datetime.now() # Fallback

        estado.resposta_shaula = data.get('resposta_shaula', "")
        estado.reflexao = data.get('reflexao', "")
        estado.tom_emocional = data.get('tom_emocional', 'neutro')
        estado.impacto_afetivo = data.get('impacto_afetivo', 'informativo')
        estado.tipo_de_interacao = data.get('tipo_de_interacao', 'pergunta')
        estado.necessita_reconciliacao = data.get('necessita_reconciliacao', False)
        
        return estado