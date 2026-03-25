# 📊 Manual Avançado: Curva ABC Dashboard
**Guia Definitivo para Escalar suas Vendas com Inteligência de Dados**

---

## 1. Visão Geral da Ferramenta

O **Curva ABC Dashboard** é uma plataforma de inteligência de dados projetada para vendedores de alta performance. Ele processa relatórios brutos dos principais marketplaces e os transforma em ações táticas imediatas.

### 🧭 Navegação Principal
A interface é dividida em três áreas principais:
1. **Menu Lateral (Esquerda):** Onde você faz o upload dos arquivos e aplica filtros (por curva, status, etc.).
2. **Painel de Métricas (Topo):** Resumo financeiro e de volume de vendas.
3. **Área de Diagnóstico (Centro):** Gráficos, funis de conversão e tabelas de ação.

---

## 2. Como Preparar e Subir seus Dados

O sucesso da análise depende da qualidade dos dados. Siga as regras abaixo rigorosamente.

> **⚠️ REGRA DE OURO:** Nunca abra os relatórios no Excel antes de subir no sistema. O Excel altera formatos de data e separadores decimais, o que corrompe a leitura dos dados. Baixe da plataforma e arraste direto para o Dashboard.

### 📦 Mercado Livre
*   **Onde baixar:** Painel do Vendedor > Vendas > Vendas > Ícone de Download.
*   **Formato:** `.xlsx` (Excel).
*   **Período:** Selecione exatamente **120 dias**. Isso é crucial para que o sistema consiga calcular a tendência de vendas nos buckets de 30, 60, 90 e 120 dias.

### 📱 Shopee
*   **Onde baixar:** Central do Vendedor > Informações Gerenciais > Aba Produto > Performance de Produto.
*   **Formato:** `.xlsx` (Excel).
*   **Período:** Últimos **30 dias**.
*   **Dica:** Você pode subir até 3 arquivos simultaneamente (Performance, Vendas e Tráfego) para uma análise mais profunda.

### 🛡️ Amazon
*   **Onde baixar:** Seller Central > Relatórios > Relatórios de Negócios > Detalhes de vendas e tráfego por ASIN.
*   **Formato:** `.csv`.
*   **Período:** Últimos **30 dias**.
*   **Dica:** O sistema aceita múltiplos arquivos CSV de uma vez e os consolida automaticamente.

---

## 3. Entendendo a Curva ABC na Prática

A Curva ABC classifica seus produtos com base na representatividade do faturamento total.

| Classe | Representação | Significado | Ação Estratégica |
| :--- | :--- | :--- | :--- |
| **A** | **80%** do Faturamento | Seus "Carros-Chefe". Poucos produtos que trazem muito dinheiro. | **Proteger:** Ruptura de estoque aqui é fatal. Monitore margem e logística diariamente. |
| **B** | **15%** do Faturamento | Produtos intermediários com potencial de crescimento. | **Otimizar:** Invista em Ads, melhore fotos e SEO para tentar transformá-los em Classe A. |
| **C** | **5%** do Faturamento | A "Cauda Longa". Muitos produtos que vendem pouco. | **Liquidar:** Avalie se o custo de armazenagem compensa. Faça promoções para liberar capital. |

---

## 4. Diagnósticos por Canal

Cada marketplace exige uma estratégia diferente. O Dashboard adapta a visualização automaticamente.

### 📦 Análise Mercado Livre: Giro e Logística
No Mercado Livre, velocidade de entrega é conversão.

*   **Buckets Temporais:** Observe a tabela de evolução. Se um produto era Classe "C" há 90 dias e hoje é Classe "A", ele está em forte tendência de alta. Aumente a compra com o fornecedor.
*   **Penetração Logística:** O painel mostra quanto você vende via Full, Flex, Coleta e Correios.
    *   *Ação:* Produtos Classe A com baixa penetração no Full devem ser enviados para o CD do Mercado Livre imediatamente.
*   **Impacto de Ads:** O sistema separa vendas orgânicas de vendas via publicidade. Se um produto Classe A depende de mais de 40% de Ads, sua margem pode estar em risco.

### 📱 Análise Shopee: Funil e Engajamento
Na Shopee, o foco é entender onde o cliente desiste da compra.

*   **Taxa de Rejeição:** Porcentagem de pessoas que abrem o anúncio e saem sem clicar em nada.
    *   *Ação:* Se for maior que 60%, sua foto principal, título ou preço inicial estão ruins. O cliente clicou na busca, mas não gostou do que viu.
*   **Conversão de Carrinho:** Relação entre quem adicionou ao carrinho e quem pagou.
    *   *Ação:* Se muitos adicionam e poucos pagam, o problema é o frete ou a falta de cupons. Crie "Cupons de Seguidor" ou combos.

### 🛡️ Análise Amazon: Buy Box e Visibilidade
Na Amazon, quem não tem a Buy Box não vende.

*   **Buy Box %:** O tempo que seu produto passou como a oferta principal.
    *   *Ação:* Se a Buy Box de um produto Classe A cair abaixo de 90%, você tem uma emergência. Verifique se um concorrente baixou o preço ou se seu estoque FBA acabou.
*   **Sessões vs. Conversão (Unit Session %):**
    *   *Muitas sessões, pouca conversão:* O cliente acha seu produto, mas a oferta (preço, reviews, descrição) está ruim.
    *   *Poucas sessões, alta conversão:* A oferta é ótima, mas ninguém acha. Invista em Amazon Ads ou melhore as palavras-chave.

---

## 5. Cards Táticos: O que fazer hoje?

O sistema gera recomendações automáticas baseadas no cruzamento de dados. Procure por estes ícones na interface:

*   🛡️ **Defesa de Curva A:** Alerta crítico. Um produto que traz muito faturamento está perdendo performance (ex: perdeu Buy Box ou as vendas caíram nos últimos 30 dias). Aja imediatamente.
*   ⚔️ **Ataque de Curva B:** Oportunidade. Um produto intermediário está com alta taxa de conversão. Aumente o investimento em Ads para escalá-lo.
*   🧹 **Limpeza de Curva C:** Alerta de capital parado. Produtos com alto volume de estoque e baixíssima saída. Crie kits ou baixe o preço para liquidar.

---

## 6. Solução de Problemas Comuns

**Problema:** O sistema diz "Formato de arquivo inválido".
**Solução:** Você provavelmente abriu o arquivo no Excel antes de subir. Baixe novamente da plataforma e arraste direto para o Dashboard.

**Problema:** Os dados de 60, 90 e 120 dias do Mercado Livre estão zerados.
**Solução:** Você baixou o relatório de apenas 30 dias. Volte ao Mercado Livre e selecione o período de 120 dias antes de exportar.

**Problema:** A Shopee não mostra dados de logística.
**Solução:** É o comportamento normal. A Shopee não exporta dados detalhados de logística no relatório de performance de produto.

---
**Desenvolvido por Vinicius Lima**  
*Estratégia de Dados para E-commerce*  
CNPJ: 47.192.694/0001-70
