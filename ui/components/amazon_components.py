import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ui.components.helpers import br_money, pct, to_xlsx_bytes
from ui.components.shared_ui import render_metric_grid, render_report_section

def render_amazon_buybox_metrics(df_export):
    """Renderiza métricas de Buybox para Amazon."""
    if 'Buy Box %' not in df_export.columns:
        return

    st.markdown(render_report_section("package", "Performance de Buybox", "Análise da Oferta em Destaque por SKU", "blue"), unsafe_allow_html=True)
    
    # Cálculos
    avg_buybox = df_export['Buy Box %'].mean()
    ganhando = df_export[df_export['Buy Box %'] >= 80]
    perdendo = df_export[df_export['Buy Box %'] < 80]
    
    # Cards de Métricas
    render_metric_grid([
        ("Média de Buybox", f"{avg_buybox:.1f}%", "package", "blue"),
        ("Produtos Ganhando (>=80%)", f"{len(ganhando)}", "star", "green"),
        ("Produtos Perdendo (<80%)", f"{len(perdendo)}", "alert-triangle", "rose")
    ])

    # Botão de Download do Relatório de Buybox
    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
    
    # Preparar dados para o relatório de Buybox
    df_buybox_report = df_export[['SKU', 'Título', 'Buy Box %', 'Fat total', 'Qtd total']].copy()
    
    # Adicionar métricas extras se disponíveis
    if '_amazon_sessions' in df_export.columns:
        df_buybox_report['Sessões'] = df_export['_amazon_sessions']
    if '_amazon_conv_rate' in df_export.columns:
        df_buybox_report['Taxa de Conversão'] = df_export['_amazon_conv_rate'] / 100 # to_xlsx_bytes formata como %
        
    # Adicionar coluna de Diagnóstico e Ação (Baseado no Guia Completo)
    def get_buybox_action(row):
        bb = row['Buy Box %']
        if bb >= 80:
            return "Dominância: Forte presença na Buy Box. Atenção para não comprometer margem sem necessidade."
        elif bb >= 60:
            return "Bom: Boa participação, mas há espaço para otimização de preço ou logística."
        elif bb >= 20:
            return "Disputa: Você divide a rotação. Testar pequenos ajustes de preço ou avaliar migração para FBA."
        elif bb > 0:
            return "Crítico: Perda severa de destaque. Analisar concorrentes (preço final e logística) e métricas de conta."
        else:
            return "Ineligível/0%: Possível falta de elegibilidade, ruptura de estoque ou concorrente monopolizando com FBA."
            
    df_buybox_report['Diagnóstico'] = df_buybox_report.apply(get_buybox_action, axis=1)
    
    # Ordenar por menor Buybox e maior faturamento (prioridade de correção)
    df_buybox_report = df_buybox_report.sort_values(by=['Buy Box %', 'Fat total'], ascending=[True, False])
    
    # Formatação para o Excel
    df_buybox_report = df_buybox_report.rename(columns={
        'Buy Box %': 'Taxa Buy Box %',
        'Fat total': 'Faturamento (BRL)',
        'Qtd total': 'Quantidade Vendida'
    })
    
    st.download_button(
        label="📥 Baixar Relatório de Performance de Buybox (Excel)",
        data=to_xlsx_bytes(df_buybox_report),
        file_name="performance_buybox_amazon.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    # Gráfico e Tabela
    col_chart, col_table = st.columns([1, 1])
    
    with col_chart:
        fig_data = pd.DataFrame({
            'Status': ['Ganhando', 'Perdendo'],
            'Quantidade': [len(ganhando), len(perdendo)]
        })
        fig = px.pie(fig_data, values='Quantidade', names='Status', 
                     title="Distribuição de Buybox",
                     color_discrete_map={'Ganhando': '#22c55e', 'Perdendo': '#ef4444'},
                     hole=0.4)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.markdown("#### Top 10 Produtos com Menor Buybox")
        top_lost = df_export.sort_values(by=['Buy Box %', 'Fat total'], ascending=[True, False]).head(10)
        
        display_df = top_lost[['SKU', 'Título', 'Buy Box %', 'Fat total']].copy()
        display_df['Buy Box %'] = display_df['Buy Box %'].apply(lambda x: f"{x:.1f}%")
        display_df['Fat total'] = display_df['Fat total'].apply(br_money)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)

