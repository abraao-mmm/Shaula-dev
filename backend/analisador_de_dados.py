# backend/analisador_de_dados.py (VERSÃO FINAL COM GERAÇÃO DE RELATÓRIO CORRIGIDA)

import os
import io
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import nbformat as nbf
from typing import TYPE_CHECKING, Tuple, Optional, Any

# Importações de Machine Learning
from sklearn.model_selection import train_test_split, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report

if TYPE_CHECKING:
    from .agente import AgenteReflexivo

class AnalisadorDeDados:
    """
    Orquestra um fluxo de trabalho de análise de dados genérico e autônomo,
    gerando um relatório em Jupyter Notebook de forma progressiva.
    """
    def __init__(self, agente: 'AgenteReflexivo', dataframe: pd.DataFrame, coluna_alvo: str):
        self.agente = agente
        self.console = self.agente.console
        self.passo_atual = 0
        
        self.df = dataframe
        self.coluna_alvo = coluna_alvo
        
        self.prompts = self.agente.prompts_analise
        self.caminho_relatorio = "exploracao/Relatorio_Gerado_pela_Shaula.ipynb"
        
        # Inicia um novo notebook em memória
        self.notebook = nbf.v4.new_notebook()
        self._adicionar_celula_markdown(f"# Relatório de Análise e Treinamento - Gerado por Shaula\n\n**Dataset:** Análise do dataset fornecido.\n**Objetivo:** Prever a coluna `{self.coluna_alvo}`.")
        self._adicionar_celula_codigo("# Célula de Configuração\nimport pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport seaborn as sns\n\nsns.set_style('whitegrid')\n\n# Simulação do carregamento de dados para o notebook ser autocontido\n# df = pd.read_csv('caminho/para/seus/dados.csv')")
        
        self.console.log("Analisador de Dados com gerador de relatório inicializado.")
        # Salva a versão inicial do relatório, como sugeriste
        self._salvar_relatorio()

    def _adicionar_celula_markdown(self, texto: str):
        """Adiciona uma célula de texto (Markdown) ao relatório."""
        self.notebook['cells'].append(nbf.v4.new_markdown_cell(texto))

    def _adicionar_celula_codigo(self, codigo: str):
        """Adiciona uma célula de código ao relatório."""
        self.notebook['cells'].append(nbf.v4.new_code_cell(codigo))

    def _salvar_relatorio(self):
        """Salva o estado atual do notebook em memória para o ficheiro .ipynb."""
        os.makedirs(os.path.dirname(self.caminho_relatorio), exist_ok=True)
        with open(self.caminho_relatorio, 'w', encoding='utf-8') as f:
            nbf.write(self.notebook, f)
        self.console.log(f"[bold green]Relatório salvo/atualizado com {len(self.notebook['cells'])} células em '{self.caminho_relatorio}'[/bold green]")

    def iniciar_fluxo(self) -> Tuple[str, str]:
        """Começa o fluxo de análise para o dataset fornecido."""
        prompt_confirmacao = f"Entendido. Recebi o dataset e o teu objetivo é prever '{self.coluna_alvo}'. O relatório inicial foi criado em '{self.caminho_relatorio}'. Para confirmar e começar a análise, diz 'sim'."
        return self._formata_resposta(prompt_confirmacao), "Aguardando confirmação"

    def continuar_fluxo(self, entrada_usuario: str) -> Tuple[str, str]:
        """Continua o fluxo após a confirmação do utilizador."""
        confirmacoes = ["sim", "pode começar", "ok", "proximo", "continua", "pode continuar"]
        if any(palavra in entrada_usuario.lower() for palavra in confirmacoes):
            self.passo_atual += 1
            return self.executar_passo(self.passo_atual)
        else:
            self.agente.sessao_de_analise = None
            self._salvar_relatorio()
            return self._formata_resposta("Sessão de análise cancelada. O relatório final foi salvo."), "Análise cancelada."

    def executar_passo(self, passo: int) -> Tuple[str, str]:
        """Router que chama o método correspondente à etapa atual do fluxo."""
        try:
            if passo == 1:
                return self._executar_passo_1_avaliacao_inicial()
            elif passo == 2:
                return self._executar_passo_2_aed_e_graficos()
            elif passo == 3:
                return self._executar_passo_3_pipeline()
            elif passo == 4:
                return self._executar_passo_4_baseline()
            else:
                self.agente.sessao_de_analise = None
                self._salvar_relatorio()
                return self._formata_resposta("Análise concluída! O teu relatório em Jupyter Notebook foi finalizado."), "Fim do fluxo."
        except Exception as e:
            self.console.print(f"[bold red]Erro ao executar o passo {passo}: {e}[/bold red]")
            self.agente.sessao_de_analise = None
            self._salvar_relatorio()
            return self._formata_resposta(f"Ocorreu um erro na etapa {passo}. A sessão foi encerrada, mas o relatório parcial foi salvo."), f"Erro no Passo {passo}"

    def _executar_passo_1_avaliacao_inicial(self) -> Tuple[str, str]:
        self.console.log("Executando Passo 1: Avaliação Inicial...")
        self._adicionar_celula_markdown("## Passo 1: Avaliação Inicial do Dataset")
        codigo = "df.info()\ndisplay(df.describe(include='all').round(2))"
        self._adicionar_celula_codigo(codigo)
        
        buffer = io.StringIO()
        self.df.info(buf=buffer)
        resultado_info = buffer.getvalue()
        resultado_describe = self.df.describe(include='all').to_string()
        
        prompt_formatado = self.prompts["passo_1_avaliacao_inicial"].format(nome_da_coluna_alvo=self.coluna_alvo, resultado_info=resultado_info, resultado_describe=resultado_describe)
        resposta_dict = self.agente.obter_resposta_llm(prompt_formatado, modo="Análise - Passo 1")
        resultado_analise = resposta_dict.get("conteudo", "")
        
        self._adicionar_celula_markdown(f"### Análise da Shaula (Passo 1)\n\n{resultado_analise}")
        self._salvar_relatorio()
        
        resposta_final = f"**Passo 1 Concluído**\n\n{resultado_analise}\n\n---\nO relatório foi atualizado. Posso avançar para a Análise Exploratória e gerar os gráficos?"
        return self._formata_resposta(resposta_final), "Passo 1 concluído."

    def _executar_passo_2_aed_e_graficos(self) -> Tuple[str, str]:
        self.console.log("Executando Passo 2: AED e Geração de Gráficos...")
        self._adicionar_celula_markdown("## Passo 2: Análise Exploratória de Dados (AED)")
        
        caminho_grafico = "exploracao/grafico_distribuicao_alvo.png"
        codigo_grafico = f"plt.figure(figsize=(10, 6))\nsns.countplot(x='{self.coluna_alvo}', data=df, palette='viridis', order=df['{self.coluna_alvo}'].value_counts().index)\nplt.title('Distribuição da Variável-Alvo ({self.coluna_alvo})')\nplt.savefig('{caminho_grafico}')\nplt.show()"
        self._adicionar_celula_codigo(codigo_grafico)
        
        plt.figure(figsize=(10, 6))
        sns.countplot(x=self.coluna_alvo, data=self.df, palette='viridis', order=self.df[self.coluna_alvo].value_counts().index)
        plt.savefig(caminho_grafico)
        plt.close()
        
        # (Aqui adicionarias o código para gerar e salvar outros gráficos)

        prompt_formatado = self.prompts["passo_2_plano_aed"].format(tipo_de_problema="Classificação", nome_da_coluna_alvo=self.coluna_alvo, lista_de_colunas_numericas=self.df.select_dtypes(include=np.number).columns.tolist(), lista_de_colunas_categoricas=self.df.select_dtypes(include=['object']).columns.tolist())
        resposta_dict = self.agente.obter_resposta_llm(prompt_formatado, modo="Análise - Passo 2")
        resultado_analise = resposta_dict.get("conteudo", "")
        
        self._adicionar_celula_markdown(f"### Análise da Shaula (Passo 2)\n\n{resultado_analise}")
        self._salvar_relatorio()
        
        resposta_final = f"**Passo 2 Concluído**\n\n{resultado_analise}\n\n---\nO relatório foi atualizado. Concordas com este plano? Posso delinear a estratégia de pré-processamento?"
        return self._formata_resposta(resposta_final), "Passo 2 concluído."
    
    def _executar_passo_3_pipeline(self) -> Tuple[str, str]:
        self.console.log("Executando Passo 3: Delineamento do Pipeline...")
        self._adicionar_celula_markdown("## Passo 3: Estratégia de Pré-processamento e Pipeline")
        
        prompt_formatado = self.prompts["passo_3_estrategia_pipeline"].format(resumo_dos_achados_da_aed="A AED revelou que a variável-alvo é desbalanceada.")
        resposta_dict = self.agente.obter_resposta_llm(prompt_formatado, modo="Análise - Passo 3")
        resultado_analise = resposta_dict.get("conteudo", "")
        
        self._adicionar_celula_markdown(f"### Análise da Shaula (Passo 3)\n\n{resultado_analise}")
        self._salvar_relatorio()

        resposta_final = f"**Passo 3 Concluído**\n\n{resultado_analise}\n\n---\nEste é o plano de pré-processamento. Posso executar o treinamento do modelo de baseline?"
        return self._formata_resposta(resposta_final), "Passo 3 concluído."

    # Em backend/analisador_de_dados.py

    def _executar_passo_4_baseline(self) -> Tuple[str, str]:
        self.console.log("Executando Passo 4: Treinamento e Reflexão da Baseline...")
        self._adicionar_celula_markdown("## Passo 4: Treinamento do Modelo de Baseline e Avaliação")
        
        try:
            df_model = self.df.copy()

            # --- CORREÇÃO E MELHORIA AQUI ---
            # Remove colunas não informativas que o utilizador identificou
            colunas_para_remover = [col for col in ['id', 'Unnamed: 32'] if col in df_model.columns]
            if colunas_para_remover:
                df_model.drop(columns=colunas_para_remover, inplace=True)
                self.console.log(f"Colunas removidas da análise: {colunas_para_remover}")

            # Lógica inteligente para binarizar a variável-alvo
            y_raw = df_model[self.coluna_alvo]
            if pd.api.types.is_numeric_dtype(y_raw):
                # Se for numérica (como review_score), usa o limiar
                df_model['target_binary'] = (y_raw >= 4).astype(int)
            else:
                # Se for categórica (como diagnosis), mapeia as classes
                # Assume a primeira categoria única como a classe positiva (1)
                positive_class = y_raw.unique()[0]
                self.console.log(f"A tratar a classe '{positive_class}' como a classe positiva (1).")
                df_model['target_binary'] = y_raw.apply(lambda x: 1 if x == positive_class else 0)

            y = df_model['target_binary']
            X = df_model.drop(columns=[self.coluna_alvo, 'target_binary'])
            
            # (O resto do código de treinamento continua igual...)
            features_numericas = X.select_dtypes(include=np.number).columns
            features_categoricas = X.select_dtypes(include=['object', 'category']).columns
            pipeline_numerico = Pipeline(steps=[('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler())])
            pipeline_categorico = Pipeline(steps=[('imputer', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore'))])
            preprocessor = ColumnTransformer(transformers=[('num', pipeline_numerico, features_numericas), ('cat', pipeline_categorico, features_categoricas)])
            modelo_pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('classifier', LogisticRegression(random_state=42, class_weight='balanced'))])
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
            y_train_pred = cross_val_predict(modelo_pipeline, X_train, y_train, cv=3)
            report = classification_report(y_train, y_train_pred, target_names=['Negativa (0)', 'Positiva (1)'], zero_division=0)
            conf_matrix = confusion_matrix(y_train, y_train_pred)
            self.console.log("Modelo de baseline treinado e avaliado com sucesso.")
            # --- FIM DO BLOCO DE TREINAMENTO ---

        except Exception as e:
            # Se ocorrer um erro aqui, ele será capturado e reportado
            raise e

        prompt_formatado = self.prompts["passo_4_analise_performance"].format(nome_do_modelo="Regressão Logística", tipo_de_problema="Classificação", matriz_de_confusao=str(conf_matrix), relatorio_de_classificacao=report)
        resposta_dict = self.agente.obter_resposta_llm(prompt_formatado, modo="Análise - Passo 4")
        resultado_analise = resposta_dict.get("conteudo", "")
        
        self.agente.contexto_analise_pendente['ultimo_resultado'] = resultado_analise # Guarda o contexto para discussão
        self._adicionar_celula_markdown(f"### Análise da Shaula (Passo 4)\n\n{resultado_analise}")
        self._salvar_relatorio()
        
        resposta_final = f"**Passo 4 Concluído**\n\n{resultado_analise}\n\n---\nA sessão de análise está terminada. O relatório final foi salvo."
        return self._formata_resposta(resposta_final), "Passo 4 concluído."

    def _formata_resposta(self, texto: str) -> str:
        prompt_para_llm = f"Você é a Shaula. Reformule a seguinte informação de forma conversacional e clara para o seu utilizador, Abraão:\n\n'{texto}'"
        return json.dumps({"ferramenta": "resposta_direta_streaming", "parametros": {"prompt": prompt_para_llm}})