"""
Componentes de UI específicos para a Shopee.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def render_shopee_conversion_funnel(df_export: pd.DataFrame):
    """
    Renderiza as métricas de conversão da Shopee: funil + origem do tráfego.
    
    Etapas: Visitantes → Add ao Carrinho → Pedidos → Pagos
    """
    st.markdown("### 📊 Métricas de Conversão")
    
    # Layout de 2 colunas
    col_funil, col_origem = st.columns(2)
    
    with col_funil:
        st.markdown("**Funil de Conversão**")
        # Agrega métricas
        total_visitantes = df_export['_shopee_visitantes'].sum()
        total_add_carrinho = df_export['_shopee_add_carrinho'].sum()
        total_pedidos = df_export['Qtd total'].sum()  # Pedidos realizados
        total_compradores = df_export['_shopee_compradores'].sum()  # Pedidos pagos
        
        # Prepara dados para o gráfico de funil
        fig = go.Figure(go.Funnel(
            y = ["Visitantes", "Add Carrinho", "Pedidos", "Pagos"],
            x = [total_visitantes, total_add_carrinho, total_pedidos, total_compradores],
            textinfo = "value+percent initial",
            marker = {"color": ["#60a5fa", "#34d399", "#fbbf24", "#4ade80"]}
        ))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=20),
            font=dict(color='#9ca3af'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_origem:
        st.markdown("**Origem do Tráfego**")
        # Verifica se há dados de PC/App
        if '_shopee_visitantes_pc' in df_export.columns and '_shopee_visitantes_app' in df_export.columns:
            visitantes_pc = df_export['_shopee_visitantes_pc'].iloc[0]
            visitantes_app = df_export['_shopee_visitantes_app'].iloc[0]
            
            if visitantes_pc > 0 or visitantes_app > 0:
                # Cria gráfico de pizza para PC vs Aplicativo
                fig_origem = go.Figure(data=[go.Pie(
                    labels=['Aplicativo', 'PC'],
                    values=[visitantes_app, visitantes_pc],
                    marker=dict(
                        colors=['#FF6B6B', '#4ECDC4'],
                        line=dict(color='rgba(255,255,255,0.3)', width=2)
                    ),
                    textfont=dict(size=14, color='white', family='Inter'),
                    textposition='inside',
                    textinfo='label+value+percent',
                    hole=0.4  # Donut chart
                )])
                
                fig_origem.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20, r=20, t=20, b=20),
                    font=dict(color='#9ca3af'),
                    height=400,
                    showlegend=True,
                    legend=dict(
                        font=dict(color='#ffffff'),
                        bgcolor='rgba(0,0,0,0)'
                    )
                )
                
                st.plotly_chart(fig_origem, use_container_width=True)
            else:
                st.info("📊 Dados de origem do tráfego zerados. Verifique o arquivo traffic_overview.")
        else:
            st.info("📊 Dados de origem do tráfego não disponíveis. Faça upload do arquivo traffic_overview para visualizar.")
    
    # Calcula taxas de conversão
    taxa_carrinho = (total_add_carrinho / total_visitantes * 100) if total_visitantes > 0 else 0
    taxa_pedido = (total_pedidos / total_visitantes * 100) if total_visitantes > 0 else 0
    taxa_pagamento = (total_compradores / total_pedidos * 100) if total_pedidos > 0 else 0
    
    # Exibe métricas de conversão em cards
    from app import render_metric_grid
    render_metric_grid([
        ("Taxa Add Carrinho", f"{taxa_carrinho:.2f}%", "🛒", "blue"),
        ("Taxa Pedido", f"{taxa_pedido:.2f}%", "📦", "amber"),
        ("Taxa Pagamento", f"{taxa_pagamento:.2f}%", "💰", "green")
    ])


def render_shopee_engagement_metrics(df_export: pd.DataFrame):
    """
    Renderiza métricas de engajamento da Shopee.
    """
    # Calcula médias ponderadas
    total_visitantes = df_export['_shopee_visitantes'].sum()
    total_visualizacoes = df_export['_shopee_visualizacoes'].sum()
    
    # Taxa de rejeição média ponderada
    if total_visitantes > 0:
        taxa_rejeicao_media = (df_export['_shopee_taxa_rejeicao'] * df_export['_shopee_visitantes']).sum() / total_visitantes
        taxa_conversao_media = (df_export['_shopee_taxa_conversao'] * df_export['_shopee_visitantes']).sum() / total_visitantes
        viz_por_visitante = total_visualizacoes / total_visitantes
    else:
        taxa_rejeicao_media = 0
        taxa_conversao_media = 0
        viz_por_visitante = 0
    
    st.markdown("### 📈 Métricas de Engajamento")
    
    from app import render_metric_grid
    render_metric_grid([
        ("Taxa de Rejeição", f"{taxa_rejeicao_media*100:.1f}%", "📉", "rose"),
        ("Visualizações/Visitante", f"{viz_por_visitante:.2f}", "👀", "blue"),
        ("Taxa de Conversão", f"{taxa_conversao_media*100:.2f}%", "🎯", "green"),
        ("Total de Visitantes", f"{int(total_visitantes):,}", "👥", "purple")
    ])


def render_shopee_top_rejection_rate(df_export: pd.DataFrame):
    """
    Renderiza os Top 5 produtos com maior taxa de rejeição
    """
    st.markdown("### ⚠️ Top 5 Produtos com Maior Taxa de Rejeição")
    
    # Filtrar produtos com dados válidos
    df_valid = df_export[
        (df_export['_shopee_taxa_rejeicao'].notna()) & 
        (df_export['_shopee_taxa_rejeicao'] > 0) &
        (df_export['_shopee_visitantes'] > 0)
    ].copy()
    
    if df_valid.empty:
        st.info("⚠️ Não há dados de taxa de rejeição disponíveis.")
        return
    
    # Ordenar por taxa de rejeição (maior para menor) e pegar top 5
    top_rejection = df_valid.nlargest(5, '_shopee_taxa_rejeicao')[[
        'SKU', 'Título', '_shopee_taxa_rejeicao', '_shopee_visitantes', 
        '_shopee_taxa_conversao', 'Fat total'
    ]].copy()
    
    # Formatar valores para exibição
    top_rejection['_shopee_taxa_rejeicao'] = top_rejection['_shopee_taxa_rejeicao'].apply(lambda x: f"{x*100:.1f}%")
    top_rejection['_shopee_taxa_conversao'] = top_rejection['_shopee_taxa_conversao'].apply(lambda x: f"{x*100:.2f}%")
    top_rejection['Fat total'] = top_rejection['Fat total'].apply(lambda x: f"R$ {x:,.2f}")
    
    st.dataframe(
        top_rejection,
        use_container_width=True,
        hide_index=True
    )


def render_shopee_abc_distribution(df_export: pd.DataFrame):
    """
    Renderiza a distribuição da curva ABC para Shopee.
    """
    st.markdown("### 📊 Distribuição ABC (Shopee)")
    
    dist = df_export['Curva 0-30'].value_counts().reindex(['A', 'B', 'C', '-']).fillna(0)
    
    fig = px.bar(
        x=dist.index,
        y=dist.values,
        labels={'x': 'Curva', 'y': 'Quantidade de Anúncios'},
        color=dist.index,
        color_discrete_map={'A': '#22c55e', 'B': '#fbbf24', 'C': '#ef4444', '-': '#9ca3af'}
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_shopee_top_products(df_export: pd.DataFrame, top_n=10):
    """
    Renderiza os top produtos da Shopee.
    """
    st.markdown(f"### 🏆 Top {top_n} Produtos por Faturamento")
    
    top_df = df_export.sort_values(by='Fat total', ascending=False).head(top_n)
    
    display_df = top_df[['SKU', 'Título', 'Qtd total', 'Fat total', 'Curva 0-30']].copy()
    display_df['Fat total'] = display_df['Fat total'].apply(lambda x: f"R$ {x:,.2f}")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def get_shopee_alerts(df_export: pd.DataFrame):
    """
    Retorna alertas específicos para a Shopee.
    """
    alerts = []
    
    # Alerta de Rejeição Alta
    high_rejection = df_export[
        (df_export['_shopee_taxa_rejeicao'] > 0.5) & 
        (df_export['_shopee_visitantes'] > 50)
    ].sort_values(by='Fat total', ascending=False)
    
    for _, row in high_rejection.head(3).iterrows():
        alerts.append({
            'SKU': row['SKU'],
            'Título': row['Título'],
            'Motivo': f"Taxa de Rejeição Alta: {row['_shopee_taxa_rejeicao']*100:.1f}%",
            'Ação': "Melhorar fotos e descrição do anúncio."
        })
        
    # Alerta de Conversão Baixa
    low_conv = df_export[
        (df_export['_shopee_taxa_conversao'] < 0.01) & 
        (df_export['_shopee_visitantes'] > 100)
    ].sort_values(by='_shopee_visitantes', ascending=False)
    
    for _, row in low_conv.head(3).iterrows():
        alerts.append({
            'SKU': row['SKU'],
            'Título': row['Título'],
            'Motivo': f"Conversão Baixa: {row['_shopee_taxa_conversao']*100:.2f}%",
            'Ação': "Revisar preço e competitividade."
        })
        
    return alerts
