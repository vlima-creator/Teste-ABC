import streamlit as st
import pandas as pd
import plotly.express as px
from ui.components.helpers import br_money, pct

def render_amazon_buybox_metrics(df_export):
    """Renderiza métricas de Buybox para Amazon."""
    if 'Buy Box %' not in df_export.columns:
        return

    st.markdown("### 📦 Performance de Buybox (Oferta em Destaque)")
    
    # Cálculos
    avg_buybox = df_export['Buy Box %'].mean()
    ganhando = df_export[df_export['Buy Box %'] >= 80]
    perdendo = df_export[df_export['Buy Box %'] < 80]
    
    pct_ganhando = (len(ganhando) / len(df_export)) * 100 if len(df_export) > 0 else 0
    pct_perdendo = (len(perdendo) / len(df_export)) * 100 if len(df_export) > 0 else 0

    # Cards de Métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Média de Buybox", f"{avg_buybox:.1f}%")
    with col2:
        st.metric("Produtos Ganhando (>=80%)", f"{len(ganhando)}", f"{pct_ganhando:.1f}% do catálogo")
    with col3:
        st.metric("Produtos Perdendo (<80%)", f"{len(perdendo)}", f"-{pct_perdendo:.1f}% do catálogo", delta_color="inverse")

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
        # Mostrar produtos que estão perdendo e têm relevância (ordenados por faturamento ou Qtd)
        top_lost = df_export.sort_values(by=['Buy Box %', 'Fat total'], ascending=[True, False]).head(10)
        
        display_df = top_lost[['SKU', 'Título', 'Buy Box %', 'Fat total']].copy()
        display_df['Buy Box %'] = display_df['Buy Box %'].apply(lambda x: f"{x:.1f}%")
        display_df['Fat total'] = display_df['Fat total'].apply(br_money)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)

def get_amazon_buybox_alerts(df_export):
    """Retorna alertas específicos de Buybox para o plano de ação."""
    alerts = []
    if 'Buy Box %' not in df_export.columns:
        return alerts
        
    critical = df_export[df_export['Buy Box %'] < 50].sort_values(by='Fat total', ascending=False)
    for _, row in critical.head(5).iterrows():
        alerts.append({
            'SKU': row['SKU'],
            'Título': row['Título'],
            'Motivo': f"Buybox Crítica: {row['Buy Box %']:.1f}%",
            'Ação': "Verificar preço da concorrência e saúde da conta."
        })
    return alerts