def render_amazon_conversion_metrics(df_export):
    """Renderiza funil de conversão para Amazon."""
    if '_amazon_sessions' not in df_export.columns:
        return

    st.markdown(render_report_section("target", "Funil de Conversão", "Comportamento de compra na Amazon", "green"), unsafe_allow_html=True)
    
    total_sessions = df_export['_amazon_sessions'].sum()
    total_units = df_export['Qtd total'].sum()
    avg_conv = (total_units / total_sessions * 100) if total_sessions > 0 else 0.0
    
    render_metric_grid([
        ("Total de Sessões", f"{int(total_sessions):,}", "activity", "blue"),
        ("Unidades Pedidas", f"{int(total_units):,}", "package", "amber"),
        ("Taxa de Conversão Média", f"{avg_conv:.2f}%", "target", "green")
    ])

    # Gráfico de Funil
    fig = go.Figure(go.Funnel(
        y = ["Sessões", "Unidades Pedidas"],
        x = [total_sessions, total_units],
        textinfo = "value+percent initial",
        marker = {"color": ["#636EFA", "#00CC96"]}
    ))
    fig.update_layout(title="Funil de Vendas", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig, use_container_width=True)

def render_amazon_engagement_metrics(df_export):
    """Renderiza métricas de engajamento para Amazon."""
    if '_amazon_page_views' not in df_export.columns:
        return

    st.markdown(render_report_section("trending-up", "Engajamento e Tráfego", "Visualizações e comportamento por sessão", "purple"), unsafe_allow_html=True)
    
    total_pv = df_export['_amazon_page_views'].sum()
    total_sessions = df_export['_amazon_sessions'].sum() if '_amazon_sessions' in df_export.columns else 0
    pv_per_session = (total_pv / total_sessions) if total_sessions > 0 else 0
    
    render_metric_grid([
        ("Visualizações de Página", f"{int(total_pv):,}", "search", "blue"),
        ("Páginas / Sessão", f"{pv_per_session:.2f}", "bar-chart-3", "purple")
    ])

    # Top 10 Produtos por Sessões
    st.markdown("#### Top 10 Produtos com Mais Tráfego")
    top_traffic = df_export.sort_values(by='_amazon_sessions', ascending=False).head(10)
    display_df = top_traffic[['SKU', 'Título', '_amazon_sessions', 'Qtd total']].copy()
    if '_amazon_conv_rate' in top_traffic.columns:
        display_df['Conversão'] = top_traffic['_amazon_conv_rate'].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def get_amazon_buybox_alerts(df_export):
    """Retorna alertas específicos de Buybox para o plano de ação baseados no Guia Completo."""
    alerts = []
    if 'Buy Box %' not in df_export.columns:
        return alerts
        
    # 1. Crítico / Sem Elegibilidade (< 20%)
    critical = df_export[df_export['Buy Box %'] < 20].sort_values(by='Fat total', ascending=False)
    for _, row in critical.head(5).iterrows():
        bb = row['Buy Box %']
        motivo = f"Buybox Crítica: {bb:.1f}%" if bb > 0 else "Buybox 0% (Ineligível?)"
        acao = "Checar elegibilidade, comparar preço final com detentor da Buy Box e revisar saúde da conta."
        alerts.append({
            'SKU': row['SKU'],
            'Título': row['Título'],
            'Motivo': motivo,
            'Ação': acao
        })
        
    # 2. Alerta de Disputa (20% - 60%)
    dispute = df_export[(df_export['Buy Box %'] >= 20) & (df_export['Buy Box %'] <= 60)].sort_values(by='Fat total', ascending=False)
    for _, row in dispute.head(3).iterrows():
        alerts.append({
            'SKU': row['SKU'],
            'Título': row['Título'],
            'Motivo': f"Disputa de Buybox: {row['Buy Box %']:.1f}%",
            'Ação': "Ajuste fino em preço/logística. Avaliar migração para FBA ou melhoria de prazos FBM."
        })
    
    # Alertas de Conversão
    if '_amazon_conv_rate' in df_export.columns:
        low_conv = df_export[(df_export['_amazon_conv_rate'] < 1.0) & (df_export['_amazon_sessions'] > 100)].sort_values(by='_amazon_sessions', ascending=False)
        for _, row in low_conv.head(3).iterrows():
            alerts.append({
                'SKU': row['SKU'],
                'Título': row['Título'],
                'Motivo': f"Conversão Baixa: {row['_amazon_conv_rate']:.2f}%",
                'Ação': "Otimizar imagens, descrição e verificar avaliações."
            })
            
    return alerts
