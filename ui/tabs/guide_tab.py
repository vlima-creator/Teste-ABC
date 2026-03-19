import streamlit as st

def render_guide_tab():
    st.markdown(
        """
        <div class='hero-header'>
            <div class='hero-title'>Guia de Uso e Relatórios</div>
            <div class='hero-subtitle'>Aprenda a extrair o máximo da ferramenta e quais dados são necessários.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🚀 Como usar a ferramenta")
        st.info(
            "Esta ferramenta foi desenhada para automatizar a análise de performance da sua conta, "
            "transformando relatórios brutos em insights estratégicos."
        )
        st.markdown(
            """
            1. **Seleção de Canal:** Na barra lateral, escolha entre **Mercado Livre**, **Shopee** ou **Amazon**.
            2. **Upload de Dados:** Insira os arquivos (.xlsx, .csv ou .txt) extraídos diretamente das plataformas.
            3. **Análise de Período:** No Dashboard, alterne entre as janelas de 30, 60, 90 ou 120 dias para ver a evolução.
            4. **Exportação:** Utilize a aba 'Listas e Exportação' para baixar as listas de ações prontas para execução.
            """
        )

    with col2:
        st.markdown("### 📊 O que conseguimos analisar")
        st.markdown(
            """
            - **Curva ABC Dinâmica:** Classificação automática de produtos por relevância de faturamento.
            - **Saúde de Portfólio:** Identificação de 'Produtos Estrela' vs 'Produtos Mortos'.
            - **Eficiência Logística:** (ML) Impacto do Full e outras modalidades no seu resultado.
            - **Funil de Conversão:** (Shopee) Onde você está perdendo clientes (Visitas -> Carrinho -> Pedidos).
            - **Plano de Ação:** Sugestões automáticas de preço, estoque e publicidade.
            """
        )

    st.markdown("---")
    st.markdown("### 📥 Onde baixar os relatórios precisos")

    tab_ml, tab_shopee, tab_amazon = st.tabs(["Mercado Livre", "Shopee", "Amazon"])

    with tab_ml:
        st.markdown(
            """
            | Relatório | Caminho no Mercado Livre | Finalidade na Ferramenta |
            | :--- | :--- | :--- |
            | **Vendas** | Vendas > Vendas > Ícone de Download (Excel) | Base de pedidos, datas e status. |
            """
        )
        st.warning("⚠️ **Atenção:** O Mercado Livre exporta arquivos com nomes como `Vendas-202X-XX-XX.xlsx`. Carregue o arquivo completo sem alterações.")

    with tab_shopee:
        st.markdown(
            """
            | Relatório | Caminho na Shopee | Arquivo Esperado |
            | :--- | :--- | :--- |
            | **Performance de Produto** | Informações Gerenciais > Produto > Performance > Exportar | `parentskudetail...xlsx` |
            | **Visão Geral de Vendas** | Informações Gerenciais > Vendas > Visão Geral > Exportar | `sales_overview...xlsx` |
            | **Visão Geral de Tráfego** | Informações Gerenciais > Tráfego > Visão Geral > Exportar | `traffic_overview...xlsx` |
            """
        )
        st.info("💡 **Dica:** O arquivo `parentskudetail` é o mais importante para a análise da Curva ABC.")
    
    with tab_amazon:
        st.markdown(
            \"\"\"
            | Relatório | Caminho na Amazon | Arquivo Esperado |
            | :--- | :--- | :--- |
            | **Relatórios de Negócios** | Relatórios > Relatórios de Negócios > Por ASIN > Detalhes de vendas e tráfego da página de detalhes por item pai | `BusinessReport...csv` ou `.txt` |
            | **Painel de Vendas** | Relatórios > Painel de Vendas > Exportar | `SalesDashboard...csv` |
            \"\"\"
        )
        st.info("💡 **Dica:** Os relatórios da Amazon podem ser exportados tanto em formato CSV quanto TXT.")

    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; opacity: 0.6; font-size: 0.8rem; padding: 20px;'>
            © Desenvolvido por Vinicius Lima/ CNPJ: 47.192.694/0001-70
        </div>
        """,
        unsafe_allow_html=True
    )
