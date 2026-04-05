import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from ui.components.shared_ui import render_metric_grid, get_svg_icon, render_report_section

def render_shopee_conversion_funnel(df_export: pd.DataFrame):
    st.markdown(render_report_section("target", "Métricas de Conversão", "Funil de vendas e origem do tráfego na Shopee", "blue"), unsafe_allow_html=True)
    
    col_funil, col_origem = st.columns(2)
    
    with col_funil:
        st.markdown("<div style=\'text-align: center; font-weight: bold; margin-bottom: 10px;\'>Funil de Conversão</div>", unsafe_allow_html=True)
        
        total_visitantes = df_export["_shopee_visitantes"].sum() if "_shopee_visitantes" in df_export.columns else 0
        total_add_carrinho = df_export["_shopee_add_carrinho"].sum() if "_shopee_add_carrinho" in df_export.columns else 0
        total_pedidos = df_export["Qtd total"].sum() if "Qtd total" in df_export.columns else 0
        total_compradores = df_export["_shopee_compradores"].sum() if "_shopee_compradores" in df_export.columns else 0
        
        if total_visitantes > 0:
            colors = ["#60a5fa", "#34d399", "#fbbf24", "#4ade80"]
            labels = ["Visitantes", "Add Carrinho", "Pedidos", "Pagos"]
            values = [total_visitantes, total_add_carrinho, total_pedidos, total_compradores]
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.5,
                marker=dict(colors=colors),
                textinfo="label+value+percent",
                textposition="inside",
                insidetextorientation="horizontal",
                sort=False
            )])
            
            fig.update_layout(
                showlegend=True,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                height=400,
                legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.0)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o funil de conversão.")
    
    with col_origem:
        st.markdown("<div style=\'text-align: center; font-weight: bold; margin-bottom: 10px;\'>Origem do Tráfego</div>", unsafe_allow_html=True)
        
        if "_shopee_visitantes_pc" in df_export.columns and "_shopee_visitantes_app" in df_export.columns:
            visitantes_pc = df_export["_shopee_visitantes_pc"].sum()
            visitantes_app = df_export["_shopee_visitantes_app"].sum()
            
            if visitantes_pc > 0 or visitantes_app > 0:
                fig_origem = go.Figure(data=[go.Pie(
                    labels=["Aplicativo", "PC"],
                    values=[visitantes_app, visitantes_pc],
                    hole=0.5,
                    marker=dict(colors=["#FF6B6B", "#4ECDC4"]),
                    textinfo="label+value+percent",
                    textposition="inside",
                    insidetextorientation="horizontal"
                )])
                
                fig_origem.update_layout(
                    showlegend=True,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=400,
                    legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.0)
                )
                st.plotly_chart(fig_origem, use_container_width=True)
            else:
                st.info("Dados de origem do tráfego zerados.")
        else:
            st.info("Dados de origem do tráfego não disponíveis.")
    
    taxa_carrinho = (total_add_carrinho / total_visitantes * 100) if total_visitantes > 0 else 0
    taxa_pedido = (total_compradores / total_visitantes * 100) if total_visitantes > 0 else 0
    taxa_pagamento = (total_compradores / total_add_carrinho * 100) if total_add_carrinho > 0 else 0
    
    render_metric_grid([
        ("Taxa Add Carrinho", f"{taxa_carrinho:.2f}%", "package", "blue"),
        ("Taxa Pedido", f"{taxa_pedido:.2f}%", "package", "amber"),
        ("Taxa Pagamento", f"{taxa_pagamento:.2f}%", "dollar-sign", "green")
    ])

