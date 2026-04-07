import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from ui.components.helpers import to_xlsx_bytes, br_money, br_int, safe_div, pct, ensure_cols
from ui.tabs.guide_tab import render_guide_tab
from ui.tabs.warning_semanal_tab import render_warning_semanal_tab
from ui.components.amazon_components import render_amazon_buybox_metrics, get_amazon_buybox_alerts
from ui.components.shared_ui import render_metric_grid, get_svg_icon, render_metric_card, render_report_section, get_icon_name

st.set_page_config(page_title="Curva ABC, Diagnóstico e Ações", layout="wide")

# Forçar fundo preto absoluto via injeção direta
st.markdown(
    """
    <script>
        // Forçar fundo preto no carregamento e em mudanças
        const forceBlack = () => {
            const main = window.parent.document.querySelector(".main");
            if (main) main.style.backgroundColor = "#000000";
            const sidebar = window.parent.document.querySelector("[data-testid='stSidebar']");
            if (sidebar) sidebar.style.backgroundColor = "#000000";
        };
        forceBlack();
        setInterval(forceBlack, 1000);
    </script>
    <style>
        /* Forçar fundo preto absoluto */
        .stApp, .main, [data-testid="stSidebar"], [data-testid="stHeader"] {
            background-color: #000000 !important;
        }
        
        /* Remover gradientes padrão do Streamlit */
        [data-testid="stAppViewContainer"] {
            background: #000000 !important;
        }

        /* ===== ESTILOS GERAIS ===== */
        body { color: #ffffff; }
        h1, h2, h3, p, span, div { color: #ffffff !important; }
        
        /* Esconder elementos desnecessários */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* ===== HERO SECTION ===== */
        .hero-container {
            background: linear-gradient(135deg, rgba(82, 121, 111, 0.1) 0%, rgba(0, 0, 0, 0) 100%);
            padding: 40px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 30px;
            text-align: center;
        }
        .hero-title {
            font-size: 2.8rem;
            font-weight: 900;
            letter-spacing: -1px;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #ffffff, #a0a0a0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .hero-subtitle {
            font-size: 1.1rem;
            opacity: 0.7;
            font-weight: 400;
        }

        /* ===== CARDS DE MÉTRICAS ===== */
        .metric-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 16px;
          margin-bottom: 1.5rem;
        }
        @media (max-width: 1200px) {
          .metric-grid { grid-template-columns: repeat(2, 1fr); }
        }
        .metric-card {
          background: rgba(255, 255, 255, 0.02);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-radius: 16px;
          padding: 20px;
          position: relative;
          overflow: hidden;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .metric-card:hover {
          background: rgba(82, 121, 111, 0.15);
          border-color: rgba(82, 121, 111, 0.6);
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(82, 121, 111, 0.2);
        }

        .metric-icon {
          width: 44px;
          height: 44px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.4rem;
          margin-bottom: 12px;
          background: transparent;
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: #ffffff !important;
        }
        .metric-icon svg {
          color: #ffffff !important;
          stroke: #ffffff !important;
          width: 24px;
          height: 24px;
          stroke-width: 2px;
        }

        .metric-label {
          font-size: 0.85rem;
          font-weight: 700;
          opacity: 1;
          margin: 0 0 4px 0;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: #ffffff;
        }
        .metric-value {
          font-size: 1.75rem;
          font-weight: 900;
          margin: 0;
          letter-spacing: -0.5px;
          color: #ffffff !important;
        }

        /* ===== LOGISTICA CARD ===== */
        .logistics-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 16px;
          margin: 1rem 0;
        }
        @media (max-width: 900px) {
          .logistics-grid { grid-template-columns: 1fr; }
        }
        .logistics-card {
          background: rgba(255, 255, 255, 0.02);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-radius: 16px;
          padding: 20px;
          text-align: center;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .logistics-card:hover {
          background: rgba(82, 121, 111, 0.15);
          border-color: rgba(82, 121, 111, 0.6);
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(82, 121, 111, 0.2);
        }

        .logistics-icon {
          width: 36px;
          height: 36px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.1rem;
          background: transparent;
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: #ffffff;
          margin: 0 auto 8px auto;
        }
        .logistics-icon svg {
          width: 20px;
          height: 20px;
          stroke: #ffffff;
          stroke-width: 2px;
        }
        .logistics-title {
          font-size: 0.85rem;
          font-weight: 700;
          opacity: 1;
          margin-bottom: 4px;
          text-transform: uppercase;
          color: #ffffff;
        }
        .logistics-value {
          font-size: 1.5rem;
          font-weight: 800;
        }
        .logistics-value.full { color: #4ade80; }
        .logistics-value.correios { color: #60a5fa; }
        .logistics-value.flex { color: #fbbf24; }
        .logistics-value.outros { color: #9ca3af; }

        /* ===== ADS CARD ===== */
        .ads-container {
          background: rgba(255, 255, 255, 0.02);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-radius: 16px;
          padding: 20px;
          margin: 1rem 0;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .ads-container:hover {
          border-color: rgba(82, 121, 111, 0.6);
          box-shadow: 0 4px 16px rgba(82, 121, 111, 0.15);
        }
        .ads-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 16px;
        }
        .ads-icon {
          width: 40px;
          height: 40px;
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.2rem;
          background: transparent;
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: #ffffff;
        }
        .ads-icon svg {
          width: 22px;
          height: 22px;
          stroke: #ffffff;
          stroke-width: 2px;
        }
        .ads-title {
          font-size: 1.1rem;
          font-weight: 800;
          color: #ffffff;
        }

        /* ===== EXPORT CARDS ===== */
        .export-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 20px;
          margin: 1rem 0;
        }
        .export-card {
          background: rgba(255, 255, 255, 0.02);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-radius: 16px;
          padding: 20px;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .export-card:hover {
          background: rgba(82, 121, 111, 0.15);
          border-color: rgba(82, 121, 111, 0.6);
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(82, 121, 111, 0.2);
        }
        .export-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 16px;
        }
        .export-icon {
          width: 48px;
          height: 48px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.2rem;
          background: transparent;
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: #ffffff;
        }
        .export-icon svg {
          width: 24px;
          height: 24px;
          stroke: #ffffff;
          stroke-width: 2px;
        }
        .export-icon.defense, .export-icon.correction, .export-icon.attack, .export-icon.cleanup, .export-icon.opportunity, .export-icon.combo { 
          background: transparent; 
          color: #ffffff; 
        }

        /* ===== TACTICAL CARD ===== */
        .tactical-card {
          background: rgba(255, 255, 255, 0.02);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-radius: 16px;
          padding: 20px;
          margin-bottom: 16px;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .tactical-card:hover {
          background: rgba(82, 121, 111, 0.15);
          border-color: rgba(82, 121, 111, 0.6);
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(82, 121, 111, 0.2);
        }
        .tactical-action svg {
          width: 18px;
          height: 18px;
          color: #ffffff !important;
          stroke: #ffffff !important;
        }

        /* ===== FRONT CARDS ===== */
        .front-card {
          background: rgba(255, 255, 255, 0.02);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-radius: 16px;
          padding: 20px;
          margin-bottom: 16px;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .front-card:hover {
          background: rgba(82, 121, 111, 0.15);
          border-color: rgba(82, 121, 111, 0.6);
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(82, 121, 111, 0.2);
        }
        .front-icon {
          width: 48px;
          height: 48px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.4rem;
          background: transparent;
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: #ffffff;
          margin-bottom: 12px;
        }
        .front-icon svg {
          width: 26px;
          height: 26px;
          stroke: #ffffff;
          stroke-width: 2px;
        }

        /* ===== REPORT SECTIONS ===== */
        .report-section {
          background: linear-gradient(145deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
          border: 1px solid rgba(255,255,255,0.08);
          border-radius: 20px;
          padding: 24px;
          margin-bottom: 24px;
        }
        .report-icon {
          width: 48px;
          height: 48px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.2rem;
          background: transparent;
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: #ffffff;
        }
        .report-icon svg {
          width: 24px;
          height: 24px;
          stroke: #ffffff;
          stroke-width: 2px;
        }
        .report-icon.purple, .report-icon.blue, .report-icon.green, .report-icon.amber, .report-icon.rose, .report-icon.cyan { 
          background: transparent; 
          color: #ffffff; 
        }

        /* ===== SECTION HEADER ===== */
        .section-icon {
          width: 40px;
          height: 40px;
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.2rem;
          background: transparent;
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: #ffffff;
        }
        .section-icon svg {
          width: 22px;
          height: 22px;
          stroke: #ffffff;
          stroke-width: 2px;
        }

        /* ===== SIDEBAR PREMIUM v2 ===== */
        .sidebar-section-icon {
          width: 32px;
          height: 32px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1rem;
          background: transparent;
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: #ffffff;
        }
        .sidebar-section-icon svg {
          width: 18px;
          height: 18px;
          stroke: #ffffff;
          stroke-width: 2px;
        }

        /* ===== INSIGHT CARD ===== */
        .insight-icon {
          width: 40px;
          height: 40px;
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.2rem;
          background: transparent;
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: #ffffff;
          flex-shrink: 0;
        }
        .insight-icon svg {
          width: 22px;
          height: 22px;
          stroke: #ffffff;
          stroke-width: 2px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Funções de UI movidas para ui/components/shared_ui.py

def render_logistics_section(df_logistics: pd.DataFrame, period: str):
    """Renderiza seção de logística com todas as formas de entrega"""
    truck_svg = get_svg_icon("truck")
    package_svg = get_svg_icon("package")
    
    st.markdown(f"""
    <div class="ads-container">
    <div class="ads-header">
    <div class="section-icon">{truck_svg}</div>
    <div>
      <div class="section-title">Logística - Período {period}</div>
      <div class="section-desc">Distribuição por forma de entrega</div>
    </div>
    </div>
    <div class="logistics-grid">
      <div class="logistics-card">
      <div class="logistics-icon">{package_svg}</div>
      <div class="logistics-title">FULL</div>
      <div class="logistics-value full">{pct(df_logistics.get('FULL', 0), 1)}</div>
      <div class="logistics-bar"><div class="logistics-bar-fill full" style="width: {df_logistics.get('FULL', 0)*100}%"></div></div>
      </div>
      <div class="logistics-card">
      <div class="logistics-icon">{package_svg}</div>
      <div class="logistics-title">FLEX</div>
      <div class="logistics-value flex">{pct(df_logistics.get('FLEX', 0), 1)}</div>
      <div class="logistics-bar"><div class="logistics-bar-fill flex" style="width: {df_logistics.get('FLEX', 0)*100}%"></div></div>
      </div>
      <div class="logistics-card">
      <div class="logistics-icon">{package_svg}</div>
      <div class="logistics-title">COLETA</div>
      <div class="logistics-value correios">{pct(df_logistics.get('COLETA', 0), 1)}</div>
      <div class="logistics-bar"><div class="logistics-bar-fill correios" style="width: {df_logistics.get('COLETA', 0)*100}%"></div></div>
      </div>
      <div class="logistics-card">
      <div class="logistics-icon">{package_svg}</div>
      <div class="logistics-title">CORREIOS</div>
      <div class="logistics-value outros">{pct(df_logistics.get('CORREIOS', 0), 1)}</div>
      <div class="logistics-bar"><div class="logistics-bar-fill outros" style="width: {df_logistics.get('CORREIOS', 0)*100}%"></div></div>
      </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

def render_ads_section(df_ads: pd.DataFrame, period: str):
    """Renderiza seção de vendas por publicidade"""
    megaphone_svg = get_svg_icon("megaphone")
    ads_qty = df_ads.get('ADS_QTY', 0)
    organic_qty = df_ads.get('ORGANIC_QTY', 0)
    total = ads_qty + organic_qty
    ads_pct = safe_div(ads_qty, total)
    organic_pct = safe_div(organic_qty, total)
    
    st.markdown(f"""
    <div class="ads-container">
    <div class="ads-header">
    <div class="ads-icon">{megaphone_svg}</div>
    <div class="ads-title">Vendas por Publicidade - Período {period}</div>
    </div>
    <div class="ads-grid">
      <div class="ads-metric ads">
      <div class="ads-metric-value ads">{pct(ads_pct, 1)}</div>
      <div class="ads-metric-label">Publicidade ({ads_qty:,} vendas)</div>
      </div>
      <div class="ads-metric organic">
      <div class="ads-metric-value organic">{pct(organic_pct, 1)}</div>
      <div class="ads-metric-label">Orgânicas ({organic_qty:,} vendas)</div>
      </div>
    </div>
    <div class="ads-bar-container">
      <div class="ads-bar-labels">
      <span>Publicidade</span>
      <span>Orgânico</span>
      </div>
      <div class="ads-bar">
      <div class="ads-bar-ads" style="width: {ads_pct*100}%"></div>
      <div class="ads-bar-organic" style="width: {organic_pct*100}%"></div>
      </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

def render_abc_quadrant(df_abc_summary: pd.DataFrame, df_abc_details: pd.DataFrame, period: str):
    """Renderiza o quadrante com 3 cards (Curva A, B, C) e botão de exportação com lista detalhada."""
    section_header(f"Resumo Curva ABC - Período {period}", "Total de anúncios e faturamento por classificação", "📊", "green")
    
    cols = st.columns(3)
    colors = {"Curva A": "#22c55e", "Curva B": "#3b82f6", "Curva C": "#f59e0b"}
    icons = {"Curva A": "⭐", "Curva B": "📈", "Curva C": "📦"}
    
    for i, (_, row) in enumerate(df_abc_summary.iterrows()):
        curva = row['Curva']
        color = colors.get(curva, "#ffffff")
        icon_emoji = icons.get(curva, "📦")
        icon_name = get_icon_name(icon_emoji)
        svg = get_svg_icon(icon_name)
        
        with cols[i]:
            st.markdown(f"""
            <div class="logistics-card" style="border-top: 4px solid {color}; padding: 20px; text-align: center; background: rgba(255,255,255,0.02); border-radius: 16px;">
                <div class="metric-icon" style="margin: 0 auto 12px auto;">{svg}</div>
                <div class="logistics-title" style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; color: #ffffff;">{curva}</div>
                <div class="logistics-value" style="font-size: 1.5rem; font-weight: 800; color: {color};">{br_money(row['Faturamento'])}</div>
                <div style="font-size: 0.85rem; opacity: 0.7; margin-top: 4px; color: #ffffff;">{br_int(row['Anúncios'])} Anúncios</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
    
    # Botão de exportação logo abaixo dos cards
    st.download_button(
        label=f"📥 Gerar Relatório Excel Curva ABC ({period})",
        data=to_xlsx_bytes(df_abc_details),
        file_name=f"curva_abc_{period}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

def render_export_card(icon: str, title: str, desc: str, itens: int, fat: float, card_type: str):
    """Renderiza card de exportação com estatísticas"""
    icon_name = get_icon_name(icon)
    svg = get_svg_icon(icon_name)
    
    return f"""
<div class='export-card'>
  <div class='export-header'>
    <div class='export-icon'>{svg}</div>
    <div>
      <div class='export-title'>{title}</div>
      <div class='export-desc'>{desc}</div>
    </div>
  </div>
  <div class='export-stats'>
    <div class='export-stat'>
      <div class='export-stat-value'>{itens}</div>
      <div class='export-stat-label'>Itens</div>
    </div>
    <div class='export-stat'>
      <div class='export-stat-value'>{br_money(fat)}</div>
      <div class='export-stat-label'>Faturamento</div>
    </div>
  </div>
</div>
    """

def render_tactical_card(row: dict, card_type: str):
    """Renderiza card tático para um produto"""
    badge_class = {
        "DEFESA": "defense",
        "CORREÇÃO": "correction",
        "ATAQUE": "attack",
        "LIMPEZA": "cleanup",
        "OTIMIZAÇÃO": "optimization"
    }.get(card_type, "optimization")
    
    return f"""
<div class='tactical-card'>
  <div class='tactical-header'>
    <div>
      <p class='tactical-title'>{row.get('Título', '-')[:60]}...</p>
      <span class='tactical-mlb'>{row.get('MLB', '-')}</span>
    </div>
    <span class='tactical-badge {badge_class}'>{card_type}</span>
  </div>
  <div class='tactical-metrics'>
    <div class='tactical-metric'>
      <div class='tactical-metric-value'>{br_money(row.get('Faturamento', 0))}</div>
      <div class='tactical-metric-label'>Faturamento</div>
    </div>
    <div class='tactical-metric'>
      <div class='tactical-metric-value'>{br_int(row.get('Qtd Vendida', 0))}</div>
      <div class='tactical-metric-label'>Vendas</div>
    </div>
    <div class='tactical-metric'>
      <div class='tactical-metric-value'>{row.get('Curva', '-')}</div>
      <div class='tactical-metric-label'>Curva</div>
    </div>
  </div>
  <div class='tactical-action'>{get_svg_icon("lightbulb")} {row.get('Ação sugerida', 'Sem ação definida')}</div>
</div>
    """

def render_front_summary(fronts: list):
    """Renderiza resumo das frentes. fronts = [(icon, count, label), ...]"""
    html = "<div class='front-summary'>"
    for icon, count, label in fronts:
        icon_name = get_icon_name(icon)
        svg = get_svg_icon(icon_name)
        html += f"""
  <div class='front-pill'>
  <span class='front-pill-icon'>{svg}</span>
  <span class='front-pill-count'>{count}</span>
  <span class='front-pill-label'>{label}</span>
  </div>
        """
    html += "</div>"
    return html

def render_insight_card(icon: str, title: str, text: str):
    icon_name = get_icon_name(icon)
    svg = get_svg_icon(icon_name)
    return f"""
<div class='insight-card'>
  <div class='insight-icon'>{svg}</div>
  <div>
    <div class='insight-title'>{title}</div>
    <div class='insight-text'>{text}</div>
  </div>
</div>
    """

def section_header(title: str, desc: str, icon: str = "📊", color: str = "purple"):
    """Renderiza header de seção"""
    icon_name = get_icon_name(icon)
    svg = get_svg_icon(icon_name)
    st.markdown(f"""
    <div class='section-header'>
    <div class='section-icon'>{svg}</div>
    <div>
      <div class='section-title'>{title}</div>
      <div class='section-desc'>{desc}</div>
    </div>
    </div>
    """, unsafe_allow_html=True)

def render_front_card(icon: str, title: str, desc: str, itens: int, fat: float, card_type: str, filename: str, df_seg: pd.DataFrame):
    icon_name = get_icon_name(icon)
    svg = get_svg_icon(icon_name)
    st.markdown(f"""
<div class='front-card'>
  <div class='front-header'>
    <div class='front-icon'>{svg}</div>
    <div>
      <div class='front-title'>{title}</div>
      <div class='front-desc'>{desc}</div>
    </div>
  </div>
  <div class='front-stats'>
    <div class='front-stat'>
      <div class='front-stat-value'>{itens}</div>
      <div class='front-stat-label'>Itens</div>
    </div>
    <div class='front-stat'>
      <div class='front-stat-value'>{br_money(fat)}</div>
      <div class='front-stat-label'>Faturamento</div>
    </div>
  </div>
</div>
    """, unsafe_allow_html=True)
    st.download_button(
        f"📥 Baixar {title}",
        data=to_xlsx_bytes(df_seg),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        key=f"btn_{filename}"
    )

# Helpers de formatação
def br_int(val):
    try: return f"{int(val):,}".replace(",", ".")
    except: return "0"

def br_money(val):
    try: return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "R$ 0,00"

def pct(val, digits=0):
    try: return f"{val*100:.{digits}f}%"
    except: return "0%"

def safe_div(a, b):
    return a / b if b and b != 0 else 0

# Lógica de processamento de dados (Mover para data_processing se crescer mais)
def process_ml_data(df):
    # Períodos em ordem decrescente (mais antigo primeiro)
    periods = ['91-120', '61-90', '31-60', '0-30']
    
    def _pick_col(cols, target):
        for c in cols:
            if target.lower() in c.lower(): return c
        raise KeyError(f"Coluna '{target}' não encontrada")

    # Localizar cabeçalho real
    header_idx = 0
    for i, row in df.iterrows():
        row = row.astype(str)
        if row.str.contains('data da venda', na=False).any() or row.str.contains('# de anúncio', na=False).any() or row.str.contains('de anúncio', na=False).any():
            header_idx = i
            break
    
    df.columns = df.iloc[header_idx]
    df = df.iloc[header_idx+1:].reset_index(drop=True)
    
    # Limpar nomes de colunas
    df.columns = [str(c).strip() for c in df.columns]
    
    col_mlb = _pick_col(df.columns, '# de anúncio')
    col_data = _pick_col(df.columns, 'Data da venda')
    col_tit = _pick_col(df.columns, 'Título do anúncio')
    col_fat = _pick_col(df.columns, 'Vendas líquidas')
    col_qtd = _pick_col(df.columns, 'Unidades vendidas')
    
    # Logística e Ads
    col_log = None
    try: col_log = _pick_col(df.columns, 'Forma de entrega')
    except: pass
    
    col_ads = None
    try: col_ads = _pick_col(df.columns, 'Venda por publicidade')
    except: 
        # Se ainda não encontrou, busca parcial por "publicidade"
        for c in df.columns:
            if "publicidade" in c.lower():
                col_ads = c
                break

    def parse_date(val):
        if pd.isna(val): return None
        val = str(val).lower().strip()
        try:
            # Tratar meses em português
            months = {
                'janeiro': '01', 'fevereiro': '02', 'março': '03', 'marco': '03',
                'abril': '04', 'maio': '05', 'junho': '06', 'julho': '07',
                'agosto': '08', 'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
            }
            for pt, en in months.items():
                if pt in val: val = val.replace(pt, en)
            return pd.to_datetime(val, dayfirst=True)
        except: return None

    def parse_num(val):
        if pd.isna(val): return 0.0
        val = str(val).replace('R$', '').strip()
        # Se contiver apenas ',', assume que é o separador decimal (1234,56)
        # Se contiver '.' e ',', assume que '.' é milhar e ',' é decimal (1.234,56)
        if ',' in val:
            val = val.replace('.', '').replace(',', '.')
        # Remove símbolos de moeda se existirem
        try: return float(val)
        except: return 0.0

    df['dt'] = df[col_data].apply(parse_date)
    df['fat'] = df[col_fat].apply(parse_num)
    df['qtd'] = df[col_qtd].apply(parse_num)
    df['mlb'] = df[col_mlb].astype(str)
    df['titulo'] = df[col_tit].astype(str)
    
    # Filtrar datas válidas
    df = df[df['dt'].notna()].copy()
    ref_date = df['dt'].max()
    
    def get_period(dt):
        days = (ref_date - dt).days
        if days <= 30: return '0-30'
        if days <= 60: return '31-60'
        if days <= 90: return '61-90'
        if days <= 120: return '91-120'
        return 'antigo'

    df['period'] = df['dt'].apply(get_period)
    df = df[df['period'] != 'antigo']
    
    # Agregação base
    cols = ['MLB','Título'] + [f'Qntd {p}' for p in ['0-30','31-60','61-90','91-120']] + [f'Fat. {p}' for p in ['0-30','31-60','61-90','91-120']] + [f'Curva {p}' for p in ['0-30','31-60','61-90','91-120']]
    
    # Pivot para períodos
    out_q = df.pivot_table(index=['mlb','titulo'], columns='period', values='qtd', aggfunc='sum').fillna(0)
    out_f = df.pivot_table(index=['mlb','titulo'], columns='period', values='fat', aggfunc='sum').fillna(0)
    
    # Garantir todas as colunas de período
    for p in periods:
        if p not in out_q.columns: out_q[p] = 0
        if p not in out_f.columns: out_f[p] = 0
    
    # Calcular Curva ABC para cada período
    def calc_abc(series):
        if series.sum() == 0: return pd.Series(['-'] * len(series), index=series.index)
        s = series.sort_values(ascending=False)
        cum_pct = s.cumsum() / s.sum()
        res = pd.Series(index=s.index)
        res[cum_pct <= 0.8] = 'A'
        res[(cum_pct > 0.8) & (cum_pct <= 0.95)] = 'B'
        res[cum_pct > 0.95] = 'C'
        return res.reindex(series.index)

    out_abc = pd.DataFrame(index=out_f.index)
    for p in periods:
        out_abc[p] = calc_abc(out_f[p])
    
    # Classificar logística
    df_logistics = None
    if col_log:
        df['log_cat'] = 'OUTROS'
        df.loc[df[col_log].str.contains('Full', na=False, case=False), 'log_cat'] = 'FULL'
        df.loc[df[col_log].str.contains('Flex', na=False, case=False), 'log_cat'] = 'FLEX'
        df.loc[df[col_log].str.contains('Coleta', na=False, case=False), 'log_cat'] = 'COLETA'
        df.loc[df[col_log].str.contains('Correios', na=False, case=False), 'log_cat'] = 'CORREIOS'
        
        df_logistics = df.pivot_table(index='period', columns='log_cat', values='qtd', aggfunc='sum').fillna(0)
        for cat in ['FULL', 'FLEX', 'COLETA', 'CORREIOS', 'OUTROS']:
            if cat not in df_logistics.columns: df_logistics[cat] = 0
        df_logistics = df_logistics.div(df_logistics.sum(axis=1), axis=0).fillna(0)

    # Classificar vendas por publicidade: "Sim" = venda via Ads, Vazio/outros = Orgânica
    # Normaliza valores e verifica se é "sim" ou variações
    df_ads = None
    if col_ads:
        df['is_ads'] = df[col_ads].astype(str).str.lower().str.strip().isin(['sim', 'yes', 'true', '1', 's'])
        df_ads_summary = df.groupby('period').agg(
            ADS_QTY=('qtd', lambda x: x[df.loc[x.index, 'is_ads']].sum()),
            ORGANIC_QTY=('qtd', lambda x: x[~df.loc[x.index, 'is_ads']].sum())
        ).fillna(0)
        df_ads = df_ads_summary

    # Agregar por período para logística
    # Para o export final, precisamos de uma linha por MLB
    out = out_q.reset_index().rename(columns={'mlb':'MLB','titulo':'Título'})
    for p in periods:
        out[f'Qntd {p}'] = out_q[p].values
        out[f'Fat. {p}'] = out_f[p].values
        out[f'Curva {p}'] = out_abc[p].values
    
    # Adicionar Logística Dominante (Simplificado para o export)
    if col_log:
        log_pivot = df.pivot_table(index='mlb', columns='log_cat', values='qtd', aggfunc='sum').fillna(0)
        for p in periods:
            # Share de Full por período e MLB
            temp_log = df[df['period'] == p].pivot_table(index='mlb', columns='log_cat', values='qtd', aggfunc='sum').fillna(0)
            if 'FULL' not in temp_log.columns: temp_log['FULL'] = 0
            share_full = temp_log['FULL'] / temp_log.sum(axis=1)
            out[f'Share Full Qtd {p}'] = out['MLB'].map(share_full).fillna(0)
            out[f'Logística dom {p}'] = np.where(out[f'Share Full Qtd {p}'] >= 0.5, 'FULL', 'NÃO FULL')

    return out, df_logistics, df_ads, df

# Interface Principal
def main():
    # Injetar CSS e JS
    # (Já feito no topo)

    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div class="hero-container" style="padding: 20px 0; margin-bottom: 20px;">
          <div class="metric-icon" style="margin: 0 auto 10px auto;">{get_svg_icon("bar-chart-3")}</div>
          <div style="font-size: 1.2rem; font-weight: 900; color: #ffffff;">CURVA ABC</div>
          <div style="font-size: 0.75rem; opacity: 0.5;">Diagnóstico & Ações</div>
        </div>
        """, unsafe_allow_html=True)

        # Seção de Upload
        package_svg = get_svg_icon("package")
        st.markdown(f"""
        <div class='sidebar-section'>
          <div class='sidebar-section-header'>
            <div class='sidebar-section-icon'>{package_svg}</div>
            <div>
              <div class='sidebar-section-title'>UPLOAD</div>
              <div class='sidebar-section-desc'>Relatórios do Mercado Livre</div>
            </div>
          </div>
        """, unsafe_allow_html=True)
        
        main_file = st.file_uploader(
            "📂 Carregar relatório(s) de vendas", 
            type=["xlsx", "xls"], 
            key="main_file",
            help="Suporta Mercado Livre, Shopee e Amazon. Para Shopee, você pode enviar múltiplos arquivos."
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Seção de Filtros
        # ... (filtros simplificados para o exemplo)
        
        # Identificação do Cliente
        st.markdown(f"""
        <div class='sidebar-section'>
          <div class='sidebar-section-header'>
            <div class='sidebar-section-icon'>{get_svg_icon("users")}</div>
            <div>
              <div class='sidebar-section-title'>CONTA</div>
            </div>
          </div>
        """, unsafe_allow_html=True)
        cliente_nome = st.text_input("Nome do Cliente / Conta", value="", placeholder="Ex: Cliente X")
        st.markdown("</div>", unsafe_allow_html=True)

        # Versão
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; opacity: 0.4; font-size: 0.7rem;'>
          <div class="sidebar-section-icon" style="margin: 0 auto 8px auto;">{get_svg_icon("layout")}</div>
          Dashboard v4.3 • Manus AI
        </div>
        """, unsafe_allow_html=True)

    if not main_file:
        st.info("Faça upload do relatório de vendas do Mercado Livre (120 dias) para começar.")
        return

    # Processar dados
    try:
        df_raw_file = pd.read_excel(main_file)
        out, df_logistics, df_ads, df_raw = process_ml_data(df_raw_file)
    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")
        return

    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["DASHBOARD", "LISTAS E EXPORTAÇÃO", "PLANO TÁTICO", "RELATÓRIO ESTRATÉGICO", "WARNING SEMANAL", "GUIA DE USO"])

    with tab1:
        # Seletor de período
        selected_period = st.selectbox("Selecione o Período para Análise", ["0-30", "31-60", "61-90", "91-120"])
        
        # Métricas principais
        total_fat = out[f'Fat. {selected_period}'].sum()
        total_qty = out[f'Qntd {selected_period}'].sum()
        total_ads = len(out[out[f'Qntd {selected_period}'] > 0])
        tm = safe_div(total_fat, total_qty)
        
        render_metric_grid([
            (f"Faturamento {selected_period}", br_money(total_fat), "💰", "green"),
            (f"Quantidade {selected_period}", br_int(total_qty), "📦", "blue"),
            (f"Ticket Médio {selected_period}", br_money(tm), "🎯", "amber"),
            (f"Anúncios Ativos", br_int(total_ads), "📊", "purple")
        ])
        
        # Curva ABC
        dist_period = out[f'Curva {selected_period}'].value_counts()
        dist_period_df = pd.DataFrame({"Curva": dist_period.index, "Anúncios": dist_period.values, "Faturamento": [out[out[f'Curva {selected_period}'] == c][f'Fat. {selected_period}'].sum() for c in dist_period.index]})
        
        render_abc_quadrant(dist_period_df, out, selected_period)
        
        # Logística e Ads
        if df_logistics is not None:
            render_logistics_section(df_logistics.loc[selected_period], selected_period)
        
        if df_ads is not None:
            render_ads_section(df_ads.loc[selected_period], selected_period)

    with tab2:
        st.markdown(render_report_section("package", "Central de Exportação", f"Baixe listas segmentadas para ação imediata - Período: {selected_period} dias", "blue"), unsafe_allow_html=True)
        
        # Grid de cards de exportação
        cols = st.columns(3)
        with cols[0]:
            anchors = out[out[f'Curva {selected_period}'] == 'A']
            st.markdown(render_export_card("🛡️", "Âncoras", "Produtos estáveis em curva A", len(anchors), anchors[f'Fat. {selected_period}'].sum(), "defense"), unsafe_allow_html=True)
        with cols[1]:
            drops = out[(out[f'Curva {selected_period}'] != 'A') & (out['Curva 31-60'] == 'A')]
            st.markdown(render_export_card("⚠️", "Fuga de Receita", "Produtos que caíram de curva", len(drops), drops[f'Fat. {selected_period}'].sum(), "correction"), unsafe_allow_html=True)
        with cols[2]:
            growth = out[(out[f'Curva {selected_period}'] == 'A') & (out['Curva 31-60'] != 'A')]
            st.markdown(render_export_card("🚀", "Crescimento", "Produtos em ascensão", len(growth), growth[f'Fat. {selected_period}'].sum(), "attack"), unsafe_allow_html=True)

    with tab3:
        st.markdown(render_report_section("layout", "Plano Tático por Produto", "Ações detalhadas para 15 e 30 dias", "purple"), unsafe_allow_html=True)
        
        # Filtros de frente
        front_icons = {"DEFESA": "🛡️", "CORREÇÃO": "⚠️", "ATAQUE": "🚀", "LIMPEZA": "🧹", "OTIMIZAÇÃO": "⚙️"}
        cols = st.columns(5)
        for i, frente in enumerate(["DEFESA", "CORREÇÃO", "ATAQUE", "LIMPEZA", "OTIMIZAÇÃO"]):
            with cols[i]:
                icon_emoji = front_icons.get(frente, "")
                icon_name = get_icon_name(icon_emoji)
                svg = get_svg_icon(icon_name)
                st.markdown(f'<div class="metric-icon" style="width:32px; height:32px; margin: 0 auto 4px auto;">{svg}</div>', unsafe_allow_html=True)
                st.checkbox(f"{frente}", value=True, key=f"front_{frente}")

    with tab4:
        st.markdown(render_report_section("search", "Diagnóstico Macro", "Visão geral da saúde do catálogo", "purple"), unsafe_allow_html=True)
        st.info("Relatório estratégico em desenvolvimento.")

    with tab5:
        render_warning_semanal_tab(out, df_raw)

    with tab6:
        render_guide_tab()

if __name__ == "__main__":
    main()
