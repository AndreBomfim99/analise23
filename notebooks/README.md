# 📓 Jupyter Notebooks - Olist E-Commerce Analysis

Notebooks interativos para análise exploratória, visualização de dados e documentação de insights do projeto.

---

## 📋 Índice

1. [Visão Geral](#visao-geral)
2. [Lista de Notebooks](#lista-notebooks)
3. [Como Usar](#como-usar)
4. [Estrutura dos Notebooks](#estrutura)
5. [Dependências](#dependencias)
6. [Boas Práticas](#boas-praticas)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral {#visao-geral}

### **Propósito dos Notebooks**

Os notebooks Jupyter servem para:

- 🔍 **Análise Exploratória (EDA):** Entender os dados antes das análises formais
- 📊 **Visualizações Interativas:** Gráficos e dashboards exploratórios
- 🧪 **Prototipagem:** Testar queries e análises antes de colocar em produção
- 📝 **Documentação:** Narrativa visual dos insights encontrados
- 🎓 **Aprendizado:** Material didático sobre as metodologias aplicadas

### **Diferença: Notebooks vs Scripts Python**

| Aspecto | Notebooks (`notebooks/`) | Scripts (`python/`) |
|---------|-------------------------|---------------------|
| **Propósito** | Exploração e documentação | Produção e automação |
| **Formato** | `.ipynb` (interativo) | `.py` (código puro) |
| **Uso** | Ad-hoc, investigativo | ETL, pipelines, testes |
| **Output** | Gráficos + narrativa | Dados processados |
| **Versionamento** | Cuidado (JSON grande) | Git-friendly |

---

## 📚 Lista de Notebooks {#lista-notebooks}

### **Estrutura Recomendada**

```
notebooks/
│
├── 01_exploratory_analysis.ipynb          ⚪ EDA inicial
├── 02_ltv_deep_dive.ipynb                 ⚪ Análise LTV detalhada
├── 03_cohort_retention.ipynb              ⚪ Análise de retenção
├── 04_rfm_segmentation.ipynb              ⚪ Segmentação RFM
├── 05_category_performance.ipynb          ⚪ Performance categorias
├── 06_logistics_analysis.ipynb            ⚪ Análise logística
├── 07_geographic_analysis.ipynb           ⚪ Análise geoespacial
├── 08_seasonality_trends.ipynb            ⚪ Sazonalidade
├── 09_business_insights_summary.ipynb     ⚪ Resumo executivo
│
├── utils/                                  # Funções auxiliares
│   ├── __init__.py
│   ├── plotting.py                         # Funções de plot
│   └── bigquery_helpers.py                 # Helpers BigQuery
│
├── outputs/                                # Outputs dos notebooks
│   ├── figures/                            # Gráficos exportados
│   └── reports/                            # Relatórios HTML
│
└── README.md                               # Este arquivo
```

---

## 📊 Notebooks Detalhados

### **01 - Exploratory Data Analysis (EDA)**

**Arquivo:** `01_exploratory_analysis.ipynb`

**Objetivo:** Primeira exploração dos dados, entender estrutura, qualidade e distribuições.

**Conteúdo:**
- Carregamento de dados do BigQuery
- Estatísticas descritivas (mean, median, std)
- Identificação de missing values
- Detecção de outliers
- Distribuições de variáveis chave (preço, frete, tempo entrega)
- Correlações iniciais
- Validação de integridade referencial

**Principais Outputs:**
- Tabelas de estatísticas descritivas
- Histogramas e boxplots
- Matriz de correlação
- Relatório de qualidade de dados

**Tempo Estimado:** 30-45 minutos

---

### **02 - LTV Deep Dive**

**Arquivo:** `02_ltv_deep_dive.ipynb`

**Objetivo:** Análise profunda de Customer Lifetime Value.

**Conteúdo:**
- Cálculo de LTV por cliente
- Distribuição de LTV (histograma, percentis)
- LTV por estado/região
- LTV por categoria de produto
- LTV por segmento RFM
- Análise LTV vs CAC (ROI)
- Identificação de clientes alto valor
- Curva de Pareto (80/20)

**Principais Outputs:**
- Gráfico de distribuição de LTV
- Mapa geográfico de LTV
- Tabela de top clientes por LTV
- Análise de ROI por segmento

**Tempo Estimado:** 45-60 minutos

---

### **03 - Cohort Retention Analysis**

**Arquivo:** `03_cohort_retention.ipynb`

**Objetivo:** Análise de retenção de clientes ao longo do tempo.

**Conteúdo:**
- Definição de cohorts (mês de primeira compra)
- Cálculo de retenção M1, M2, M3, M6, M12
- Heatmap de retenção
- Curva de retenção
- Comparação entre cohorts
- Identificação de janela crítica de churn
- Benchmarking com mercado

**Principais Outputs:**
- Heatmap de cohort retention
- Gráfico de curva de retenção
- Tabela de taxas de retenção
- Insights sobre churn

**Tempo Estimado:** 45 minutos

---

### **04 - RFM Segmentation**

**Arquivo:** `04_rfm_segmentation.ipynb`

**Objetivo:** Segmentação de clientes usando metodologia RFM.

**Conteúdo:**
- Cálculo de Recency, Frequency, Monetary
- Criação de scores RFM (1-5)
- Definição de 11 segmentos
- Análise de cada segmento (tamanho, LTV, comportamento)
- Visualização 3D de segmentos
- Recomendações de ação por segmento
- Distribuição de clientes por segmento

**Principais Outputs:**
- Gráfico de pizza (distribuição segmentos)
- Scatter plot 3D (R-F-M)
- Tabela de características de cada segmento
- Matriz de ações recomendadas

**Tempo Estimado:** 60 minutos

---

### **05 - Category Performance**

**Arquivo:** `05_category_performance.ipynb`

**Objetivo:** Análise de performance de categorias de produtos.

**Conteúdo:**
- Top 10 categorias por receita
- NPS por categoria
- Crescimento YoY por categoria
- Ticket médio por categoria
- Curva de Pareto de categorias
- Matriz preço vs volume
- Identificação de categorias subestimadas
- Análise de oportunidades

**Principais Outputs:**
- Gráfico de barras (top categorias)
- Matriz 2x2 (preço vs volume)
- Scatter plot (NPS vs receita)
- Tabela de oportunidades

**Tempo Estimado:** 45 minutos

---

### **06 - Logistics Analysis**

**Arquivo:** `06_logistics_analysis.ipynb`

**Objetivo:** Análise de performance logística e entregas.

**Conteúdo:**
- Tempo médio de entrega por região
- SLA compliance rate
- Análise de atrasos
- Correlação atraso vs NPS
- Rotas críticas (seller → customer)
- Análise de frete (custo vs tempo)
- Impacto de atrasos na satisfação
- Identificação de gargalos

**Principais Outputs:**
- Mapa de tempo de entrega por estado
- Gráfico de correlação atraso-NPS
- Tabela de rotas problemáticas
- Heatmap de SLA compliance

**Tempo Estimado:** 45 minutos

---

### **07 - Geographic Analysis**

**Arquivo:** `07_geographic_analysis.ipynb`

**Objetivo:** Análise geoespacial de clientes e vendas.

**Conteúdo:**
- Concentração de clientes por estado
- Receita por estado/cidade
- Top 20 cidades
- Disparidade regional (Sul/Sudeste vs Norte/Nordeste)
- Análise de penetração de mercado
- Oportunidades de expansão geográfica
- Mapas interativos (Folium/Plotly)

**Principais Outputs:**
- Mapa coroplético (receita por estado)
- Gráfico de barras (top cidades)
- Tabela de concentração regional
- Mapa de calor de clientes

**Tempo Estimado:** 30-45 minutos

---

### **08 - Seasonality & Trends**

**Arquivo:** `08_seasonality_trends.ipynb`

**Objetivo:** Análise de sazonalidade e tendências temporais.

**Conteúdo:**
- Vendas por mês (série temporal)
- Crescimento MoM (Month-over-Month)
- Crescimento YoY (Year-over-Year)
- Vendas por dia da semana
- Vendas por hora do dia
- Sazonalidade por categoria (ex: brinquedos no Natal)
- Identificação de picos (Black Friday, Natal)
- Decomposição de séries temporais (trend + seasonality + noise)

**Principais Outputs:**
- Gráfico de linha (vendas mensais)
- Heatmap (dia da semana vs hora)
- Gráfico de sazonalidade por categoria
- Tabela de crescimento

**Tempo Estimado:** 45 minutos

---

### **09 - Business Insights Summary**

**Arquivo:** `09_business_insights_summary.ipynb`

**Objetivo:** Resumo executivo de todos os insights para apresentação.

**Conteúdo:**
- Top 5 descobertas críticas
- Métricas principais (KPIs)
- Recomendações estratégicas
- Impacto financeiro estimado
- Roadmap de ações
- Visualizações chave de cada análise
- Narrativa de storytelling com dados

**Principais Outputs:**
- Dashboard executivo
- Slides de apresentação (export to PDF)
- Relatório HTML para stakeholders
- One-pager de insights

**Tempo Estimado:** 60 minutos (compilação)

---

## 🚀 Como Usar {#como-usar}

### **Pré-requisitos**

```bash
# 1. Instalar Jupyter
pip install jupyter jupyterlab

# 2. Instalar dependências de visualização
pip install matplotlib seaborn plotly folium

# 3. Configurar credenciais GCP
export GOOGLE_APPLICATION_CREDENTIALS="./keys/gcp-key.json"
```

---

### **Iniciar Jupyter**

#### **Opção A: Jupyter Notebook (Clássico)**

```bash
# Iniciar no navegador
jupyter notebook

# Iniciar em pasta específica
jupyter notebook notebooks/

# Iniciar em porta específica
jupyter notebook --port=8889
```

**URL padrão:** http://localhost:8888

---

#### **Opção B: JupyterLab (Moderno - Recomendado)**

```bash
# Iniciar JupyterLab
jupyter lab

# Iniciar em pasta específica
cd notebooks/
jupyter lab
```

**URL padrão:** http://localhost:8888/lab

**Vantagens do JupyterLab:**
- ✅ Interface mais moderna
- ✅ Multi-tabs
- ✅ Terminal integrado
- ✅ File explorer melhor
- ✅ Extensions

---

### **Executar Notebook**

1. **Abrir notebook:** Clique no arquivo `.ipynb`
2. **Executar célula:** `Shift + Enter`
3. **Executar todas:** Menu → Cell → Run All
4. **Reiniciar kernel:** Menu → Kernel → Restart & Clear Output

---

### **Ordem Recomendada de Execução**

```
1º → 01_exploratory_analysis.ipynb      (entender os dados)
2º → 03_cohort_retention.ipynb          (ver retenção)
3º → 04_rfm_segmentation.ipynb          (segmentar clientes)
4º → 02_ltv_deep_dive.ipynb             (calcular valor)
5º → 05_category_performance.ipynb      (produtos)
6º → 06_logistics_analysis.ipynb        (logística)
7º → 07_geographic_analysis.ipynb       (geografia)
8º → 08_seasonality_trends.ipynb        (tempo)
9º → 09_business_insights_summary.ipynb (síntese)
```

---

## 📐 Estrutura Padrão de Notebook {#estrutura}

### **Template Recomendado**

```python
"""
Notebook: [Nome da Análise]
Projeto: Olist E-Commerce Analysis
Autor: Andre Bomfim
Data: Novembro 2024
"""

# =============================================================================
# 1. SETUP & IMPORTS
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from google.cloud import bigquery
import warnings
warnings.filterwarnings('ignore')

# Configurações de visualização
%matplotlib inline
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_rows', 100)

# =============================================================================
# 2. CONEXÃO COM BIGQUERY
# =============================================================================

client = bigquery.Client()
project_id = "seu-projeto"
dataset_id = "olist_ecommerce"

# =============================================================================
# 3. CARREGAMENTO DE DADOS
# =============================================================================

query = """
SELECT * FROM `olist_ecommerce.orders`
LIMIT 1000
"""

df = client.query(query).to_dataframe()
print(f"Dados carregados: {len(df)} linhas, {len(df.columns)} colunas")

# =============================================================================
# 4. ANÁLISE EXPLORATÓRIA
# =============================================================================

# 4.1 Visão geral
df.info()
df.describe()

# 4.2 Visualizações
# ... (seu código de análise)

# =============================================================================
# 5. INSIGHTS E CONCLUSÕES
# =============================================================================

"""
## Principais Descobertas:

1. [Insight 1]
2. [Insight 2]
3. [Insight 3]

## Recomendações:

- [Ação 1]
- [Ação 2]
"""
```

---

## 📦 Dependências {#dependencias}

### **Instalação de Bibliotecas**

```bash
# Análise de dados
pip install pandas numpy scipy

# Visualização
pip install matplotlib seaborn plotly

# BigQuery
pip install google-cloud-bigquery

# Mapas
pip install folium geopandas

# Jupyter
pip install jupyter jupyterlab ipywidgets

# Utilitários
pip install python-dotenv tqdm
```

### **Imports Padrão**

```python
# Data manipulation
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# BigQuery
from google.cloud import bigquery

# Stats
from scipy import stats
from scipy.stats import pearsonr

# Utils
import warnings
warnings.filterwarnings('ignore')
```

---

## ✅ Boas Práticas {#boas-praticas}

### **1. Organização**

✅ **Fazer:**
- Usar seções com títulos claros
- Numerar seções (1, 2, 3...)
- Adicionar docstrings e comentários
- Separar código de markdown (narrativa)

❌ **Evitar:**
- Notebooks muito longos (> 500 linhas)
- Código sem comentários
- Executar células fora de ordem

---

### **2. Versionamento**

✅ **Fazer:**
- Limpar outputs antes de commitar: `jupyter nbconvert --clear-output --inplace *.ipynb`
- Usar `.gitignore` para checkpoints
- Exportar versões finais para HTML/PDF

❌ **Evitar:**
- Commitar com outputs (aumenta diff)
- Commitar credenciais ou dados sensíveis

**Git Hooks:**
```bash
# .git/hooks/pre-commit
jupyter nbconvert --clear-output --inplace notebooks/*.ipynb
```

---

### **3. Performance**

✅ **Fazer:**
- Usar `LIMIT` em queries de teste
- Salvar dados intermediários em CSV
- Usar `%%time` para medir performance
- Reiniciar kernel periodicamente

❌ **Evitar:**
- Carregar datasets gigantes inteiros
- Loops desnecessários
- Recarregar dados a cada célula

---

### **4. Visualizações**

✅ **Fazer:**
- Adicionar títulos, labels, legendas
- Usar cores consistentes
- Exportar gráficos importantes (`.savefig()`)
- Manter resolução alta (dpi=300)

❌ **Evitar:**
- Gráficos sem contexto
- Cores confusas
- Escalas inadequadas

**Exemplo:**
```python
plt.figure(figsize=(12, 6))
plt.plot(x, y, linewidth=2, color='#2E86AB')
plt.title('Título Descritivo', fontsize=14, fontweight='bold')
plt.xlabel('Eixo X', fontsize=12)
plt.ylabel('Eixo Y', fontsize=12)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('outputs/figures/meu_grafico.png', dpi=300, bbox_inches='tight')
plt.show()
```

---

### **5. Markdown e Narrativa**

✅ **Fazer:**
- Explicar **o que** está fazendo
- Explicar **por que** está fazendo
- Adicionar contexto de negócio
- Usar markdown para seções

**Exemplo:**
```markdown
## 3. Análise de Retenção

Nesta seção, vamos calcular a taxa de retenção mensal para entender
quantos clientes retornam após a primeira compra. 

**Por que isso importa?**
- Retenção > 15% é considerada saudável no e-commerce
- Baixa retenção indica problemas de experiência ou fidelização
```

---

## 🐛 Troubleshooting {#troubleshooting}

### **Problema: "Kernel keeps dying"**

**Causas:**
- Memória insuficiente
- Dataset muito grande
- Loop infinito

**Soluções:**
```python
# 1. Reduzir tamanho dos dados
df = df.sample(frac=0.1)  # Usar apenas 10%

# 2. Liberar memória
import gc
del df_grande
gc.collect()

# 3. Reiniciar kernel
# Menu → Kernel → Restart
```

---

### **Problema: "BigQuery authentication failed"**

**Solução:**
```bash
# Verificar variável de ambiente
echo $GOOGLE_APPLICATION_CREDENTIALS

# Ou autenticar via gcloud
gcloud auth application-default login

# Testar conexão
python -c "from google.cloud import bigquery; client = bigquery.Client(); print('OK')"
```

---

### **Problema: Gráficos não aparecem**

**Solução:**
```python
# Adicionar no início do notebook
%matplotlib inline

# Ou usar backend interativo
%matplotlib widget

# Para plotly
import plotly.io as pio
pio.renderers.default = 'notebook'
```

---

### **Problema: "Module not found"**

**Solução:**
```bash
# Instalar no kernel correto
python -m pip install nome-do-pacote

# Ou dentro do notebook
!pip install nome-do-pacote

# Verificar kernel ativo
import sys
print(sys.executable)
```

---

### **Problema: Notebook muito lento**

**Soluções:**
```python
# 1. Usar cache de queries
@lru_cache(maxsize=None)
def get_data():
    return client.query(query).to_dataframe()

# 2. Salvar intermediários
df.to_csv('outputs/temp_data.csv', index=False)
df = pd.read_csv('outputs/temp_data.csv')

# 3. Usar chunks
for chunk in pd.read_csv('file.csv', chunksize=10000):
    process(chunk)
```

---

## 📤 Exportar Notebooks

### **Para HTML (Compartilhamento)**

```bash
# Exportar um notebook
jupyter nbconvert --to html notebooks/01_exploratory_analysis.ipynb

# Exportar todos
jupyter nbconvert --to html notebooks/*.ipynb

# Com output customizado
jupyter nbconvert --to html --output-dir=outputs/reports/ notebooks/01_exploratory_analysis.ipynb
```

---

### **Para PDF (Apresentação)**

```bash
# Requer LaTeX instalado
jupyter nbconvert --to pdf notebooks/09_business_insights_summary.ipynb

# Ou via HTML
jupyter nbconvert --to html notebooks/09_business_insights_summary.ipynb
wkhtmltopdf outputs/reports/09_business_insights_summary.html output.pdf
```

---

### **Para Python Script**

```bash
# Converter para .py
jupyter nbconvert --to python notebooks/04_rfm_segmentation.ipynb

# Output: notebooks/04_rfm_segmentation.py
```

---

## 🎨 Customização

### **Temas do JupyterLab**

```bash
# Instalar tema escuro
pip install jupyterlab-theme-solarized-dark
jupyter labextension install jupyterlab-theme-solarized-dark

# Ativar tema
# Settings → JupyterLab Theme → Solarized Dark
```

### **Extensões Úteis**

```bash
# Table of Contents
jupyter labextension install @jupyterlab/toc

# Variable Inspector
jupyter labextension install @lckr/jupyterlab_variableinspector

# Code Formatter
pip install jupyterlab-code-formatter black
```

---

## 📚 Recursos Adicionais

### **Tutoriais**

- 📖 [Jupyter Documentation](https://jupyter.org/documentation)
- 📖 [Pandas User Guide](https://pandas.pydata.org/docs/user_guide/index.html)
- 📖 [Matplotlib Tutorials](https://matplotlib.org/stable/tutorials/index.html)
- 📖 [Seaborn Tutorial](https://seaborn.pydata.org/tutorial.html)

### **Galeria de Exemplos**

- 🎨 [Seaborn Gallery](https://seaborn.pydata.org/examples/index.html)
- 🎨 [Plotly Gallery](https://plotly.com/python/)
- 🎨 [Kaggle Notebooks](https://www.kaggle.com/code)

---

## ✅ Checklist Final

Antes de considerar um notebook completo:

- [ ] Todas as células executam sem erro
- [ ] Código está comentado e legível
- [ ] Visualizações têm títulos e labels
- [ ] Insights estão documentados em markdown
- [ ] Outputs foram limpos (antes de commit)
- [ ] Notebook foi exportado para HTML
- [ ] Gráficos importantes foram salvos em `outputs/figures/`

---

## 🚀 Quick Start

```bash
# Setup
cd notebooks/
jupyter lab

# Abrir primeiro notebook
# → 01_exploratory_analysis.ipynb

# Executar todas as células
# Menu → Run → Run All Cells

# Explorar e iterar!
```

---

**Happy Analyzing! 📊🐍**

---

**Última atualização:** Novembro 2024  
**Autor:** Andre Bomfim  
**Projeto:** [GitHub - analise23](https://github.com/AndreBomfim99/analise23)