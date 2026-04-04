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
    
    IMPORTANTE: Esta aba SEMPRE mostra apenas as últimas 5 semanas de dados,
    independentemente do período total do relatório carregado.
    
    Args:
        df_export: DataFrame principal com dados de vendas
        df_raw: DataFrame bruto com colunas de data para cálculo semanal
    """
    
    # Se não temos dados brutos, tenta extrair do df_export
    if df_raw is None or df_raw.empty:
        st.warning("⚠️ Dados brutos não disponíveis para análise semanal detalhada. Usando dados agregados de 30 dias.")
        # Usar dados agregados disponíveis
        df_analysis = df_export.copy()
        
        # Mapear colunas de 30 dias para o formato semanal (Sem1) para não quebrar a UI
        # Isso permite que Amazon e Shopee mostrem pelo menos o estado atual
        if 'Qntd 0-30' in df_analysis.columns:
            df_analysis['Qntd Sem1'] = df_analysis['Qntd 0-30']
            df_analysis['Fat. Sem1'] = df_analysis.get('Fat. 0-30', 0)
            df_analysis['Curva Sem1'] = df_analysis.get('Curva 0-30', '-')
            
            # Criar colunas vazias para as outras semanas para evitar erros de visualização
            for i in range(2, 6):
                df_analysis[f'Qntd Sem{i}'] = 0
                df_analysis[f'Fat. Sem{i}'] = 0.0
                df_analysis[f'Curva Sem{i}'] = '-'
        
        # Adicionar cálculos de warning (mesmo que vazios ou estáveis)
        df_analysis = WeeklyAnalyzer.calculate_warnings(df_analysis)
    else:
        # Calcular análise semanal a partir dos dados brutos
        # IMPORTANTE: WeeklyAnalyzer.calculate_weekly_curves() SEMPRE filtra para as últimas 5 semanas
        df_analysis = WeeklyAnalyzer.calculate_weekly_curves(df_raw)
        if df_analysis.empty:
            st.error("Não foi possível processar os dados semanais. Verifique se o arquivo contém colunas de Data, SKU/ID e Valores.")
            return
        
        # Adicionar cálculos de warning
        # IMPORTANTE: calculate_warnings() garante que APENAS as últimas 5 semanas são usadas
        df_analysis = WeeklyAnalyzer.calculate_warnings(df_analysis)
    
    # ===== HEADER =====
    from app import render_report_section
    st.markdown(
        render_report_section("⚠️", "Warning Semanal", "Monitoramento ágil de performance com alertas de mudança de curva ABC", "amber"),
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
    
    # Identificar colunas de ID e Título dinamicamente
    id_priority = ['MLB', 'ASIN (child)', 'SKU da Variação', 'SKU Principle', 'ID do Item', 'SKU', 'ASIN', 'ID']
    id_col = next((c for c in id_priority if c in df_analysis.columns), df_analysis.columns[0])
    
    title_priority = ['Título', 'Produto', 'Product Name', 'Nome do Produto', 'Item Name', 'titulo']
    title_col = next((c for c in title_priority if c in df_analysis.columns), df_analysis.columns[1])

    # ===== FILTROS =====
    with col2:
        st.markdown("**Filtrar por Status:**")
        if 'Status Warning' in df_analysis.columns:
            status_options = df_analysis['Status Warning'].unique().tolist()
            selected_status = st.multiselect(
                "Status",
                status_options,
                default=status_options,
                key="warning_status_filter"
            )
            df_filtered = df_analysis[df_analysis['Status Warning'].isin(selected_status)]
        else:
            df_filtered = df_analysis.copy()
            
    with col3:
        st.markdown("**Pesquisar Produto:**")
        search = st.text_input(f"Buscar por {id_col} ou {title_col}", placeholder=f"Ex: {id_col}...")
        if search:
            df_filtered = df_filtered[
                df_filtered[id_col].astype(str).str.contains(search, case=False, na=False) | 
                df_filtered[title_col].astype(str).str.contains(search, case=False, na=False)
            ]

    # ===== CONTEÚDO PRINCIPAL =====
    if df_filtered.empty:
        st.info("Nenhum produto encontrado com os filtros selecionados.")
        return

    # Identificar colunas de volume (Qntd SemX) e ordenar de Sem1 a Sem5
    volume_cols = [c for c in df_filtered.columns if c.startswith('Qntd Sem')]
    volume_cols.sort() # Sem1, Sem2, Sem3, Sem4, Sem5
    
    # Identificar colunas de faturamento (Fat. SemX) e ordenar de Sem1 a Sem5
    fat_cols = [c for c in df_filtered.columns if c.startswith('Fat. Sem')]
    fat_cols.sort() # Fat. Sem1, Fat. Sem2...

    # Garantir que colunas de totais existem
    if 'Qtd Total' not in df_filtered.columns:
        df_filtered['Qtd Total'] = df_filtered[volume_cols].sum(axis=1) if volume_cols else 0
    if 'Fat Total' not in df_filtered.columns:
        df_filtered['Fat Total'] = df_filtered[fat_cols].sum(axis=1) if fat_cols else 0

    if view_mode == "📊 Volume":
        col_v1, col_v2 = st.columns([1, 1])
        
        with col_v1:
            # Top 10 Quedas
            if 'Delta %' in df_filtered.columns:
                st.markdown("📉 **Maiores Quedas de Volume (Sem1 vs Sem2):**")
                # Filtrar produtos que tinham pelo menos 1 venda na Sem2 para evitar -100% irrelevantes
                # E ordenar pela queda absoluta (Delta Qtd) para mostrar o que mais impactou o volume
                drops_df = df_filtered[df_filtered['Qntd Sem2'] > 0].copy()
                if not drops_df.empty:
                    top_drops = drops_df.sort_values('Delta %').head(10)
                    for _, row in top_drops.iterrows():
                        st.caption(f"{row[id_col]} - {str(row[title_col])[:40]}... ({row['Delta %']:.1f}%)")
                else:
                    st.caption("Nenhuma queda significativa detectada com vendas na semana anterior.")
        
        with col_v2:
            # Gráfico de evolução do Top 5
            top_5 = df_filtered.sort_values('Qtd Total', ascending=False).head(5)
            if not top_5.empty and volume_cols:
                plot_data = []
                for _, row in top_5.iterrows():
                    # Invertendo para que a Semana 1 apareça primeiro (à esquerda)
                    for sem in volume_cols:
                        plot_data.append({
                            'Produto': row[id_col],
                            'Semana': sem.replace('Qntd ', ''),
                            'Quantidade': row[sem]
                        })
                
                df_plot = pd.DataFrame(plot_data)
                fig = px.line(
                    df_plot, 
                    x='Semana', 
                    y='Quantidade',
                    color='Produto',
                    markers=True,
                    title='Evolução de Vendas (Top 5 Produtos)',
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
        # Na tabela, mostramos de Sem1 (mais recente) para Sem5 (mais antiga)
        cols_to_show = [id_col, title_col] + volume_cols + ['Qtd Total']
        volume_display = df_filtered[cols_to_show].copy()
        volume_display = volume_display.sort_values('Qtd Total', ascending=False)
        
        # Formatar números
        for col in volume_cols + ['Qtd Total']:
            if col in volume_display.columns:
                volume_display[col] = volume_display[col].apply(br_int)
        
        st.dataframe(volume_display, use_container_width=True, hide_index=True, height=400)
        
        # Download
        st.download_button(
            "📥 Baixar Volume (Excel)",
            data=to_xlsx_bytes(df_filtered[cols_to_show]),
            file_name="warning_volume.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_volume",
            use_container_width=True
        )

    elif view_mode == "💰 Faturamento":
        # Similar ao volume, mas para faturamento
        st.markdown("**Detalhamento de Faturamento por Semana:**")
        cols_to_show = [id_col, title_col] + fat_cols + ['Fat Total']
        fat_display = df_filtered[cols_to_show].copy()
        fat_display = fat_display.sort_values('Fat Total', ascending=False)
        
        for col in fat_cols + ['Fat Total']:
            if col in fat_display.columns:
                fat_display[col] = fat_display[col].apply(br_money)
        
        st.dataframe(fat_display, use_container_width=True, hide_index=True, height=400)
        
        st.download_button(
            "📥 Baixar Faturamento (Excel)",
            data=to_xlsx_bytes(df_filtered[cols_to_show]),
            file_name="warning_faturamento.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_fat",
            use_container_width=True
        )

    elif view_mode == "📈 Curva ABC":
        # Mostrar mudança de curva
        st.markdown("**Mudança de Curva ABC (Semana Atual vs Anterior):**")
        
        abc_display = df_filtered[[id_col, title_col, 'Curva Anterior', 'Curva Atual', 'Status Warning']].copy()
        st.dataframe(abc_display, use_container_width=True, hide_index=True, height=500)
        
        st.download_button(
            "📥 Baixar Análise ABC (Excel)",
            data=to_xlsx_bytes(df_filtered[[id_col, title_col, 'Curva Anterior', 'Curva Atual', 'Status Warning']]),
            file_name="warning_abc.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_abc",
            use_container_width=True
        )
