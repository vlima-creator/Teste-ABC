"""
Aba de Warning Semanal - Monitoramento ágil de performance de vendas.
Foca em análise semanal com alertas de mudança de curva ABC.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from ui.components.helpers import br_money, br_int, safe_div, pct, to_xlsx_bytes, ensure_cols
from ui.components.shared_ui import render_metric_grid, get_svg_icon
from data_processing.weekly_analyzer import WeeklyAnalyzer


def render_warning_semanal_tab(df_export: pd.DataFrame, df_raw: pd.DataFrame = None):
    """
    Renderiza a aba de Warning Semanal com análise de performance semanal.
    
    Args:
        df_export: DataFrame principal com dados de vendas
        df_raw: DataFrame bruto com colunas de data para cálculo semanal
    """
    
    # Se não temos dados brutos, tenta extrair do df_export
    if df_raw is None or df_raw.empty:
        st.warning("⚠️ Dados brutos não disponíveis para análise semanal detalhada. Usando dados agregados.")
        # Usar dados agregados disponíveis
        df_analysis = df_export.copy()
    else:
        # Calcular análise semanal a partir dos dados brutos
        df_analysis = WeeklyAnalyzer.calculate_weekly_curves(df_raw)
        if df_analysis.empty:
            st.error("Erro ao processar dados semanais.")
            return
        
        # Adicionar cálculos de warning
        df_analysis = WeeklyAnalyzer.calculate_warnings(df_analysis)
    
    # ===== HEADER =====
    st.markdown(
        """
        <div class="hero-header">
            <h1 class="hero-title">⚠️ Warning Semanal</h1>
            <p class="hero-subtitle">Monitoramento ágil de performance com alertas de mudança de curva ABC</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # ===== RESUMO DE ALERTAS =====
    if 'Status Warning' in df_analysis.columns:
        warning_summary = df_analysis['Status Warning'].value_counts().to_dict()
        
        metrics = []
        metrics.append((
            warning_summary.get('🔴 Queda Crítica', 0),
            'Quedas Críticas',
            'alert-circle',
            'rose'
        ))
        metrics.append((
            warning_summary.get('🟡 Atenção', 0),
            'Atenção',
            'alert-triangle',
            'amber'
        ))
        metrics.append((
            warning_summary.get('🟢 Recuperação', 0),
            'Recuperações',
            'trending-up',
            'green'
        ))
        metrics.append((
            warning_summary.get('🟢 Estável', 0),
            'Estáveis',
            'check-circle',
            'blue'
        ))
        
        st.markdown(render_metric_grid(metrics), unsafe_allow_html=True)
    
    # ===== SELETOR DE VISÃO =====
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        view_mode = st.radio(
            "Escolha a visão:",
            ["📊 Volume", "💰 Faturamento", "📈 Curva ABC"],
            horizontal=False
        )
    
    # ===== FILTROS =====
    with col2:
        st.markdown("**Filtrar por Status:**")
        if 'Status Warning' in df_analysis.columns:
            status_options = df_analysis['Status Warning'].unique().tolist()
            selected_status = st.multiselect(
                "Status",
                status_options,
                default=status_options,
                label_visibility="collapsed"
            )
            df_filtered = df_analysis[df_analysis['Status Warning'].isin(selected_status)]
        else:
            df_filtered = df_analysis
    
    with col3:
        st.markdown("**Buscar Produto:**")
        search_term = st.text_input(
            "Buscar",
            value="",
            label_visibility="collapsed",
            placeholder="MLB ou Título..."
        )
        if search_term:
            search_lower = search_term.lower()
            df_filtered = df_filtered[
                (df_filtered['MLB'].astype(str).str.lower().str.contains(search_lower)) |
                (df_filtered['Título'].astype(str).str.lower().str.contains(search_lower))
            ]
    
    st.markdown("---")
    
    # ===== VISÃO 1: VOLUME =====
    if view_mode == "📊 Volume":
        st.subheader("📊 Análise de Volume Semanal")
        
        # Preparar dados para visualização
        volume_cols = [col for col in df_filtered.columns if col.startswith('Qntd Sem')]
        if volume_cols:
            # Gráfico de evolução
            chart_data = df_filtered[['MLB', 'Título'] + volume_cols].head(10).copy()
            chart_data['Produto'] = chart_data['MLB'] + ' - ' + chart_data['Título'].astype(str).str[:30]
            
            # Preparar dados para gráfico
            plot_data = []
            for _, row in chart_data.iterrows():
                for col in volume_cols:
                    semana = col.replace('Qntd ', '')
                    plot_data.append({
                        'Produto': row['Produto'],
                        'Semana': semana,
                        'Quantidade': row[col]
                    })
            
            if plot_data:
                plot_df = pd.DataFrame(plot_data)
                fig = px.line(
                    plot_df,
                    x='Semana',
                    y='Quantidade',
                    color='Produto',
                    markers=True,
                    title='Evolução de Vendas (Top 10 Produtos)',
                    labels={'Quantidade': 'Unidades Vendidas', 'Semana': 'Semana'}
                )
                fig.update_layout(
                    template='plotly_dark',
                    hovermode='x unified',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Tabela de volume
        st.markdown("**Detalhamento de Volume por Semana:**")
        volume_display = df_filtered[['MLB', 'Título'] + volume_cols + ['Qtd Total']].copy()
        volume_display = volume_display.sort_values('Qtd Total', ascending=False)
        
        # Formatar números
        for col in volume_cols + ['Qtd Total']:
            if col in volume_display.columns:
                volume_display[col] = volume_display[col].apply(br_int)
        
        st.dataframe(volume_display, use_container_width=True, hide_index=True, height=400)
        
        # Download
        st.download_button(
            "📥 Baixar Volume (Excel)",
            data=to_xlsx_bytes(df_filtered[['MLB', 'Título'] + volume_cols + ['Qtd Total']]),
            file_name="warning_volume.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    # ===== VISÃO 2: FATURAMENTO =====
    elif view_mode == "💰 Faturamento":
        st.subheader("💰 Análise de Faturamento Semanal")
        
        # Preparar dados para visualização
        fat_cols = [col for col in df_filtered.columns if col.startswith('Fat. Sem')]
        if fat_cols:
            # Gráfico de evolução
            chart_data = df_filtered[['MLB', 'Título'] + fat_cols].head(10).copy()
            chart_data['Produto'] = chart_data['MLB'] + ' - ' + chart_data['Título'].astype(str).str[:30]
            
            # Preparar dados para gráfico
            plot_data = []
            for _, row in chart_data.iterrows():
                for col in fat_cols:
                    semana = col.replace('Fat. ', '')
                    plot_data.append({
                        'Produto': row['Produto'],
                        'Semana': semana,
                        'Faturamento': row[col]
                    })
            
            if plot_data:
                plot_df = pd.DataFrame(plot_data)
                fig = px.line(
                    plot_df,
                    x='Semana',
                    y='Faturamento',
                    color='Produto',
                    markers=True,
                    title='Evolução de Faturamento (Top 10 Produtos)',
                    labels={'Faturamento': 'Faturamento (R$)', 'Semana': 'Semana'}
                )
                fig.update_layout(
                    template='plotly_dark',
                    hovermode='x unified',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Tabela de faturamento
        st.markdown("**Detalhamento de Faturamento por Semana:**")
        fat_display = df_filtered[['MLB', 'Título', 'Status Warning'] + fat_cols + ['Fat Total']].copy()
        fat_display = fat_display.sort_values('Fat Total', ascending=False)
        
        # Formatar valores
        for col in fat_cols + ['Fat Total']:
            if col in fat_display.columns:
                fat_display[col] = fat_display[col].apply(lambda x: br_money(float(x)) if pd.notna(x) else '-')
        
        st.dataframe(fat_display, use_container_width=True, hide_index=True, height=400)
        
        # Download
        st.download_button(
            "📥 Baixar Faturamento (Excel)",
            data=to_xlsx_bytes(df_filtered[['MLB', 'Título'] + fat_cols + ['Fat Total']]),
            file_name="warning_faturamento.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    # ===== VISÃO 3: CURVA ABC =====
    elif view_mode == "📈 Curva ABC":
        st.subheader("📈 Evolução de Curva ABC Semanal")
        
        # Preparar dados
        curva_cols = [col for col in df_filtered.columns if col.startswith('Curva Sem')]
        if curva_cols:
            # Tabela de curva ABC
            st.markdown("**Classificação ABC por Semana:**")
            curva_display = df_filtered[['MLB', 'Título', 'Status Warning'] + curva_cols].copy()
            curva_display = curva_display.sort_values('MLB')
            
            st.dataframe(curva_display, use_container_width=True, hide_index=True, height=400)
            
            # Distribuição de curvas por semana
            st.markdown("**Distribuição de Curvas por Semana:**")
            
            dist_data = []
            for col in curva_cols:
                semana = col.replace('Curva ', '')
                counts = df_filtered[col].value_counts()
                for curva in ['A', 'B', 'C', '-']:
                    dist_data.append({
                        'Semana': semana,
                        'Curva': curva,
                        'Quantidade': counts.get(curva, 0)
                    })
            
            if dist_data:
                dist_df = pd.DataFrame(dist_data)
                fig = px.bar(
                    dist_df,
                    x='Semana',
                    y='Quantidade',
                    color='Curva',
                    barmode='stack',
                    title='Distribuição de Produtos por Curva ABC',
                    color_discrete_map={'A': '#4ade80', 'B': '#fbbf24', 'C': '#ef4444', '-': '#9ca3af'}
                )
                fig.update_layout(
                    template='plotly_dark',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Download
        st.download_button(
            "📥 Baixar Curva ABC (Excel)",
            data=to_xlsx_bytes(df_filtered[['MLB', 'Título', 'Status Warning'] + curva_cols]),
            file_name="warning_curva_abc.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    # ===== ALERTAS DETALHADOS =====
    st.markdown("---")
    st.subheader("🚨 Alertas Detalhados")
    
    if 'Status Warning' in df_analysis.columns:
        # Filtrar apenas alertas críticos e atenção
        alertas = df_analysis[
            df_analysis['Status Warning'].isin(['🔴 Queda Crítica', '🟡 Atenção'])
        ].sort_values('Delta %', ascending=True).head(20)
        
        if not alertas.empty:
            alert_cols = ['MLB', 'Título', 'Status Warning', 'Curva Anterior', 'Curva Atual', 'Delta %']
            alert_display = alertas[alert_cols].copy()
            alert_display['Delta %'] = alert_display['Delta %'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(alert_display, use_container_width=True, hide_index=True, height=300)
        else:
            st.success("✅ Nenhum alerta crítico no momento!")
    
    # ===== INFORMAÇÕES ADICIONAIS =====
    st.markdown("---")
    with st.expander("ℹ️ Como interpretar os alertas"):
        st.markdown("""
        - **🔴 Queda Crítica**: Produto caiu de curva (A→B/C, B→C) - Requer ação imediata
        - **🟡 Atenção**: Faturamento caiu >30% mantendo curva - Monitorar de perto
        - **🟢 Recuperação**: Produto subiu de curva - Excelente desempenho
        - **🟢 Estável**: Mantém performance - Continuar estratégia atual
        
        **Buckets Semanais:**
        - **Sem1**: Últimos 7 dias
        - **Sem2**: 8-14 dias atrás
        - **Sem3**: 15-21 dias atrás
        - **Sem4**: 22-28 dias atrás
        - **Sem5**: 29-35 dias atrás
        """)
