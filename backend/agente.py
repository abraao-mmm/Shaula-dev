# backend/agente.py (VERSÃO 100% COMPLETA E FINAL)

import json
import os
import openai
import pandas as pd
from typing import Callable, Dict, Tuple, Optional
from rich.console import Console
from rich.panel import Panel
from rich.markup import escape

# --- Importações Relativas do Pacote 'backend' ---
from .estado_agora import EstadoAgora
from .memoria import Memoria
from .personalidade import Personalidade
from .usuario import Usuario
from .gerenciador_usuarios import GerenciadorDeUsuarios
from .mundo_interior import MundoInterior
from .humor import Humor
from .processador_cognitivo import ProcessadorCognitivo
from .analisador_de_intencao import identificar_intencao
from .analisador_de_dados import AnalisadorDeDados

class AgenteReflexivo:
    """
    O cérebro principal da Shaula. Gere a interação em tempo real,
    mantém o estado interno, classifica a intenção do utilizador e delega
    as tarefas para os módulos corretos.
    """
    def __init__(self, usuario_atual: Usuario, gerenciador: GerenciadorDeUsuarios, console_log: Console):
        self.usuario_atual = usuario_atual
        self.gerenciador_de_usuarios = gerenciador
        self.console = console_log
        self.memoria = Memoria()
        self.personalidade = Personalidade()
        self.mundo_interior = MundoInterior()
        self.humor = Humor()
        
        self.fadiga_cognitiva: int = 0
        self.sonhos_passados: list = []
        self.memoria_inicial_count: int = 0
        
        self.sessao_de_analise: Optional[AnalisadorDeDados] = None
        self.estado_da_analise: str = "inativo"
        self.contexto_analise_pendente: Dict = {}
        
        self.prompts_analise: Dict[str, str] = {}
        self._carregar_prompts_de_analise()

        self.processador_cognitivo = ProcessadorCognitivo(self)
        self._inicializar_estado()
        
    def obter_resposta_llm(self, prompt: str, modo: str = "Criatividade", stream: bool = False, schema: dict = None, imagem_base64: str = None) -> Dict:
        """Centraliza todas as chamadas à API da OpenAI."""
        self.console.print(f"\n[dim][Conectando à OpenAI... Núcleo de '{modo}' ativado...][/dim]")
        MODELO_USADO = "gpt-4o"
        try:
            client = openai.OpenAI()
            if imagem_base64:
                mensagens = [{"role": "user","content": [{"type": "text", "text": prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{imagem_base64}"}}]}]
                stream = False 
            else:
                mensagens = [{"role": "user", "content": prompt}]
            kwargs = {"model": MODELO_USADO, "messages": mensagens, "temperature": 0.7, "max_tokens": 2048, "stream": stream}
            if schema:
                kwargs["response_format"] = {"type": "json_object"}
                mensagens.insert(0, {"role": "system", "content": "You are a helpful assistant designed to output JSON."})
            
            response = client.chat.completions.create(**kwargs)
            conteudo = response.choices[0].message.content.strip()
            return {"tipo": "texto", "conteudo": conteudo}
        except Exception as e:
            self.console.print(f"❌ [bold red]Erro na chamada da API da OpenAI: {e}[/bold red]")
            return {"tipo": "erro", "conteudo": "{}" if schema else f"Ocorreu um erro: {e}"}

    def _carregar_prompts_de_analise(self):
        """Carrega os prompts genéricos que guiam a análise de dados."""
        self.console.log("A carregar prompts de análise de dados...")
        # (Cola os teus 4 prompts genéricos aqui)
        self.prompts_analise = { "passo_1_avaliacao_inicial": """
Você é uma cientista de dados Sênior e especialista em análise exploratória. Acabou de receber um novo dataset para um projeto. O seu objetivo é prever a coluna '{nome_da_coluna_alvo}'.

**Contexto:**
Abaixo estão os resultados dos comandos `.info()` e `.describe()` executados no dataset.

**Resultado do `.info()`:**
{resultado_info}


**Resultado do `.describe()`:**
{resultado_describe}


**Tarefa de Análise Crítica:**
Com base **apenas** nestas informações, forneça uma avaliação inicial completa e estruturada:

1.  **Tipo de Problema:** Esta é uma tarefa de **Regressão** ou **Classificação**? Justifique a sua resposta com base na natureza (tipo de dado, número de valores únicos) da coluna-alvo '{nome_da_coluna_alvo}'.

2.  **Qualidade dos Dados (Primeira Impressão):** Identifique os 3 principais desafios de pré-processamento que você prevê. Foque em:
    * **Dados Ausentes:** Quais colunas têm valores nulos e isso parece ser um problema significativo?
    * **Tipos de Dados:** Existem colunas que precisam de conversão (ex: 'Object' para data ou número)?
    * **Escalas Numéricas:** As colunas numéricas parecem ter escalas muito diferentes (ex: uma vai de 0 a 1 e outra de 0 a 1.000.000)?
    * **Cardinalidade Categórica:** Existem colunas de texto? Se sim, parecem ter muitas categorias únicas?

3.  **Hipótese Inicial:** Qual a sua primeira hipótese sobre o que será mais desafiador neste projeto (ex: "o feature engineering será complexo devido à falta de preditores óbvios", ou "a limpeza de dados será a fase mais demorada devido à quantidade de valores ausentes").

4.  **Sugestão de Próximo Passo:** Confirme que o próximo passo lógico é uma Análise Exploratória de Dados (AED) mais profunda para visualizar as distribuições e correlações.
""",

            "passo_2_plano_aed": """
Shaula, agora que temos a avaliação inicial, a tua tarefa é delinear um plano de ação para a Análise Exploratória de Dados (AED).

**Contexto:**
- O nosso problema é de **{tipo_de_problema}**.
- A nossa variável-alvo é **'{nome_da_coluna_alvo}'**.
- As colunas numéricas candidatas a preditores são: {lista_de_colunas_numericas}.
- As colunas categóricas candidatas a preditores são: {lista_de_colunas_categoricas}.

**Tarefa: Criar um Plano de AED**
Descreve, passo a passo, o plano que seguirias. Para cada passo, especifica qual a tua principal pergunta e que tipo de gráfico usarias para a responder. O teu plano deve cobrir:

1.  **Análise da Variável-Alvo:** Como investigarias a distribuição da coluna '{nome_da_coluna_alvo}'? Que problema específico (ex: assimetria, desbalanceamento de classes) estás a procurar?

2.  **Análise de Preditores Numéricos:** Como investigarias a relação entre as features numéricas e a variável-alvo? Qual é a ferramenta estatística principal que usarias?

3.  **Análise de Preditores Categóricos:** Como investigarias a relação entre as features categóricas e a variável-alvo? Que tipo de visualização seria mais eficaz?

4.  **Conclusão e Próximo Passo:** Com base neste plano, qual é o *insight* mais importante que esperas obter da AED?""",

            "passo_3_estrategia_pipeline": """
Shaula, a Análise Exploratória de Dados foi concluída. Agora, a tua tarefa como Engenheira de Machine Learning é projetar um pipeline de pré-processamento robusto e completo com o Scikit-Learn.

**Contexto (Achados da AED):**
- {resumo_dos_achados_da_aed} 
(Ex: "A variável-alvo está altamente desbalanceada. As features numéricas 'A' e 'B' têm uma distribuição assimétrica. A feature categórica 'C' tem 5% de valores ausentes.")

**Tarefa: Projetar o Pipeline de Pré-processamento**
Descreve, de forma estruturada, o teu plano para construir um `ColumnTransformer` que prepare os dados para o modelo. Justifica cada escolha.

1.  **Estratégia de Divisão de Dados:** Como dividirias os dados em treino e teste? Que parâmetro específico usarias na função `train_test_split` para lidar com o desbalanceamento que encontrámos?

2.  **Pipeline para Features Numéricas:** Descreve a sequência de etapas (transformadores do Scikit-Learn) que aplicarias a todas as colunas numéricas.

3.  **Pipeline para Features Categóricas:** Descreve a sequência de etapas que aplicarias a todas as colunas categóricas.

4.  **Tratamentos Especiais (Se necessário):** Com base nos achados da AED, propões algum tratamento especial para colunas específicas (ex: uma transformação logarítmica para as colunas assimétricas)? Como integrarias isso no pipeline?""",
           
            "passo_4_analise_performance": """
Shaula, executámos o pipeline e treinámos um modelo de baseline ({nome_do_modelo}) para a nossa tarefa de {tipo_de_problema}. A tua tarefa final é realizar uma análise crítica e profunda da sua performance.

**Contexto (Resultados do Modelo):**

**Matriz de Confusão:**
{matriz_de_confusao}


**Relatório de Classificação:**
{relatorio_de_classificacao}


**Tarefa: Análise Crítica e Sugestão Estratégica**
Fornece uma análise completa dos resultados:

1.  **Interpretação das Métricas:** Explica o que as métricas (Precision, Recall, F1-Score) para cada classe significam no contexto do nosso problema. Qual métrica consideras a mais importante aqui e porquê?

2.  **Análise dos Erros:** Com base na Matriz de Confusão, qual é o tipo de erro mais comum que o modelo está a cometer (Falsos Positivos ou Falsos Negativos)? Qual é o impacto disso no problema de negócio?

3.  **Conclusão Geral:** Este modelo de baseline é "bom" o suficiente? Ele resolve o problema principal? Justifica.

4.  **Sugestão Estratégica:** Com base nesta análise, qual é a tua recomendação para o **próximo passo**? ex: "tentar um modelo mais complexo", "focar em feature engineering", "usar técnicas de reamostragem como SMOTE para tratar o desbalanceamento", etc.).
""" }

    # Em backend/agente.py

    def processar_entrada_do_utilizador(self, entrada_usuario: str) -> Tuple[Optional[str], Optional[str]]:
        """Ponto de entrada principal. Roteia a ação com base no estado da análise."""
        
        comandos_continuar = ["ok", "continua", "pode continuar", "proximo", "sim", "entendi, continua"]

        # --- NOVA MÁQUINA DE ESTADOS INTELIGENTE ---
        
        # Estado 1: O Agente está à espera do nome da coluna-alvo.
        if self.estado_da_analise == "aguardando_alvo":
            return self._confirmar_alvo_e_iniciar(entrada_usuario)
        
        # Estado 2: O Agente apresentou um resultado e está 'em discussão'.
        elif self.estado_da_analise == "em_discussao":
            # Verifica se o utilizador quer continuar o fluxo principal.
            if any(cmd in entrada_usuario.lower() for cmd in comandos_continuar):
                return self.sessao_de_analise.continuar_fluxo(entrada_usuario)
            else:
                # Se não for um comando para continuar, é uma pergunta sobre a análise.
                # Trata como uma conversa normal, MAS adicionando o contexto da última análise.
                self.console.log("Utilizador fez uma pergunta de seguimento sobre a análise...")
                contexto = self.contexto_analise_pendente.get('ultimo_resultado', 'sobre a análise de dados atual')
                prompt_contextual = f"Contexto da nossa análise: {contexto}. Pergunta do utilizador sobre este contexto: {entrada_usuario}"
                return self._processar_conversa_normal(prompt_contextual)
        
        # Estado 3: O Agente está inativo, à espera de uma nova instrução.
        self.console.log("A iniciar análise de intenção...")
        analise_intencao = identificar_intencao(entrada_usuario, self.obter_resposta_llm)
        intencao = analise_intencao.get("intencao", "conversa_geral")
        dataset_mencionado = analise_intencao.get("dataset_mencionado")
        raciocinio_log = f"1. Intenção detetada: '{intencao}'."

        if intencao == "analise_de_dados":
            return self._localizar_e_confirmar_dataset(dataset_mencionado)
        else:
            return self._processar_conversa_normal(entrada_usuario)
        

    def _localizar_e_confirmar_dataset(self, nome_curto: Optional[str]) -> Tuple[str, str]:
        """Procura por datasets e pede ao utilizador para definir o alvo."""
        self.console.print(f"[cyan]Recebi um pedido de análise para '{nome_curto}'... A procurar...[/cyan]")
        
        DATA_ROOT = 'data/'
        try:
            datasets_disponiveis = [d.name for d in os.scandir(DATA_ROOT) if d.is_dir()]
        except FileNotFoundError:
            return self._formata_resposta_direta("Erro: A minha pasta 'data/' não foi encontrada."), "Erro de diretório"

        if not nome_curto:
            resposta_texto = f"Detetei que queres analisar dados. Os que eu tenho são:\n- " + "\n- ".join(datasets_disponiveis) + "\n\nQual deles gostarias de analisar?"
            return self._formata_resposta_direta(resposta_texto), "Ambiguidade de dataset"

        matches = [d for d in datasets_disponiveis if nome_curto in d.lower()]

        if len(matches) == 1:
            dataset_encontrado = matches[0]
            try:
                caminho_dataset = os.path.join(DATA_ROOT, dataset_encontrado)
                ficheiros_csv = [f for f in os.listdir(caminho_dataset) if f.endswith('.csv')]
                if not ficheiros_csv: raise FileNotFoundError("Nenhum CSV encontrado na pasta.")
                
                caminho_csv_principal = os.path.join(caminho_dataset, ficheiros_csv[0])
                df_temp = pd.read_csv(caminho_csv_principal)
                colunas = df_temp.columns.tolist()

                self.estado_da_analise = "aguardando_alvo"
                self.contexto_analise_pendente = {"caminho_csv": caminho_csv_principal}

                resposta_texto = f"Ótimo! Encontrei o dataset '{dataset_encontrado}'. Para começar, qual coluna queres que eu tente prever? As colunas disponíveis são:\n\n{colunas}"
                return self._formata_resposta_direta(resposta_texto), "Aguardando coluna-alvo"
            except Exception as e:
                return self._formata_resposta_direta(f"Encontrei a pasta '{dataset_encontrado}', mas tive um problema ao ler os ficheiros. Erro: {e}"), "Erro de leitura"
        
        else: # Lida com múltiplos matches ou nenhum
            return self._formata_resposta_direta(f"Não encontrei um dataset correspondente a '{nome_curto}'."), "Dataset não encontrado"

    def _confirmar_alvo_e_iniciar(self, nome_coluna_alvo: str) -> Tuple[str, str]:
        """Recebe a coluna-alvo, inicia o AnalisadorDeDados e começa o fluxo."""
        caminho_csv = self.contexto_analise_pendente.get("caminho_csv")
        if not caminho_csv:
            self.estado_da_analise = "inativo"
            return self._formata_resposta_direta("Ocorreu um erro de contexto."), "Erro de contexto"

        try:
            df = pd.read_csv(caminho_csv)
            if nome_coluna_alvo not in df.columns:
                return self._formata_resposta_direta(f"A coluna '{nome_coluna_alvo}' não existe. Tenta de novo."), "Coluna-alvo inválida"

            self.console.print(f"[cyan]Alvo confirmado: '{nome_coluna_alvo}'. A iniciar a sessão de análise...[/cyan]")
            self.sessao_de_analise = AnalisadorDeDados(self, dataframe=df, coluna_alvo=nome_coluna_alvo)
            
            self.estado_da_analise = "em_discussao" 
            self.contexto_analise_pendente = {}

            return self.sessao_de_analise.iniciar_fluxo()

        except Exception as e:
            self.estado_da_analise = "inativo"
            return self._formata_resposta_direta(f"Ocorreu um erro ao carregar o dataset. Erro: {e}"), "Erro fatal"
            
    def _processar_conversa_normal(self, entrada_usuario: str) -> Tuple[Optional[str], Optional[str]]:
        self._log("Iniciando fluxo de raciocínio para conversa normal...")
        estado = EstadoAgora("Conversa reativa", "...", "...", entrada_usuario, self.usuario_atual.id)
        self.memoria.registrar_estado(estado)
        prompt_persona = self.personalidade.gerar_descricao_persona_dinamica(self.usuario_atual)
        prompt_final = f"{prompt_persona}\n\n### TAREFA IMEDIATA\n- {self.usuario_atual.nome} disse: '{escape(entrada_usuario)}'"
        resposta_dict = self.obter_resposta_llm(prompt_final)
        texto_final = resposta_dict.get("conteudo", "Não consegui responder.")
        return self._formata_resposta_direta(texto_final), "Fluxo de conversa normal concluído."

    def _formata_resposta_direta(self, texto: str) -> str:
        return json.dumps({"ferramenta": "resposta_direta_streaming", "parametros": {"texto_final": texto}})

    def _log(self, mensagem: str, tipo: str = "dim"):
        self.console.print(f"[{tipo}]{mensagem}[/{tipo}]")

    def _inicializar_estado(self):
        self.carregar_memoria()
        self.memoria_inicial_count = len(self.memoria.estados)
        self._log(f"Estado inicializado para {self.usuario_atual.nome}. Memória com {self.memoria_inicial_count} registos.")

    def executar_analise_de_sessao(self):
        self.processador_cognitivo.executar_analise_de_sessao(self.obter_resposta_llm)

    def _atualizar_fadiga(self, custo: int):
        self.fadiga_cognitiva = max(0, self.fadiga_cognitiva + custo)
        self._log(f"Fadiga alterada em {custo}. Nível atual: {self.fadiga_cognitiva}", "red")

    def carregar_memoria(self, caminho="data/memoria_log.json"):
        self.memoria.carregar_de_json(caminho)
    
    def salvar_memoria(self, caminho="data/memoria_log.json"):
        self.memoria.exportar_para_json(caminho)