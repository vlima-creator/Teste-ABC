import streamlit as st
from ui.components.shared_ui import get_svg_icon

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
    st.markdown("### Fluxo de Trabalho Recomendado")
    
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
    st.markdown("### Especificações por Canal")
    
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
                
                *   **Arquivos Aceitos:** Você pode subir até 3 arquivos (Performance de Produto, Vendas e Tráfego). O de **Performance de Produto** (parentskudetail) é o principal.
                *   **Taxa de Rejeição:** Indica visitantes que saíram sem interagir. Se estiver alta, revise sua foto principal e título.
                *   **Conversão de Carrinho:** Mostra se o cliente desiste no fechamento (pode ser frete caro ou falta de cupons).
                *   **Análise Semanal:** O sistema monitora as últimas 5 semanas para detectar mudanças rápidas de tendência.
                """
            )
        with col_sh_2:
            st.markdown(
                """
                **Onde baixar:**
                1. Informações Gerenciais
                2. Aba Produto
                3. Performance de Produto
                4. Exportar (Excel)
                """
            )

    with st.expander("Amazon - Buy Box e Visibilidade"):
        col_am_1, col_am_2 = st.columns([2, 1])
        with col_am_1:
            st.markdown(
                """
                A métrica vital na Amazon é a **Buy Box (Oferta em Destaque)**.
                
                *   **Buy Box %:** Se estiver abaixo de 80%, o sistema sinaliza como perda de destaque. Abaixo de 20% é considerado nível crítico.
                *   **Sessões vs Conversão:** Se tem muitas sessões e pouca conversão (abaixo de 1%), o problema é a oferta. Se tem poucas sessões e alta conversão, o problema é o tráfego (SEO/Ads).
                *   **Multi-arquivos:** Você pode subir vários CSVs de "Relatórios de Negócios" e o sistema irá consolidá-los.
                """
            )
        with col_am_2:
            st.markdown(
                """
                **Onde baixar:**
                1. Relatórios > Negócios
                2. Detalhes de vendas e tráfego por ASIN
                3. Selecionar período
                4. Exportar (CSV)
                """
            )

    st.markdown("---")

    # Seção 3: Inteligência e Ações
    st.markdown("### Inteligência e Ações Táticas")
    st.markdown(
        """
        O sistema gera automaticamente **Cards Táticos** com base no comportamento de cada produto. 
        Veja como interpretar as principais recomendações:
        """
    )
    
    tac1, tac2, tac3 = st.columns(3)
    
    with tac1:
        st.markdown(f'<div class="metric-icon" style="width:32px; height:32px; margin-bottom:8px;">{get_svg_icon("target")}</div>', unsafe_allow_html=True)
        st.markdown("**Defesa de Curva A**")
        st.caption("Produtos com alto faturamento mas queda de Buy Box ou estoque baixo. Ação imediata necessária para proteger o faturamento.")
        
    with tac2:
        st.markdown(f'<div class="metric-icon" style="width:32px; height:32px; margin-bottom:8px;">{get_svg_icon("trending-up")}</div>', unsafe_allow_html=True)
        st.markdown("**Ataque de Curva B**")
        st.caption("Produtos com potencial de virar \'A\'. Recomenda-se aumento de investimento em Ads ou melhoria de SEO.")
        
    with tac3:
        st.markdown(f'<div class="metric-icon" style="width:32px; height:32px; margin-bottom:8px;">{get_svg_icon("package")}</div>', unsafe_allow_html=True)
        st.markdown("**Limpeza de Curva C**")
        st.caption("Produtos com baixo giro e estoque parado. Recomenda-se liquidação para liberar capital de giro.")

    st.markdown("---")

    # Seção 4: Entendendo a Curva ABC
    st.markdown("### Entendendo a Curva ABC")
    
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
    st.markdown("### Solução de Problemas Comuns")
    
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
