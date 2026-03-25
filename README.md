# 📊 Curva ABC Dashboard - Diagnóstico e Ações

Uma ferramenta avançada de inteligência de dados para e-commerce, focada em análise de **Curva ABC**, **Saúde de Conta** e **Ações Estratégicas** para os principais marketplaces: **Mercado Livre**, **Shopee** e **Amazon**.

---

## 🚀 Funcionalidades Principais

- **Detecção Automática de Canal:** Basta arrastar seus relatórios e o sistema identifica se os dados são do Mercado Livre, Shopee ou Amazon.
- **Análise de Curva ABC Dinâmica:** Classificação automática de produtos em A, B e C baseada em faturamento acumulado.
- **Buckets Temporais (Mercado Livre):** Visualização de tendências em 30, 60, 90 e 120 dias para identificar produtos em ascensão ou queda.
- **Diagnóstico de Logística:** Monitoramento de penetração em Full, Flex, Coleta e Correios.
- **Inteligência de Publicidade:** Separação clara entre vendas orgânicas e via Ads (ACOS/Impacto).
- **Funil de Conversão (Shopee):** Análise de Taxa de Rejeição, Adição ao Carrinho e Conversão Final.
- **Monitoramento de Buy Box (Amazon):** Alertas de perda de oferta em destaque e impacto no faturamento.

---

## 🛠️ Como Usar

### 1. Preparação dos Dados
Para cada canal, exporte os relatórios originais das centrais de vendedor:

| Canal | Relatório | Formato | Período Recomendado |
| :--- | :--- | :--- | :--- |
| **Mercado Livre** | Vendas > Vendas > Download | `.xlsx` | 120 dias |
| **Shopee** | Informações Gerenciais > Produto | `.xlsx` | 30 dias |
| **Amazon** | Relatórios de Negócios > Por ASIN | `.csv` | 30 dias |

> **⚠️ Importante:** Não abra ou salve os arquivos no Excel antes do upload para evitar corrupção de formatos de data e valores.

### 2. Execução Local
Certifique-se de ter o Python instalado e siga os passos:

```bash
# Clone o repositório
git clone https://github.com/vlima-creator/Teste-ABC.git

# Entre na pasta
cd Teste-ABC

# Instale as dependências
pip install -r requirements.txt

# Execute o app
streamlit run app.py
```

---

## 💡 Estratégia de Análise

O dashboard não apenas mostra números, mas sugere ações baseadas na classe do produto:

- **Classe A (80% do faturamento):** Foco total em **estoque** e **proteção de margem**.
- **Classe B (15% do faturamento):** Foco em **otimização de anúncios** e **Ads** para subir para Classe A.
- **Classe C (5% do faturamento):** Foco em **liquidação** ou **descontinuação** para liberar capital de giro.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.11+**
- **Streamlit:** Interface de usuário premium e interativa.
- **Pandas:** Processamento e limpeza de dados de alta performance.
- **Plotly:** Visualizações gráficas dinâmicas.

---

## 👤 Autor

**Vinicius Lima**  
*Estratégia de Dados para E-commerce*  
CNPJ: 47.192.694/0001-70
