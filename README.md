# Curva ABC Dashboard

Ferramenta de inteligência de dados para vendedores de alta performance, focada em transformar relatórios brutos de marketplaces em ações táticas imediatas.

---

## Funcionalidades

- **Análise Multi-Canal:** Suporte integrado para Mercado Livre, Shopee e Amazon.
- **Curva ABC Dinâmica:** Classificação de produtos por relevância de faturamento em múltiplos períodos (30, 60, 90, 120 dias).
- **Diagnóstico Estratégico:** Identificação automática de produtos Âncora, Fuga de Receita e Potenciais.
- **Plano Tático Automatizado:** Geração de recomendações de ação para cada produto, divididas em frentes (Defesa, Ataque, Correção, Limpeza, Otimização).
- **Análise de Logística (ML):** Detalhamento de vendas por modalidade (Full, Flex, Coleta, Correios).
- **Funil de Conversão (Shopee/Amazon):** Métricas de engajamento, rejeição e conversão.
- **Monitoramento de Buy Box (Amazon):** Alertas de perda de destaque e análise de competitividade.

---

## Como Utilizar

1.  **Extraia os Relatórios:** Baixe os arquivos originais dos marketplaces sem abri-los ou editá-los.
2.  **Faça o Upload:** Arraste os arquivos para a área de upload na barra lateral do aplicativo.
3.  **Navegue pelas Abas:** Utilize as abas de diagnóstico para analisar os dados e tomar decisões.

### Requisitos de Arquivo por Canal

| Canal | Relatório | Período Recomendado |
| :--- | :--- | :--- |
| **Mercado Livre** | Vendas (Excel) | 120 dias |
| **Shopee** | Performance de Produto (Excel) | 30 dias |
| **Amazon** | Detalhes de Vendas e Tráfego (CSV) | 30 dias |

---

## Tecnologias Utilizadas

- **Backend:** Python, Pandas
- **Frontend:** Streamlit
- **Visualização de Dados:** Plotly

---

## Autor

**Vinicius Lima**
- Estratégia de Dados para E-commerce
- CNPJ: 47.192.694/0001-70