def render_shopee_engagement_metrics(df_export: pd.DataFrame):
    total_visitantes = df_export["_shopee_visitantes"].sum() if "_shopee_visitantes" in df_export.columns else 0
    total_visualizacoes = df_export["_shopee_visualizacoes"].sum() if "_shopee_visualizacoes" in df_export.columns else 0
    
    taxa_rejeicao_media = 0
    taxa_conversao_media = 0
    viz_por_visitante = 0
    
    if total_visitantes > 0:
        if "_shopee_taxa_rejeicao" in df_export.columns:
            taxa_rejeicao_media = (df_export["_shopee_taxa_rejeicao"] * df_export["_shopee_visitantes"]).sum() / total_visitantes
        if "_shopee_taxa_conversao" in df_export.columns:
            taxa_conversao_media = (df_export["_shopee_taxa_conversao"] * df_export["_shopee_visitantes"]).sum() / total_visitantes
        viz_por_visitante = total_visualizacoes / total_visitantes
    
    st.markdown(render_report_section("trending-up", "Métricas de Engajamento", "Comportamento do usuário e retenção", "green"), unsafe_allow_html=True)
    
    render_metric_grid([
        ("Taxa de Rejeição", f"{taxa_rejeicao_media*100:.1f}%", "alert-triangle", "rose"),
        ("Visualizações/Visitante", f"{viz_por_visitante:.2f}", "search", "blue"),
        ("Taxa de Conversão", f"{taxa_conversao_media*100:.2f}%", "target", "green"),
        ("Total de Visitantes", f"{int(total_visitantes):,}", "activity", "purple")
    ])

    if "_shopee_taxa_rejeicao" in df_export.columns:
        high_rejection_df = df_export[
            (df_export["_shopee_taxa_rejeicao"] > 0.5) & 
            (df_export["_shopee_visitantes"] >= 50)
        ].sort_values("_shopee_taxa_rejeicao", ascending=False)

        if not high_rejection_df.empty:
            count = len(high_rejection_df)
            top_prod = high_rejection_df.iloc[0]
            
            lightbulb_svg = get_svg_icon("lightbulb")
            
            st.markdown(f"""
            <div class=\'insight-card\' style=\'margin-top: 20px; border-left: 4px solid #fbbf24;\'>
              <div class=\'insight-icon\' style=\'color: #fbbf24;\'>{lightbulb_svg}</div>
              <div>
                <div class=\'insight-title\'>Ações Recomendadas: Alta Taxa de Rejeição</div>
                <div class=\'insight-text\'>
                    Identificamos <b>{count} produtos</b> com taxa de rejeição acima de 50%. <br/>
                    <b>Destaque:</b> {top_prod["Título"]} ({top_prod["_shopee_taxa_rejeicao"]*100:.1f}% de rejeição). <br/>
                    <i>Sugestão: Revise as fotos principais, o título e o preço para aumentar a retenção dos visitantes.</i>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

def render_shopee_top_rejection_rate(df_export: pd.DataFrame):
    st.markdown(render_report_section("alert-triangle", "Top 5 Produtos com Maior Taxa de Rejeição", "Produtos que mais precisam de atenção imediata", "rose"), unsafe_allow_html=True)
    
    df_valid = df_export[
        (df_export["_shopee_taxa_rejeicao"].notna()) & 
        (df_export["_shopee_taxa_rejeicao"] > 0) &
        (df_export["_shopee_visitantes"] > 0)
    ].copy()
    
    if df_valid.empty:
        st.info("Não há dados de taxa de rejeição disponíveis.")
        return
    
    top_rejection = df_valid.nlargest(5, "_shopee_taxa_rejeicao")[[
        "SKU", "Título", "_shopee_taxa_rejeicao", "_shopee_visitantes", 
        "_shopee_taxa_conversao", "Fat total"
    ]].copy()
    
    top_rejection["_shopee_taxa_rejeicao"] = top_rejection["_shopee_taxa_rejeicao"].apply(lambda x: f"{x*100:.1f}%")
    top_rejection["_shopee_taxa_conversao"] = top_rejection["_shopee_taxa_conversao"].apply(lambda x: f"{x*100:.2f}%")
    top_rejection["Fat total"] = top_rejection["Fat total"].apply(lambda x: f"R$ {x:,.2f}")
    
    st.dataframe(top_rejection, use_container_width=True, hide_index=True)

def render_shopee_abc_distribution(df_export: pd.DataFrame):
    st.markdown(render_report_section("bar-chart-3", "Distribuição ABC (Shopee)", "Distribuição do catálogo por curva de faturamento", "blue"), unsafe_allow_html=True)
    
    dist = df_export["Curva 0-30"].value_counts().reindex(["A", "B", "C", "-"]).fillna(0)
    
    fig = px.bar(
        x=dist.index,
        y=dist.values,
        labels={"x": "Curva", "y": "Quantidade de Anúncios"},
        color=dist.index,
        color_discrete_map={"A": "#22c55e", "B": "#fbbf24", "C": "#ef4444", "-": "#9ca3af"}
    )
    
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_shopee_top_products(df_export: pd.DataFrame, top_n=10):
    st.markdown(render_report_section("award", f"Top {top_n} Produtos por Faturamento", "Os produtos que mais contribuem para o seu resultado", "green"), unsafe_allow_html=True)
    
    top_df = df_export.sort_values(by="Fat total", ascending=False).head(top_n)
    
    display_df = top_df[["SKU", "Título", "Qtd total", "Fat total", "Curva 0-30"]].copy()
    display_df["Fat total"] = display_df["Fat total"].apply(lambda x: f"R$ {x:,.2f}")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def get_shopee_alerts(df_export: pd.DataFrame):
    alerts = []
    
    if "_shopee_taxa_rejeicao" in df_export.columns and "_shopee_visitantes" in df_export.columns:
        high_rejection = df_export[
            (df_export["_shopee_taxa_rejeicao"] > 0.5) & 
            (df_export["_shopee_visitantes"] > 50)
        ].sort_values(by="Fat total", ascending=False)
        
        for _, row in high_rejection.head(3).iterrows():
            alerts.append({
                "SKU": row["SKU"],
                "Título": row["Título"],
                "Motivo": f"Taxa de Rejeição Alta: {row["_shopee_taxa_rejeicao"]*100:.1f}%",
                "Ação": "Melhorar fotos e descrição do anúncio."
            })
        
    if "_shopee_taxa_conversao" in df_export.columns and "_shopee_visitantes" in df_export.columns:
        low_conv = df_export[
            (df_export["_shopee_taxa_conversao"] < 0.01) & 
            (df_export["_shopee_visitantes"] > 100)
        ].sort_values(by="_shopee_visitantes", ascending=False)
        
        for _, row in low_conv.head(3).iterrows():
            alerts.append({
                "SKU": row["SKU"],
                "Título": row["Título"],
                "Motivo": f"Conversão Baixa: {row["_shopee_taxa_conversao"]*100:.2f}%",
                "Ação": "Revisar preço e competitividade."
            })
        
    return alerts
