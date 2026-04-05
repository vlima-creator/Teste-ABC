import streamlit as st
from ui.components.shared_ui import render_report_section, render_metric_grid

def render_guide_tab():
    st.markdown(
        """
        <div class='hero-header'>
            <div class='hero-title'>Guia Estratégico e de Operação</div>
            <div class='hero-subtitle'>Domine a análise de dados para escalar suas vendas nos principais marketplaces.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Seção 1: Fluxo de Trabalho
    st.markdown(render_report_section("layout", "Fluxo de Trabalho Recomendado", "Siga estes passos para uma análise precisa", "purple"), unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**1. Extração de Dados**")
        st.markdown(
            """
            Baixe os relatórios diretamente das centrais de vendedor. 
            **Importante:** Não abra ou salve os arquivos no Excel antes do upload, pois isso pode alterar o formato das datas e números.
            """
        )
        
    with col2:
        st.info("**2. Upload e Detecção**")
        st.markdown(
            """
            Arraste os arquivos para a área de upload. O sistema identificará automaticamente se os dados são do **Mercado Livre**, **Shopee** ou **Amazon**.
            """
        )
        
    with col3:
        st.info("**3. Análise e Ação**")
        st.markdown(
            """
            Navegue pelas abas de diagnóstico. Identifique produtos que estão perdendo performance e aplique as ações recomendadas pelo sistema.
            """
        )

    st.markdown("---")

    # Seção 2: Detalhes por Canal
    st.markdown(render_report_section("📊", "Especificações por Canal", "Detalhes técnicos para cada marketplace", "blue"), unsafe_allow_html=True)
    
    with st.expander("Mercado Livre - Análise de Giro e Logística", expanded=True):
        col_ml_1, col_ml_2 = st.columns([2, 1])
        with col_ml_1:
            st.markdown(
                """
                A análise do Mercado Livre é focada na **estabilidade de vendas** e **eficiência logística**.
                
                *   **Período Ideal:** Baixe o relatório de vendas dos últimos **120 dias**.
                *   **Buckets Temporais:** O sistema divide as vendas em 4 períodos (0-30, 31-60, 61-90, 91-120 dias). Isso permite ver se um produto está em tendência de alta ou queda.
                *   **Logística:** Identificamos automaticamente vendas via **Full, Flex, Coleta e Correios**.
                *   **Publicidade:** Separamos o que é venda orgânica do que veio via **Mercado Ads**.
                """
            )
        with col_ml_2:
            st.markdown(
                """
                **Onde baixar:**
                1. Vendas > Vendas
                2. Ícone de Download
                3. Selecionar período (120 dias)
                4. Formato Excel
                """
            )

    with st.expander("Shopee - Funil de Conversão e Rejeição"):
        col_sh_1, col_sh_2 = st.columns([2, 1])
        with col_sh_1:
            st.markdown(
                """
                Na Shopee, o foco é o **comportamento do usuário** e o funil de vendas.
                
                *   **Arquivos Aceitos:** Você pode subir até 3 arquivos simultaneamente para uma análise completa.
                *   **Performance de Produto:** (Obrigatório) Relatório detalhado por SKU para análise de conversão e rejeição.
                *   **Vendas e Tráfego:** (Opcional) Relatórios de visão geral que permitem uma análise semanal mais precisa.
                *   **Análise Semanal:** O sistema monitora as últimas 5 semanas para detectar mudanças rápidas de tendência.
                """
            )
        with col_sh_2:
            st.markdown(
                """
                **Onde baixar:**
                1. Informações Gerenciais
                2. Aba Produto > Performance
                3. Aba Vendas > Visão Geral
                4. Aba Tráfego > Visão Geral
                5. Exportar todos em **Excel**
                """
            )

    with st.expander("Amazon - Buy Box e Visibilidade"):
        col_am_1, col_am_2 = st.columns([2, 1])
        with col_am_1:
            st.markdown(
                """
                A métrica vital na Amazon é a **Buy Box (Oferta em Destaque)**.
                
                *   **Multi-arquivos:** Você pode subir vários CSVs de "Relatórios de Negócios" e o sistema irá consolidar os dados automaticamente.
                *   **Buy Box %:** Se estiver abaixo de 80%, o sistema sinaliza como perda de destaque. Abaixo de 20% é considerado nível crítico.
                *   **Sessões vs Conversão:** Se tem muitas sessões e pouca conversão (abaixo de 1%), o problema é a oferta.
                *   **Análise Semanal:** Ao subir relatórios com datas, o sistema habilita o monitoramento de tendências das últimas 5 semanas.
                """
            )
        with col_am_2:
            st.markdown(
                """
                **Onde baixar:**
                1. Relatórios > Negócios
                2. Detalhes de vendas e tráfego por ASIN
                3. Selecionar período desejado
                4. Exportar em **CSV**
                """
            )

    st.markdown("---")

    # Seção 3: Inteligência e Ações
    st.markdown(render_report_section("lightbulb", "Inteligência e Ações Táticas", "Interpretação das recomendações automáticas", "amber"), unsafe_allow_html=True)
    
    tac_metrics = [
        ("Defesa de Curva A", "Proteger Faturamento", "🛡️", "rose"),
        ("Ataque de Curva B", "Escalar Vendas", "⚔️", "green"),
        ("Limpeza de Curva C", "Liberar Capital", "🧹", "blue")
    ]
    # Como render_metric_grid espera emojis para mapear para ícones, vamos ajustar o mapeamento no shared_ui ou usar os nomes de ícones diretamente se suportado.
    # Vou usar render_metric_grid com os ícones mapeados.
    
    render_metric_grid([
        ("Defesa de Curva A", "Proteger Faturamento", "star", "rose"),
        ("Ataque de Curva B", "Escalar Vendas", "trending-up", "green"),
        ("Limpeza de Curva C", "Liberar Capital", "package", "blue")
    ])

    st.markdown("---")

    # Seção 4: Entendendo a Curva ABC
    st.markdown(render_report_section("bar-chart-3", "Entendendo a Curva ABC", "Classificação de relevância do catálogo", "green"), unsafe_allow_html=True)
    
    abc_col1, abc_col2, abc_col3 = st.columns(3)
    
    with abc_col1:
        st.success("#### Classe A (80%)")
        st.markdown("Seus produtos 'estrela'. Representam 80% do seu faturamento. **Ação:** Nunca deixe faltar estoque e monitore a margem de perto.")
        
    with abc_col2:
        st.warning("#### Classe B (15%)")
        st.markdown("Produtos intermediários. Representam os próximos 15%. **Ação:** Tente transformá-los em 'A' através de melhorias no anúncio ou Ads.")
        
    with abc_col3:
        st.error("#### Classe C (5%)")
        st.markdown("A 'cauda longa'. Muitos produtos que somam apenas 5% do faturamento. **Ação:** Avalie se vale a pena manter o estoque ou se deve liquidar.")

    st.markdown("---")

    # Seção 5: Solução de Problemas
    st.markdown(render_report_section("⚠️", "Solução de Problemas Comuns", "Dúvidas frequentes e erros de processamento", "rose"), unsafe_allow_html=True)
    
    with st.expander("O sistema não reconheceu meu arquivo"):
        st.markdown(
            """
            1.  **Formato:** Certifique-se de que é um arquivo original (Excel para ML/Shopee, CSV para Amazon).
            2.  **Edição:** Se você abriu o arquivo e salvou, ele pode ter mudado. Baixe novamente do marketplace.
            3.  **Idioma:** O sistema está otimizado para relatórios em Português.
            """
        )
    
    with st.expander("Os dados parecem incorretos"):
        st.markdown(
            """
            *   **Mercado Livre:** Verifique se você selecionou o período de 120 dias. Se selecionar menos, os buckets de 60/90/120 ficarão zerados.
            *   **Warning Semanal:** Esta aba sempre foca nas últimas 5 semanas de dados para garantir uma análise ágil de tendências.
            *   **Filtros:** Verifique se há filtros aplicados no menu lateral que estão ocultando dados.
            """
        )

    st.markdown(
        """
        <div style='text-align: center; opacity: 0.6; font-size: 0.8rem; padding: 40px 20px 20px 20px;'>
            © Desenvolvido por Vinicius Lima | Estratégia de Dados para E-commerce<br>
            CNPJ: 47.192.694/0001-70
        </div>
        """,
        unsafe_allow_html=True
    )
