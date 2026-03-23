import streamlit as st

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

    # Seção 1: Primeiros Passos
    st.markdown("### 🚀 Como Iniciar sua Análise")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            """
            Para extrair o máximo de inteligência da ferramenta, siga o fluxo de processamento:
            
            O primeiro passo é a **Seleção do Canal** no menu lateral. Cada marketplace possui métricas e comportamentos únicos que a ferramenta interpreta de forma distinta. Após selecionar o canal, realize a **Preparação dos Arquivos** baixando os relatórios brutos diretamente das centrais de vendedor, sem realizar edições manuais que possam corromper a estrutura de dados.
            
            Com os arquivos em mãos, utilize a área de **Upload de Dados**. O sistema detectará automaticamente o formato e processará as informações em segundos. Navegue pelo **Dashboard** explorando a Curva ABC e as Métricas de Saúde para identificar gargalos e oportunidades imediatas em sua operação.
            """
        )

    with col2:
        st.markdown(
            """
            | Canal | Relatório Principal | Onde Baixar |
            | :--- | :--- | :--- |
            | **Amazon** | Detalhes de vendas e tráfego | Relatórios > Negócios > Por ASIN |
            | **Mercado Livre** | Relatório de Vendas (Excel) | Vendas > Vendas > Ícone Download |
            | **Shopee** | Performance de Produto | Informações Gerenciais > Produto |
            
            *Certifique-se de baixar o período de 120 dias (4 meses) para o Mercado Livre para uma análise histórica completa.*
            """
        )

    st.markdown("---")

    # Seção 2: Inteligência por Canal
    st.markdown("### 💡 Inteligência e Estratégia por Canal")
    
    tab_ml, tab_shopee, tab_amazon = st.tabs([
        "📦 Mercado Livre (Giro e Logística)", 
        "📱 Shopee (Funil e Engajamento)", 
        "🛡️ Amazon (Buy Box e SEO)"
    ])

    with tab_ml:
        st.markdown(
            """
            No **Mercado Livre**, o sucesso é determinado pela velocidade de giro e pela eficiência da malha logística. A análise de **Buckets Temporais (30/60/90/120 dias)** permite identificar a constância de suas vendas. Um produto que hoje é Classe "A", mas era "C" há 90 dias, indica uma tendência de alta que exige atenção redobrada ao estoque.
            
            A **Penetração de Logística** é o indicador crucial de conversão. Vendas via **Full** e **Flex** tendem a ter taxas de conversão significativamente superiores ao envio convencional. Se seus produtos de curva "A" possuem baixa penetração no Full, sua prioridade estratégica deve ser o envio imediato de estoque para o centro de distribuição do Mercado Livre.
            
            | Métrica ML | O que observar | Ação Recomendada |
            | :--- | :--- | :--- |
            | **Impacto de Ads** | % de vendas via publicidade | Se > 30% em Curva A, revise o ACOS para proteger a margem. |
            | **Curva ABC Dinâmica** | Mudança de classe entre períodos | Produtos que caem de A para B precisam de revisão de preço ou oferta. |
            | **Mix de Logística** | Equilíbrio entre Full/Flex/Coleta | Priorize o Full para produtos de alto giro (Curva A). |
            """
        )

    with tab_shopee:
        st.markdown(
            """
            Na **Shopee**, a análise é centrada no comportamento do usuário dentro do aplicativo e no **Funil de Conversão**. Monitoramos o caminho desde a visita até o pedido pago para identificar onde você está perdendo dinheiro.
            
            A **Taxa de Rejeição** é um indicador crucial: ela mede a porcentagem de visitantes que chegam à sua página de produto e a abandonam imediatamente, sem interagir (clicar em fotos, ler descrição, adicionar ao carrinho). Uma taxa de rejeição alta indica que a **primeira impressão** do seu anúncio (foto principal, título, preço) não foi atrativa o suficiente para reter o interesse do comprador. Isso pode ser causado por imagens de baixa qualidade, títulos confusos ou irrelevantes, ou um preço que não se alinha às expectativas. Uma alta rejeição não só afasta clientes, mas também sinaliza para o algoritmo da Shopee que seu anúncio pode não ser relevante, impactando negativamente seu posicionamento nas buscas.
            
            A métrica de **Conversão de Carrinho** revela se o problema está na oferta final. Muitos itens adicionados ao carrinho que não viram pedidos pagos sugerem que o valor do frete ou a falta de cupons competitivos está fazendo o cliente desistir no último momento. Como a Shopee é uma plataforma predominantemente mobile, verifique sempre se sua comunicação visual está otimizada para telas pequenas.
            
            | Métrica Shopee | O que observar | Ação Recomendada |
            | :--- | :--- | :--- |
            | **Taxa de Rejeição** | % de visitantes que abandonam a página | Revise a foto principal, título e preço para serem mais atrativos. |
            | **Conversão de Carrinho** | Relação Add Carrinho vs Pedidos | Teste "Cupom de Seguidor" ou "Oferta Relâmpago". |
            | **Tráfego PC vs App** | Origem das visitas | Otimize imagens e textos para leitura em dispositivos móveis. |
            """
        )

    with tab_amazon:
        st.markdown(
            """
            Na **Amazon**, a métrica absoluta é a **Buy Box (Oferta em Destaque)**. Perder a Buy Box significa, na prática, ficar invisível para a grande maioria dos compradores. Se sua porcentagem de Buy Box cair abaixo de 90% em produtos de Curva "A", você tem uma emergência operacional que pode ser causada por preços desalinhados, falta de estoque FBA ou problemas na saúde da conta.
            
            Analisamos também o equilíbrio entre **Sessões e Conversão (Unit Session Percentage)**. Se o produto tem muitas sessões mas baixa conversão, o problema é a oferta (preço, avaliações ou descrição). Se a conversão é alta mas as sessões são baixas, o problema é o tráfego, exigindo melhorias em SEO ou maior investimento em Amazon Advertising.
            
            | Métrica Amazon | O que observar | Ação Recomendada |
            | :--- | :--- | :--- |
            | **Buy Box %** | Tempo como oferta principal | Verifique competitividade de preço e disponibilidade FBA. |
            | **Sessões** | Volume de tráfego no ASIN | Melhore palavras-chave de busca ou invista em Sponsored Products. |
            | **Unit Session %** | Taxa de conversão real | Revise imagens secundárias, vídeos e descrição A+. |
            """
        )

    st.markdown("---")

    # Seção 3: Boas Práticas e Ciclo de Análise
    st.markdown("### 📈 Ciclo de Análise e Boas Práticas")
    
    st.markdown(
        """
        Para manter uma operação saudável e em crescimento, recomendamos um **Ciclo Semanal de Análise**. Compare sempre o desempenho de curto prazo (30 dias) com o histórico de médio prazo (90-120 dias). Produtos que mantêm a estabilidade na Curva "A" são suas "Vacas Leiteiras" e devem ter o estoque protegido a qualquer custo.
        
        Evite manipular os arquivos de origem. Abrir um CSV no Excel e salvá-lo novamente pode alterar formatos de data e separadores decimais, impedindo que a ferramenta processe os dados corretamente. Sempre realize o upload do arquivo exatamente como ele foi exportado do marketplace para garantir a precisão total dos indicadores.
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
