# 📈 Analytics Scripts - Olist E-Commerce

Scripts Python para análises avançadas e geração de insights de negócio.

---

## 📋 Conteúdo

1. [Visão Geral](#visao-geral)
2. [Scripts Disponíveis](#scripts)
3. [Como Usar](#uso)
4. [Outputs](#outputs)

---

## 🎯 Visão Geral {#visao-geral}

Scripts complementares aos notebooks para:

- Análises programáticas escaláveis
- Geração automatizada de relatórios
- Integração com pipelines CI/CD
- Exportação de métricas para dashboards

**Quando usar:**
- ✅ Análises recorrentes/automatizadas
- ✅ Pipelines de produção
- ✅ Geração de relatórios agendados

**Quando usar Notebooks:**
- ✅ Exploração interativa
- ✅ Prototipagem
- ✅ Apresentações

---

## 📜 Scripts Disponíveis {#scripts}

### **1. rfm_segmentation.py**

**Descrição:** Segmentação RFM automatizada

**Uso:**
```bash
python python/analytics/rfm_segmentation.py \
  --output data/processed/rfm_segments.csv
```

**Funcionalidades:**
- Cálculo RFM (Recency, Frequency, Monetary)
- Segmentação em 11 categorias
- Exportação CSV/JSON
- Integração com BigQuery

**Output:**
```csv
customer_id,rfm_score,segment,priority
ABC123,555,Champions,1
XYZ789,111,Lost,6
...
```

---

### **2. cohort_analysis.py**

**Descrição:** Análise de retenção por cohort

**Uso:**
```bash
python python/analytics/cohort_analysis.py \
  --start-date 2016-09-01 \
  --end-date 2018-08-31
```

**Output:**
- Matriz de retenção (CSV)
- Gráficos de curvas (PNG)
- Métricas agregadas (JSON)

---

### **3. category_performance.py**

**Descrição:** Performance por categoria de produto

**Uso:**
```bash
python python/analytics/category_performance.py \
  --top-n 20 \
  --format json
```

**Métricas:**
- Receita por categoria
- Ticket médio
- NPS médio
- Growth rate

---

### **4. delivery_analysis.py**

**Descrição:** Análise de SLA e entregas

**Uso:**
```bash
python python/analytics/delivery_analysis.py \
  --threshold 15  # SLA crítico em dias
```

**Outputs:**
- Taxa de compliance
- Rotas problemáticas
- Correlação atraso vs NPS

---

### **5. ltv_calculation.py**

**Descrição:** Cálculo de Lifetime Value

**Uso:**
```bash
python python/analytics/ltv_calculation.py \
  --method cohort  # ou 'historic' ou 'predictive'
```

**Métodos:**
- `cohort`: LTV por cohort mensal
- `historic`: LTV histórico médio
- `predictive`: LTV futuro (ML)

---

## ▶️ Como Usar {#uso}

### **Execução Individual**
```bash
# Com parâmetros default
python python/analytics/rfm_segmentation.py

# Com configurações customizadas
python python/analytics/rfm_segmentation.py \
  --project-id your-project \
  --dataset-id olist_ecommerce \
  --output data/processed/rfm_$(date +%Y%m%d).csv
```

---

### **Execução em Batch**
```bash
# Script runner
bash scripts/run_all_analytics.sh

# Ou Python
python python/analytics/run_all.py
```

**run_all.py:**
```python
import subprocess

scripts = [
    'rfm_segmentation.py',
    'cohort_analysis.py',
    'category_performance.py',
    'delivery_analysis.py'
]

for script in scripts:
    print(f"Executando {script}...")
    subprocess.run(['python', f'python/analytics/{script}'])
```

---

### **Agendamento (Cron)**
```bash
# Editar crontab
crontab -e

# Executar diariamente às 2am
0 2 * * * cd /path/to/project && python python/analytics/rfm_segmentation.py >> logs/analytics.log 2>&1

# Executar semanalmente (segunda-feira)
0 3 * * 1 cd /path/to/project && bash scripts/run_all_analytics.sh
```

---

## 📊 Outputs {#outputs}

### **Estrutura de Diretórios**
```
data/processed/
├── rfm_segments_20241104.csv
├── cohort_retention_20241104.csv
├── category_performance_20241104.json
└── delivery_metrics_20241104.csv

docs/images/
├── cohort_retention_curves.png
├── rfm_segments_distribution.png
└── category_pareto.png

logs/
└── analytics_20241104.log
```

---

### **Formatos de Output**

**CSV (padrão):**
```csv
metric,value,date
total_revenue,15000000.00,2024-11-04
avg_ticket,150.00,2024-11-04
```

**JSON (com `--format json`):**
```json
{
  "execution_date": "2024-11-04",
  "metrics": {
    "total_revenue": 15000000.00,
    "avg_ticket": 150.00
  },
  "segments": [...]
}
```

**BigQuery (com `--export-bq`):**
```bash
python python/analytics/rfm_segmentation.py \
  --export-bq \
  --bq-table analytics.rfm_segments
```

---

## 🔧 Configuração

### **Argumentos Comuns**
```bash
--project-id      # ID do projeto GCP
--dataset-id      # Dataset BigQuery
--output          # Arquivo de saída
--format          # csv, json, parquet
--export-bq       # Exportar para BigQuery
--verbose         # Logs detalhados
```

---

### **Exemplo de Uso Completo**
```bash
python python/analytics/rfm_segmentation.py \
  --project-id my-gcp-project \
  --dataset-id olist_ecommerce \
  --output data/processed/rfm_segments.csv \
  --format csv \
  --export-bq \
  --bq-table analytics.rfm_daily \
  --verbose
```

---

## 📚 Dependências
```txt
pandas>=2.0.0
google-cloud-bigquery>=3.10.0
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

---

## 🚀 Próximos Passos

1. **Explorar Notebooks:** `notebooks/`
2. **Criar Dashboards:** Looker Studio
3. **Automatizar:** Airflow/Cloud Scheduler

---

**✅ Analytics Rodando?** Veja: [Notebooks](../../notebooks/README.md)