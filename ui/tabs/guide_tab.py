import streamlit as st

def render_guide_tab():
    st.markdown(
        """
        <div class='hero-header'>
            <div class='hero-title'>Guia de Uso e Relatórios</div>
            <div class='hero-subtitle'>Aprenda a extrair o máximo da ferramenta e quais dados são necessários para a sua análise.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Tópico 1: Como Começar - Passo a Passo
    with st.expander("🚀 Como Começar - Passo a Passo", expanded=True):
        st.markdown(
            """
            Para iniciar sua análise, siga este fluxo otimizado:
            
            1.  **Seleção do Canal:** No menu lateral, escolha a plataforma que deseja analisar (**Amazon**, **Mercado Livre** ou **Shopee**).
            2.  **Preparação dos Arquivos:** Certifique-se de ter baixado os relatórios brutos das plataformas (conforme a tabela abaixo). Não é necessário editar os arquivos.
            3.  **Upload de Dados:** Arraste e solte os arquivos na área de upload. A ferramenta detectará automaticamente o formato e processará os dados.
            4.  **Navegação no Dashboard:** 
                *   Use os **filtros de data** para ajustar o período de análise.
                *   Explore a **Curva ABC** para identificar seus produtos de maior impacto.
                *   Analise as **Métricas de Saúde** para ver quais produtos precisam de atenção imediata.
            5.  **Ações e Exportação:** Vá até a aba 'Listas e Exportação' para baixar o plano de ação pronto para ser executado na sua operação.
            """
        )

    # Tópico 2: Localizando os Relatórios
    with st.expander("📂 Localizando os Relatórios"):
        tab_amazon, tab_ml, tab_shopee = st.tabs(["Amazon", "Mercado Livre", "Shopee"])
        
        with tab_amazon:
            st.markdown(
                """
                | Relatório | Caminho na Amazon Seller Central | Arquivo Esperado |
                | :--- | :--- | :--- |
                | **Relatório de Negócios** | Relatórios > Relatórios de Negócios > Por ASIN > Detalhes de vendas e tráfego da página de detalhes por item pai | `BusinessReport...csv` ou `.txt` |
                | **Painel de Vendas** | Relatórios > Painel de Vendas > Exportar | `SalesDashboard...csv` |
                
                **Dica:** O relatório de "Detalhes de vendas e tráfego" é o mais completo, pois contém dados de **Sessões** e **Buy Box %**.
                """
            )

        with tab_ml:
            st.markdown(
                """
                | Relatório | Caminho no Mercado Livre | Finalidade |
                | :--- | :--- | :--- |
                | **Vendas** | Vendas > Vendas > Ícone de Download (Excel) | Base de pedidos, faturamento e status de logística. |
                
                **Atenção:** Carregue o arquivo `.xlsx` original sem alterar nomes de colunas.
                """
            )

        with tab_shopee:
            st.markdown(
                """
                | Relatório | Caminho na Central do Vendedor Shopee | Arquivo Esperado |
                | :--- | :--- | :--- |
                | **Performance de Produto** | Informações Gerenciais > Produto > Performance > Exportar | `parentskudetail...xlsx` |
                | **Visão Geral de Vendas** | Informações Gerenciais > Vendas > Visão Geral > Exportar | `sales_overview...xlsx` |
                | **Visão Geral de Tráfego** | Informações Gerenciais > Tráfego > Visão Geral > Exportar | `traffic_overview...xlsx` |
                """
            )

    # Tópico 3: Explicação dos Cálculos e Métricas
    with st.expander("📊 Explicação dos Cálculos e Métricas"):
        st.markdown(
            """
            Entenda como os indicadores são calculados para tomar decisões melhores:

            *   **Curva ABC (Faturamento):**
                *   **Classe A:** 20% dos produtos que geram ~80% do seu faturamento (Foco Total).
                *   **Classe B:** 30% dos produtos que geram ~15% do seu faturamento (Potencial de Crescimento).
                *   **Classe C:** 50% dos produtos que geram ~5% do seu faturamento (Eficiência Operacional).
            
            *   **Métricas Exclusivas Amazon:**
                *   **Buy Box % (Oferta em Destaque):** Porcentagem de tempo que seu produto foi a opção de compra principal. Abaixo de 80% indica perda de competitividade ou estoque.
                *   **Sessões:** Número de visitantes únicos que visualizaram suas ofertas.
                *   **Conversão (Unit Session Percentage):** Unidades pedidas divididas pelo número de sessões.
            
            *   **Saúde do Produto:**
                *   **Produto Estrela:** Alto faturamento e alta conversão.
                *   **Produto Morto:** Sem vendas nos últimos 30 dias.
                *   **Oportunidade:** Alto tráfego (sessões), mas baixa conversão.
            """
        )

    # Tópico 4: Dicas e Boas Práticas
    with st.expander("💡 Dicas e Boas Práticas"):
        st.markdown(
            """
            Para extrair o melhor da ferramenta:
            
            *   **Frequência de Análise:** Recomendamos realizar o upload dos dados semanalmente para acompanhar tendências de queda na Buy Box ou aumento de estoque parado.
            *   **Períodos Comparativos:** Ao analisar a Curva ABC, compare o período de 30 dias com o de 90 dias para identificar se um produto 'A' está perdendo relevância.
            *   **Ação Imediata:** Produtos que caíram da Curva A para a B ou C devem ser prioridade em revisões de preço ou campanhas de Ads.
            *   **Limpeza de Dados:** Não abra os arquivos CSV/Excel e salve-os novamente antes do upload, pois isso pode alterar a formatação de datas e moedas, causando erros no processamento.
            """
        )

    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; opacity: 0.6; font-size: 0.8rem; padding: 20px;'>
            © Desenvolvido por Vinicius Lima/ CNPJ: 47.192.694/0001-70
        </div>
        """,
        unsafe_allow_html=True
    )
