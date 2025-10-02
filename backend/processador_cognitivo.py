# backend/processador_cognitivo.py

import json
import datetime
from typing import TYPE_CHECKING, Callable

from rich.panel import Panel
from rich.markup import escape

# --- Importações Relativas Corrigidas ---
from .memoria import Memoria
from .mundo_interior import MundoInterior
from .ruminacao import MotorDeRuminacao
from .meta_reflexao import RevisorDeMemoria
from .autocompaixao import MotorDeAutocompaixao
from .memoria_teatral import encenar_memoria
from .calibrador_dialogo import analisar_equilibrio_conversacional
# Assumindo que estes ficheiros também estão no backend
# Se não estiverem, terás de ajustar o caminho ou criá-los.
# from .analisador_de_estilo import extrair_metafora 

# Type hinting para evitar importação circular com 'agente.py'
if TYPE_CHECKING:
    from .agente import AgenteReflexivo

class ProcessadorCognitivo:
    """
    Encapsula os processos cognitivos de 'background' da Shaula.
    Funciona como o 'subconsciente', lidando com a reflexão, análise de sessão
    e outras tarefas que não precisam de ser executadas em tempo real.
    """
    def __init__(self, agente: 'AgenteReflexivo'):
        """
        Inicializa o processador cognitivo com uma referência ao agente principal.
        """
        # Referência ao agente para aceder aos seus componentes
        self.agente = agente
        self.console = agente.console
        self.memoria = agente.memoria
        self.mundo_interior = agente.mundo_interior
        self.usuario_atual = agente.usuario_atual
        
        # Instancia os motores cognitivos que este processador irá orquestrar
        self.ruminacao_engine = MotorDeRuminacao()
        self.revisor_memoria = RevisorDeMemoria()
        self.autocompaixao_engine = MotorDeAutocompaixao()

    def _registrar_crise_existencial(self, tipo_crise: str, texto_original: str, texto_modulado: str):
        """Regista um log de uma crise/reflexão significativa."""
        crise = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_id": self.usuario_atual.id,
            "tipo_crise": tipo_crise,
            "pensamento_original": texto_original,
            "pensamento_modulado": texto_modulado
        }
        try:
            with open("data/crises_log.json", "a", encoding="utf-8") as f:
                f.write(json.dumps(crise, ensure_ascii=False) + "\n")
            self.agente._log("LOG: Crise existencial registrada.", "dim")
        except Exception as e:
            self.console.print(f"[bold red]Erro ao salvar crise existencial: {e}[/bold red]")
        
        # Influencia o humor da Shaula
        self.agente.humor.influenciar("Inquieta", 8, f"Crise sobre '{tipo_crise}'")

    def executar_analise_de_sessao(self, obter_resposta_llm_func: Callable):
        """
        Executa a ruminação de curto prazo sobre a sessão de conversa que acabou de terminar.
        """
        self.agente._atualizar_fadiga(custo=3)
        estados_da_sessao = [e for e in self.memoria.estados[self.agente.memoria_inicial_count:] if e.user_id == self.usuario_atual.id]
        
        if not estados_da_sessao:
            self.console.print(Panel(f"[yellow]Nenhuma nova interação com {self.usuario_atual.nome} nesta sessão para analisar.[/yellow]", title="Aviso de Ruminação"))
            return

        self.console.print(Panel(f"[bold yellow]Analisando a sessão com {self.usuario_atual.nome}...[/bold yellow]", title="[yellow] Fim de Sessão: Ruminação", border_style="yellow"))
        
        # 1. Gera a análise bruta da sessão
        resultado_bruto = self.ruminacao_engine.analisar_sessao(estados_da_sessao, obter_resposta_llm_func, self.usuario_atual.id, self.usuario_atual.nome)
        
        # 2. Passa a análise pelo filtro de autocompaixão
        resultado_final = self.autocompaixao_engine.analisar_e_modular_autocritica(resultado_bruto, obter_resposta_llm_func)
        
        self.console.print(Panel(escape(resultado_final), title=f"[bold yellow]Análise da Sessão (Modulada)[/bold yellow]", border_style="yellow"))

    def executar_meta_reflexao(self, obter_resposta_llm_func: Callable):
        """
        Executa a meta-reflexão de longo prazo ("sonho") sobre a memória.
        """
        self.agente._atualizar_fadiga(custo=5)
        self.console.print(Panel(f"[purple]Shaula está a sonhar sobre a sua relação com {self.usuario_atual.nome}...[/purple]", title="🌙 Sonho Simbólico: Meta-Reflexão", border_style="purple"))
        
        # 1. Gera o "sonho" bruto
        novo_sonho_bruto = self.revisor_memoria.executar_revisao(obter_resposta_llm_func, self.usuario_atual.id, self.usuario_atual.nome)
        
        if novo_sonho_bruto:
            # 2. Passa o sonho pelo filtro de autocompaixão
            novo_sonho_final = self.autocompaixao_engine.analisar_e_modular_autocritica(novo_sonho_bruto, obter_resposta_llm_func)
            
            # Se o sonho foi alterado, significa que houve uma autocrítica que precisou de ser modulada
            if novo_sonho_bruto != novo_sonho_final:
                self._registrar_crise_existencial("Autocrítica no Sonho", novo_sonho_bruto, novo_sonho_final)
            
            self.agente.sonhos_passados.append(novo_sonho_final)
            
            # 3. Persiste o sonho final
            try:
                with open("data/sonhos.json", "a", encoding="utf-8") as f:
                    f.write(json.dumps({"timestamp": datetime.datetime.now().isoformat(), "user_id": self.usuario_atual.id, "sonho": novo_sonho_final}) + "\n")
                self.console.print(Panel(f"**Novo sonho salvo:**\n[dim]{escape(novo_sonho_final)}[/dim]", title="🌙 Sonho Registado!", border_style="green"))
            except Exception as e:
                self.console.print(f"[bold red]Erro ao salvar sonho: {e}[/bold red]")