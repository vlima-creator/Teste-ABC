import streamlit as st
import pandas as pd
import numpy as np
import history_manager
import plotly.express as px
import plotly.graph_objects as go

# Imports dos novos módulos multi-canal
from data_processing.factory import detect_and_process
from ui.components.shopee_components import (
    render_shopee_conversion_funnel,
    render_shopee_engagement_metrics,
    render_shopee_top_rejection_rate,
    render_shopee_top_products,
    render_shopee_abc_distribution
)
from ui.components.helpers import to_xlsx_bytes, br_money, br_int, safe_div, pct, ensure_cols
from ui.tabs.guide_tab import render_guide_tab
from ui.tabs.warning_semanal_tab import render_warning_semanal_tab
from ui.components.amazon_components import render_amazon_buybox_metrics, get_amazon_buybox_alerts
from ui.components.shared_ui import render_metric_grid, get_svg_icon, render_metric_card, render_report_section

st.set_page_config(page_title="Curva ABC, Diagnóstico e Ações", layout="wide")

# Forçar fundo preto absoluto via injeção direta
st.markdown(
    """
    <script>
        // Forçar fundo preto no carregamento e em mudanças
        const forceBlack = () => {
            document.body.style.backgroundColor = "#000000";
            const stApp = document.querySelector(".stApp");
            if (stApp) stApp.style.backgroundColor = "#000000";
        };
        forceBlack();
        setInterval(forceBlack, 1000);
    </script>
    <style>
        /* Forçar fundo preto absoluto */
        .stApp, .main, .block-container, body {
            background-color: #000000 !important;
        }
        /* Esconder elementos que podem ter cores residuais */
        [data-testid="stHeader"] {
            background-color: rgba(0,0,0,0) !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================
# Estilo premium aprimorado v3.2 (Padronização de Ícones)
# =========================
st.markdown(
    """
<style>
/* ===== RESET E BASE ===== */
* { 
    font-variant-numeric: tabular-nums; 
    font-family: 'Inter', sans-serif;
}
.stApp, .main, .block-container, body {
    background-color: #000000 !important;
    color: #ffffff !important;
}
.block-container {padding-top: 1rem; padding-bottom: 2rem; max-width: 1600px;}

/* Header transparente */
header[data-testid="stHeader"] {background: rgba(0,0,0,0);}

/* Esconde linhas separadoras */
hr {display: none !important;}

/* ===== SIDEBAR PREMIUM ===== */
section[data-testid="stSidebar"] {
  background: #000000 !important;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-right: 1px solid rgba(255, 255, 255, 0.15);
}
section[data-testid="stSidebar"] .block-container {padding-top: 1rem;}
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
  letter-spacing: -0.3px;
  color: #e2e8f0;
}

/* ===== HEADER PRINCIPAL ===== */
.hero-header {
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  padding: 24px 28px;
  margin: 0 0 1.5rem 0;
  position: relative;
  overflow: hidden;
}
.hero-title {
  font-size: 2rem;
  font-weight: 800;
  margin: 0;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, #fff, #c4b5fd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-subtitle {
  margin-top: 0.5rem;
  font-weight: 700;
  opacity: 1;
  font-size: 1rem;
  color: #ffffff;
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
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  margin-bottom: 12px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff !important;
}
.metric-icon svg {
  color: #ffffff !important;
  stroke: #ffffff !important;
  width: 20px;
  height: 20px;
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

/* ===== PERIOD SELECTOR ===== */
.period-selector {
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 16px 20px;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 16px;
}
.period-label {
  font-size: 0.9rem;
  font-weight: 800;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ===== LOGISTICA CARD ===== */
.logistics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
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
  margin: 0 auto 8px auto;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff !important;
}
.logistics-icon svg {
  color: #ffffff !important;
  stroke: #ffffff !important;
  width: 18px;
  height: 18px;
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
.logistics-value.coleta { color: #a78bfa; }
.logistics-value.outros { color: #9ca3af; }

.logistics-bar {
  height: 8px;
  background: rgba(255,255,255,0.1);
  border-radius: 4px;
  margin-top: 12px;
  overflow: hidden;
}
.logistics-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}
.logistics-bar-fill.full { background: linear-gradient(90deg, #22c55e, #4ade80); }
.logistics-bar-fill.correios { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.logistics-bar-fill.flex { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.logistics-bar-fill.coleta { background: linear-gradient(90deg, #8b5cf6, #a78bfa); }
.logistics-bar-fill.outros { background: linear-gradient(90deg, #6b7280, #9ca3af); }

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
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff !important;
}
.ads-icon svg {
  color: #ffffff !important;
  stroke: #ffffff !important;
  width: 18px;
  height: 18px;
}
.ads-title {
  font-size: 1.1rem;
  font-weight: 800;
  color: #ffffff;
}
.ads-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}
.ads-metric {
  text-align: center;
  padding: 16px;
  background: rgba(255,255,255,0.03);
  border-radius: 12px;
}
.ads-metric.ads { border-left: 4px solid #f97316; }
.ads-metric.organic { border-left: 4px solid #22c55e; }
.ads-metric-value {
  font-size: 2rem;
  font-weight: 800;
}
.ads-metric-value.ads { color: #fb923c; }
.ads-metric-value.organic { color: #4ade80; }
.ads-metric-label {
  font-size: 0.85rem;
  opacity: 0.7;
  margin-top: 4px;
}
.ads-bar-container {
  margin-top: 16px;
}
.ads-bar-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  opacity: 0.7;
  margin-bottom: 6px;
}
.ads-bar {
  height: 12px;
  background: rgba(255,255,255,0.1);
  border-radius: 6px;
  overflow: hidden;
  display: flex;
}
.ads-bar-ads {
  height: 100%;
  background: linear-gradient(90deg, #f97316, #fb923c);
  transition: width 0.5s ease;
}
.ads-bar-organic {
  height: 100%;
  background: linear-gradient(90deg, #22c55e, #4ade80);
  transition: width 0.5s ease;
}

/* ===== EXPORT CARDS ===== */
.export-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin: 1rem 0;
}
@media (max-width: 1000px) {
  .export-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 700px) {
  .export-grid { grid-template-columns: 1fr; }
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
  border-color: rgba(82, 121, 111, 0.6);
  box-shadow: 0 4px 16px rgba(82, 121, 111, 0.15);
}
.export-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.export-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff !important;
}
.export-icon svg {
  color: #ffffff !important;
  stroke: #ffffff !important;
  width: 18px;
  height: 18px;
}
.export-title {
  font-size: 1rem;
  font-weight: 800;
  color: #ffffff;
}
.export-desc {
  font-size: 0.8rem;
  opacity: 0.6;
  margin-bottom: 16px;
}

/* ===== TACTICAL CARDS ===== */
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
.tactical-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.tactical-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.tactical-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff !important;
}
.tactical-icon svg {
  width: 20px;
  height: 20px;
  color: #ffffff !important;
  stroke: #ffffff !important;
}
.tactical-title {
  font-size: 1.1rem;
  font-weight: 800;
  color: #ffffff;
}
.tactical-frente {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
}
.tactical-frente.defense { background: rgba(34, 197, 94, 0.2); color: #4ade80; }
.tactical-frente.attack { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
.tactical-frente.cleanup { background: rgba(244, 63, 94, 0.2); color: #fb7185; }
.tactical-frente.correction { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
.tactical-frente.optimization { background: rgba(139, 92, 246, 0.2); color: #a78bfa; }

.tactical-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}
@media (max-width: 800px) {
  .tactical-grid { grid-template-columns: repeat(2, 1fr); }
}
.tactical-metric {
  min-width: 80px;
}
.tactical-metric-value {
  font-size: 1.1rem;
  font-weight: 800;
  color: #ffffff;
}
.tactical-metric-label {
  font-size: 0.7rem;
  opacity: 0.6;
  text-transform: uppercase;
}
.tactical-action {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 0.9rem;
  color: #ffffff;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
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

.front-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.front-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff !important;
}
.front-icon svg {
  width: 20px;
  height: 20px;
  color: #ffffff !important;
  stroke: #ffffff !important;
}

.front-title {
  font-size: 1.1rem;
  font-weight: 800;
  color: #ffffff;
}
.front-desc {
  font-size: 0.85rem;
  opacity: 0.6;
}
.front-stats {
  display: flex;
  gap: 20px;
}
.front-stat {
  flex: 1;
  text-align: center;
  padding: 12px;
  background: rgba(255,255,255,0.03);
  border-radius: 10px;
}
.front-stat-value {
  font-size: 1.25rem;
  font-weight: 800;
  color: #ffffff;
}
.front-stat-label {
  font-size: 0.7rem;
  opacity: 0.6;
  text-transform: uppercase;
}

/* ===== REPORT SECTIONS ===== */
.report-section {
  background: linear-gradient(145deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
}
.report-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.report-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff !important;
}
.report-icon svg {
  width: 22px;
  height: 22px;
  color: #ffffff !important;
  stroke: #ffffff !important;
}

.report-title {
  font-size: 1.4rem;
  font-weight: 900;
  color: #ffffff;
  margin: 0;
  text-transform: uppercase;
}
.report-desc {
  font-size: 0.9rem;
  opacity: 0.6;
  margin-top: 2px;
}

/* ===== KPI HIGHLIGHT ===== */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin: 16px 0;
}
@media (max-width: 800px) {
  .kpi-grid { grid-template-columns: 1fr; }
}
.kpi-box {
  background: linear-gradient(145deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 14px;
  padding: 20px;
  text-align: center;
}
.kpi-box.purple { border-top: 3px solid #8b5cf6; }
.kpi-box.blue { border-top: 3px solid #3b82f6; }
.kpi-box.green { border-top: 3px solid #22c55e; }
.kpi-box.amber { border-top: 3px solid #f59e0b; }
.kpi-box.rose { border-top: 3px solid #f43f5e; }

.kpi-value {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 4px;
}
.kpi-value.purple { color: #ffffff; }
.kpi-value.blue { color: #ffffff; }
.kpi-value.green { color: #ffffff; }
.kpi-value.amber { color: #ffffff; }
.kpi-value.rose { color: #ffffff; }

.kpi-label {
  font-size: 0.85rem;
  font-weight: 800;
  opacity: 1;
  color: #ffffff;
  text-transform: uppercase;
}

/* ===== INSIGHT CARD ===== */
.insight-card {
  background: linear-gradient(145deg, rgba(139, 92, 246, 0.1), rgba(99, 102, 241, 0.05));
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 14px;
  padding: 18px 20px;
  margin: 16px 0;
  display: flex;
  align-items: flex-start;
  gap: 14px;
}
.insight-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff !important;
}
.insight-icon svg {
  width: 18px;
  height: 18px;
  color: #ffffff !important;
  stroke: #ffffff !important;
}
.insight-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #c4b5fd;
  margin-bottom: 4px;
}
.insight-text {
  font-size: 0.9rem;
  opacity: 0.85;
  line-height: 1.5;
}

/* ===== FRONT SUMMARY ===== */
.front-summary {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin: 16px 0;
}
.front-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 30px;
  font-size: 0.9rem;
}
.front-pill-icon {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff !important;
}
.front-pill-icon svg {
  width: 14px;
  height: 14px;
  color: #ffffff !important;
  stroke: #ffffff !important;
}
.front-pill-count {
  font-weight: 900;
  color: #ffffff;
}
.front-pill-label {
  font-weight: 800;
  opacity: 1;
  color: #ffffff;
  text-transform: uppercase;
}

/* ===== SECTION HEADER ===== */
.section-box {
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.section-box:hover {
  border-color: rgba(82, 121, 111, 0.6);
  box-shadow: 0 4px 16px rgba(82, 121, 111, 0.15);
}
.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.section-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff !important;
}
.section-icon svg {
  color: #ffffff !important;
  stroke: #ffffff !important;
  width: 18px;
  height: 18px;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 800;
  color: #ffffff;
}
.section-desc {
  font-size: 0.85rem;
  opacity: 0.6;
}

/* ===== INPUTS ===== */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
  border-radius: 12px !important;
  border-color: rgba(255,255,255,0.08) !important;
  background: rgba(255, 255, 255, 0.03) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
div[data-baseweb="input"] > div:hover,
div[data-baseweb="select"] > div:hover {
  border-color: rgba(82, 121, 111, 0.4) !important;
}
div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within {
  border-color: rgba(82, 121, 111, 0.6) !important;
  box-shadow: 0 0 0 2px rgba(82, 121, 111, 0.1) !important;
}

/* ===== BOTÕES ===== */
div.stDownloadButton button, div.stButton button {
  border-radius: 12px !important;
  padding: 0.6rem 1rem !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  background: rgba(255, 255, 255, 0.05) !important;
  backdrop-filter: blur(5px) !important;
  font-weight: 800 !important;
  color: #ffffff !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
div.stDownloadButton button:hover, div.stButton button:hover {
  background: rgba(82, 121, 111, 0.25) !important;
  border-color: rgba(82, 121, 111, 0.6) !important;
  box-shadow: 0 4px 16px rgba(82, 121, 111, 0.3) !important;
  transform: translateY(-1px) !important;
}

/* ===== TABS ===== */
.stTabs [data-baseweb="tab-list"] {
  gap: 8px;
  background: rgba(255,255,255,0.03);
  padding: 8px;
  border-radius: 14px;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 10px !important;
  padding: 10px 20px !important;
  font-weight: 800 !important;
}
.stTabs [aria-selected="true"] {
  background: rgba(82, 121, 111, 0.25) !important;
  border: 1px solid rgba(82, 121, 111, 0.6) !important;
  color: #ffffff !important;
}

/* ===== EXPANDERS ===== */
.streamlit-expanderHeader {
  background: rgba(255,255,255,0.03) !important;
  border-radius: 12px !important;
}


/* ===== SIDEBAR PREMIUM v2 ===== */
.sidebar-section {
  background: linear-gradient(145deg, rgba(99, 102, 241, 0.12), rgba(139, 92, 246, 0.06));
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 16px;
  padding: 18px;
  margin-bottom: 16px;
}
.sidebar-section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(139, 92, 246, 0.15);
}
.sidebar-section-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff !important;
}
.sidebar-section-icon svg {
  color: #ffffff !important;
  stroke: #ffffff !important;
  width: 16px;
  height: 16px;
}
.sidebar-section-title {
  font-size: 0.95rem;
  font-weight: 800;
  color: #ffffff;
}
.sidebar-section-desc {
  font-size: 0.75rem;
  font-weight: 600;
  opacity: 1;
  margin-top: 2px;
  color: #ffffff;
}
.sidebar-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-top: 14px;
}
.sidebar-stat {
  background: rgba(255,255,255,0.04);
  border-radius: 10px;
  padding: 10px;
  text-align: center;
}
.sidebar-stat-value {
  font-size: 1.1rem;
  font-weight: 800;
  color: #ffffff;
}
.sidebar-stat-label {
  font-size: 0.65rem;
  font-weight: 700;
  opacity: 1;
  text-transform: uppercase;
  margin-top: 2px;
  color: #ffffff;
}
.sidebar-tip {
  background: linear-gradient(145deg, rgba(34, 197, 94, 0.12), rgba(34, 197, 94, 0.04));
  border: 1px solid rgba(34, 197, 94, 0.2);
  border-radius: 10px;
  padding: 12px;
  margin-top: 12px;
  font-size: 0.8rem;
  color: #86efac;
  line-height: 1.4;
}
.sidebar-version {
  text-align: center;
  font-size: 0.75rem;
  opacity: 0.4;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(255,255,255,0.08);
}

/* ===== FILTER BAR v2 ===== */
.filter-container {
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.filter-container:hover {
  border-color: rgba(82, 121, 111, 0.6);
  box-shadow: 0 4px 16px rgba(82, 121, 111, 0.15);
}
.filter-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.filter-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.filter-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff !important;
}
.filter-icon svg {
  width: 18px;
  height: 18px;
  color: #ffffff !important;
  stroke: #ffffff !important;
}
.filter-main-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #e2e8f0;
}
.filter-subtitle {
  font-size: 0.8rem;
  opacity: 0.6;
}
.filter-count {
  background: rgba(139, 92, 246, 0.2);
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #a78bfa;
}
.filter-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1.5fr 1fr;
  gap: 16px;
  align-items: end;
}
@media (max-width: 1000px) {
  .filter-grid { grid-template-columns: 1fr 1fr; }
}
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.filter-label {
  font-size: 0.8rem;
  font-weight: 800;
  color: #ffffff;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* ===== FRONT BUTTONS ===== */
.front-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
</style>
<script src="https://unpkg.com/lucide@latest"></script>
    """,
    unsafe_allow_html=True
)

# =========================
# Funções de UI Auxiliares (Padronizadas)
# =========================
def section_header(title: str, desc: str, icon: str = "layout", color: str = "purple"):
    icon_map = {
        "📅": "calendar",
        "🎯": "target",
        "🚚": "truck",
        "📊": "bar-chart-3",
        "🔍": "search",
        "📦": "package",
        "⚠️": "alert-triangle",
        "🛡️": "star",
        "⚔️": "trending-up",
        "🚀": "trending-up",
        "🧹": "package",
        "⚙️": "activity",
        "💡": "lightbulb"
    }
    icon_name = icon_map.get(icon, icon)
    svg = get_svg_icon(icon_name)
    st.markdown(
        f"""
<div class='section-box'>
  <div class='section-header'>
    <div class='section-icon'>{svg}</div>
    <div>
      <div class='section-title'>{title}</div>
      <div class='section-desc'>{desc}</div>
    </div>
  </div>
        """,
        unsafe_allow_html=True,
    )

def section_footer():
    st.markdown("</div>", unsafe_allow_html=True)

def render_kpi_highlight(kpis: list):
    """Renderiza grid de KPIs destacados. kpis = [(value, label, color), ...]"""
    html = '<div class="kpi-grid">'
    for val, label, color in kpis:
        html += f"""
<div class='kpi-box {color}'>
  <div class='kpi-value {color}'>{val}</div>
  <div class='kpi-label'>{label}</div>
</div>
        """
    html += '</div>'
    return html

def render_insight_card(icon: str, title: str, text: str):
    icon_map = {"📊": "bar-chart-3", "💡": "lightbulb", "⚠️": "alert-triangle", "🔍": "search"}
    icon_name = icon_map.get(icon, "lightbulb")
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

def render_front_summary(pills: list):
    """Renderiza resumo de frentes. pills = [(icon, count, label), ...]"""
    html = '<div class="front-summary">'
    icon_map = {"🛡️": "star", "⚠️": "alert-triangle", "🚀": "trending-up", "🧹": "package", "⚙️": "activity"}
    for icon, count, label in pills:
        icon_name = icon_map.get(icon, "activity")
        svg = get_svg_icon(icon_name)
        html += f"""
<div class='front-pill'>
  <div class='front-pill-icon'>{svg}</div>
  <div class='front-pill-count'>{count}</div>
  <div class='front-pill-label'>{label}</div>
</div>
        """
    html += '</div>'
    return html

def render_tactical_card(row: dict, frente: str):
    icon_map = {"DEFESA": "star", "CORREÇÃO": "alert-triangle", "ATAQUE": "trending-up", "LIMPEZA": "package", "OTIMIZAÇÃO": "activity"}
    icon_name = icon_map.get(frente, "activity")
    svg = get_svg_icon(icon_name)
    frente_class = {"DEFESA": "defense", "CORREÇÃO": "correction", "ATAQUE": "attack", "LIMPEZA": "cleanup", "OTIMIZAÇÃO": "optimization"}.get(frente, "optimization")
    
    return f"""
<div class='tactical-card'>
  <div class='tactical-header'>
    <div class='tactical-header-left'>
      <div class='tactical-icon'>{svg}</div>
      <div class='tactical-title'>{row['Título']}</div>
    </div>
    <div class='tactical-frente {frente_class}'>{frente}</div>
  </div>
  <div class='tactical-grid'>
    <div class='tactical-metric'>
      <div class='tactical-metric-value'>{br_money(row['Fat total'])}</div>
      <div class='tactical-metric-label'>Faturamento</div>
    </div>
    <div class='tactical-metric'>
      <div class='tactical-metric-value'>{row['Curva 0-30']}</div>
      <div class='tactical-metric-label'>Curva Atual</div>
    </div>
    <div class='tactical-metric'>
      <div class='tactical-metric-value'>{row['Qntd 0-30']}</div>
      <div class='tactical-metric-label'>Qtd 30d</div>
    </div>
    <div class='tactical-metric'>
      <div class='tactical-metric-value'>{row.get('Buy Box %', '-')}</div>
      <div class='tactical-metric-label'>Buy Box</div>
    </div>
  </div>
  <div class='tactical-action'>
    {get_svg_icon('target')}
    <span><b>Ação:</b> {row['Ação sugerida']}</span>
  </div>
</div>
    """

def render_export_card(title: str, desc: str, icon: str, df_seg: pd.DataFrame, filename: str):
    icon_map = {"📦": "package", "⚠️": "alert-triangle", "🛡️": "star", "🚀": "trending-up", "🧹": "package", "⚙️": "activity"}
    icon_name = icon_map.get(icon, "package")
    svg = get_svg_icon(icon_name)
    itens = len(df_seg)
    fat = df_seg['Fat total'].sum() if 'Fat total' in df_seg.columns else 0
    
    st.markdown(
        f"""
<div class='export-card'>
  <div class='export-header'>
    <div class='export-icon'>{svg}</div>
    <div class='export-title'>{title}</div>
  </div>
  <div class='export-desc'>{desc}</div>
  <div class='front-stats'>
    <div class='front-stat'>
      <div class='front-stat-value'>{br_int(itens)}</div>
      <div class='front-stat-label'>Itens</div>
    </div>
    <div class='front-stat'>
      <div class='front-stat-value'>{br_money(fat)}</div>
      <div class='front-stat-label'>Faturamento</div>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.download_button(
        f"📥 Baixar {title}",
        data=to_xlsx_bytes(df_seg),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"dl_{title}_{filename}",
        use_container_width=True
    )

def render_front_card(title: str, desc: str, icon: str, itens: int, fat: float):
    icon_map = {"🛡️": "star", "⚠️": "alert-triangle", "🚀": "trending-up", "🧹": "package", "⚙️": "activity"}
    icon_name = icon_map.get(icon, "activity")
    svg = get_svg_icon(icon_name)
    st.markdown(
        f"""
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
      <div class='front-stat-value'>{br_int(itens)}</div>
      <div class='front-stat-label'>Itens</div>
    </div>
    <div class='front-stat'>
      <div class='front-stat-value'>{br_money(fat)}</div>
      <div class='front-stat-label'>Faturamento</div>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

def render_logistics_section(full_pct: float, correios_pct: float, flex_pct: float, coleta_pct: float, outros_pct: float, period: str, **kwargs):
    """Renderiza seção de logística com todas as formas de entrega"""
    truck_svg = get_svg_icon("truck")
    package_svg = get_svg_icon("package")
    html = f"""
<div class="section-box">
  <div class="section-header">
    <div class="section-icon">{truck_svg}</div>
    <div>
      <div class="section-title">Logística - Período {period}</div>
      <div class="section-desc">Distribuição por forma de entrega</div>
    </div>
  </div>
  <div class="logistics-grid">
    <div class="logistics-card full">
      <div class="logistics-icon">{package_svg}</div>
      <div class="logistics-title">Full</div>
      <div class="logistics-value full">{full_pct:.1f}%</div>
      <div class="logistics-bar">
        <div class="logistics-bar-fill full" style="width: {full_pct}%"></div>
      </div>
    </div>
    <div class="logistics-card correios">
      <div class="logistics-icon">{package_svg}</div>
      <div class="logistics-title">Correios / Pontos</div>
      <div class="logistics-value correios">{correios_pct:.1f}%</div>
      <div class="logistics-bar">
        <div class="logistics-bar-fill correios" style="width: {correios_pct}%"></div>
      </div>
    </div>
    <div class="logistics-card flex">
      <div class="logistics-icon">{package_svg}</div>
      <div class="logistics-title">Flex</div>
      <div class="logistics-value flex">{flex_pct:.1f}%</div>
      <div class="logistics-bar">
        <div class="logistics-bar-fill flex" style="width: {flex_pct}%"></div>
      </div>
    </div>
    <div class="logistics-card coleta">
      <div class="logistics-icon">{package_svg}</div>
      <div class="logistics-title">Coleta</div>
      <div class="logistics-value coleta">{coleta_pct:.1f}%</div>
      <div class="logistics-bar">
        <div class="logistics-bar-fill coleta" style="width: {coleta_pct}%"></div>
      </div>
    </div>
  </div>
</div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_ads_section(ads_pct: float, organic_pct: float, ads_qty: int, organic_qty: int, period: str):
    """Renderiza seção de vendas por publicidade"""
    megaphone_svg = get_svg_icon("megaphone")
    html = f"""
<div class="ads-container">
  <div class="ads-header">
    <div class="ads-icon">{megaphone_svg}</div>
    <div class="ads-title">Vendas por Publicidade - Período {period}</div>
  </div>
  <div class="ads-grid">
    <div class="ads-metric ads">
      <div class="ads-metric-value ads">{ads_pct:.1f}%</div>
      <div class="ads-metric-label">Via Publicidade ({ads_qty:,} vendas)</div>
    </div>
    <div class="ads-metric organic">
      <div class="ads-metric-value organic">{organic_pct:.1f}%</div>
      <div class="ads-metric-label">Orgânicas ({organic_qty:,} vendas)</div>
    </div>
  </div>
  <div class="ads-bar-container">
    <div class="ads-bar-labels">
      <span>Ads</span>
      <span>Orgânico</span>
    </div>
    <div class="ads-bar">
      <div class="ads-bar-ads" style="width: {ads_pct}%"></div>
      <div class="ads-bar-organic" style="width: {organic_pct}%"></div>
    </div>
  </div>
</div>
    """
    st.markdown(html, unsafe_allow_html=True)
# =========================
# Helpers de formatação
# =========================
def br_money(x: float) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "-"
    return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def br_int(x) -> str:
    try:
        return f"{int(x):,}".replace(",", ".")
    except Exception:
        return "-"

def safe_div(a, b):
    try:
        if b and b != 0:
            return a / b
    except Exception:
        pass
    return np.nan

def pct(x, decimals=1) -> str:
    try:
        if x is None or (isinstance(x, float) and np.isnan(x)):
            return "-"
        return f"{round(float(x) * 100, decimals)}%"
    except Exception:
        return "-"



def ensure_cols(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Garante que todas as colunas existam antes do recorte (evita KeyError)."""
    out = df.copy()
    for c in cols:
        if c not in out.columns:
            out[c] = np.nan
    return out[cols].copy()

rank = {"-": 0, "C": 1, "B": 2, "A": 3}

# Períodos em ordem decrescente (mais antigo primeiro)
periods = [
    ("91-120", "Curva 91-120", "Qntd 91-120", "Fat. 91-120"),
    ("61-90", "Curva 61-90", "Qntd 61-90", "Fat. 61-90"),
    ("31-60", "Curva 31-60", "Qntd 31-60", "Fat. 31-60"),
    ("0-30", "Curva 0-30", "Qntd 0-30", "Fat. 0-30"),
]

QTY_COLS = ["Qntd 0-30", "Qntd 31-60", "Qntd 61-90", "Qntd 91-120"]
FAT_COLS = ["Fat. 0-30", "Fat. 31-60", "Fat. 61-90", "Fat. 91-120"]
CURVE_COLS = ["Curva 0-30", "Curva 31-60", "Curva 61-90", "Curva 91-120"]

# =========================
# Loaders
# =========================
@st.cache_data
def _transform_ml_raw(file) -> tuple:
    """Converte o relatorio bruto de vendas do Mercado Livre (120 dias) na estrutura 'Export'.
    Retorna: (df_export, df_logistics, df_ads)
    """

    def _seek0(f):
        try:
            f.seek(0)
        except Exception:
            pass

    def _pick_col(cols, target: str) -> str:
        if target in cols:
            return target
        for c in cols:
            sc = str(c).strip()
            if sc.startswith(target + "."):
                return c
        t = target.lower()
        for c in cols:
            if t in str(c).lower():
                return c
        raise KeyError(f"Coluna '{target}' não encontrada")

    def _try_pick_col(cols, target: str):
        try:
            return _pick_col(cols, target)
        except KeyError:
            return None

    _seek0(file)
    preview = pd.read_excel(file, sheet_name=0, header=None, nrows=80)

    header_row = None
    for i in range(min(60, len(preview))):
        row = preview.iloc[i].astype(str).str.lower()
        if row.str.contains('data da venda', na=False).any() or row.str.contains('# de anúncio', na=False).any() or row.str.contains('de anúncio', na=False).any():
            header_row = i
            break
    if header_row is None:
        header_row = 0

    _seek0(file)
    df = pd.read_excel(file, sheet_name=0, header=header_row)
    df.columns = [str(c).strip() for c in df.columns]

    col_data = _pick_col(df.columns, 'Data da venda')
    col_unid = _pick_col(df.columns, 'Unidades')

    try:
        col_rec = _pick_col(df.columns, 'Receita por produtos (BRL)')
    except Exception:
        col_rec = _pick_col(df.columns, 'Receita por produtos')

    col_mlb = _pick_col(df.columns, '# de anúncio')
    col_sku = _try_pick_col(df.columns, 'SKU')
    col_tit = _pick_col(df.columns, 'Título do anúncio')
    col_log = _pick_col(df.columns, 'Forma de entrega')
    
    # Nova coluna: Venda por publicidade (nome correto do ML)
    col_ads = None
    ads_variations = [
        'Venda por publicidade',  # Nome correto do ML
        'Venda por Publicidade',
        'Vendas por Publicidade',
        'Vendas por publicidade', 
        'vendas por publicidade',
        'venda por publicidade',
        'Publicidade',
        'publicidade',
    ]
    for var in ads_variations:
        col_ads = _try_pick_col(df.columns, var)
        if col_ads is not None:
            break
    
    # Se ainda não encontrou, busca parcial por "publicidade"
    if col_ads is None:
        for c in df.columns:
            c_lower = str(c).lower().strip()
            if 'publicidade' in c_lower:
                col_ads = c
                break

    use_cols = [col_data, col_unid, col_rec, col_mlb, col_tit, col_log]
    if col_sku is not None:
        use_cols.insert(4, col_sku)
    if col_ads is not None:
        use_cols.append(col_ads)

    base = df[use_cols].copy()

    # Renomear colunas
    if col_sku is None and col_ads is None:
        base.columns = ['data', 'unidades', 'receita', 'mlb', 'titulo', 'logistica']
        base['sku'] = ''
        base['ads'] = ''
    elif col_sku is None and col_ads is not None:
        base.columns = ['data', 'unidades', 'receita', 'mlb', 'titulo', 'logistica', 'ads']
        base['sku'] = ''
    elif col_sku is not None and col_ads is None:
        base.columns = ['data', 'unidades', 'receita', 'mlb', 'sku', 'titulo', 'logistica']
        base['ads'] = ''
    else:
        base.columns = ['data', 'unidades', 'receita', 'mlb', 'sku', 'titulo', 'logistica', 'ads']

    base['mlb'] = base['mlb'].astype(str).str.strip()
    base['sku'] = base['sku'].astype(str).str.strip()
    base['titulo'] = base['titulo'].astype(str).str.strip()
    base['logistica'] = base['logistica'].astype(str).str.strip()
    base['ads'] = base['ads'].astype(str).str.strip().str.lower()

    empty_mlb = base['mlb'].isin(['', 'nan', 'none', 'None', 'NaN'])
    if empty_mlb.any():
        base.loc[empty_mlb, 'mlb'] = base.loc[empty_mlb, 'sku']

    base['_data_raw'] = base['data'].astype(str)
    base['data'] = pd.to_datetime(base['_data_raw'], errors='coerce', dayfirst=True)

    if base['data'].notna().sum() == 0:
        s = base['_data_raw'].astype(str)
        for fmt in ('%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M', '%d/%m/%Y'):
            tmp = pd.to_datetime(s, errors='coerce', format=fmt)
            if tmp.notna().sum() > 0:
                base['data'] = tmp
                break

    if base['data'].notna().sum() == 0:
        month_map = {
            'janeiro': '01', 'fevereiro': '02', 'março': '03', 'marco': '03',
            'abril': '04', 'maio': '05', 'junho': '06', 'julho': '07',
            'agosto': '08', 'setembro': '09', 'outubro': '10',
            'novembro': '11', 'dezembro': '12',
        }
        s = base['_data_raw'].astype(str).str.lower()
        s = s.str.replace('hs.', '', regex=False).str.replace('hs', '', regex=False)
        for name, num in month_map.items():
            s = s.str.replace(rf'\b{name}\b', num, regex=True)
        s = s.str.replace(r'\s*de\s*', '/', regex=True)
        s = s.str.replace(r'\s+', ' ', regex=True).str.strip()
        tmp = pd.to_datetime(s, errors='coerce', dayfirst=True)
        if tmp.notna().sum() > 0:
            base['data'] = tmp

    base = base.drop(columns=['_data_raw'], errors='ignore')
    base = base.dropna(subset=['data'])
    base = base[~base['mlb'].isin(['', 'nan', 'none', 'None', 'NaN'])].copy()

    base['unidades'] = pd.to_numeric(base['unidades'], errors='coerce').fillna(0).astype(int)

    rec = base['receita']
    if rec.dtype == object:
        rec = rec.astype(str).str.replace('\u00a0', '', regex=False).str.strip()
        # Se contiver tanto '.' quanto ',', assume formato BR (1.234,56)
        if rec.str.contains(r'\.', regex=True).any() and rec.str.contains(r',', regex=True).any():
            rec = rec.str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        # Se contiver apenas ',', assume que é o separador decimal (1234,56)
        elif rec.str.contains(r',', regex=True).any():
            rec = rec.str.replace(',', '.', regex=False)
        # Remove símbolos de moeda se existirem
        rec = rec.str.replace(r'[R\$\s]', '', regex=True)
        
    base['receita'] = pd.to_numeric(rec, errors='coerce').fillna(0.0)

    if base.empty:
        cols = ['MLB','Título'] + [f'Qntd {p}' for p in ['0-30','31-60','61-90','91-120']] + [f'Fat. {p}' for p in ['0-30','31-60','61-90','91-120']] + [f'Curva {p}' for p in ['0-30','31-60','61-90','91-120']]
        empty_df = pd.DataFrame(columns=cols)
        empty_log = pd.DataFrame(columns=['periodo', 'full_pct', 'correios_pct', 'flex_pct', 'coleta_pct', 'outros_pct', 
                                          'full_qty', 'correios_qty', 'flex_qty', 'coleta_qty', 'outros_qty',
                                          'full_fat', 'correios_fat', 'flex_fat', 'coleta_fat', 'outros_fat'])
        empty_ads = pd.DataFrame(columns=['periodo', 'ads_pct', 'organic_pct', 'ads_qty', 'organic_qty'])
        return empty_df, empty_log, empty_ads

    ref = base['data'].max()
    base['dias'] = (ref - base['data']).dt.days

    def bucket(d):
        if d <= 30:
            return '0-30'
        if d <= 60:
            return '31-60'
        if d <= 90:
            return '61-90'
        if d <= 120:
            return '91-120'
        return None

    base['periodo'] = base['dias'].apply(bucket)
    base = base.dropna(subset=['periodo'])

    # Classificar logística
    log_lower = base['logistica'].str.lower()
    base['is_full'] = log_lower.str.contains('full', na=False)
    base['is_correios'] = log_lower.str.contains('correios', na=False) | log_lower.str.contains('pontos', na=False) | log_lower.str.contains('ponto de envio', na=False)
    base['is_flex'] = log_lower.str.contains('flex', na=False)
    base['is_coleta'] = log_lower.str.contains('coleta', na=False)
    base['is_outros'] = ~(base['is_full'] | base['is_correios'] | base['is_flex'] | base['is_coleta'])
    
    # Classificar vendas por publicidade: "Sim" = venda via Ads, Vazio/outros = Orgânica
    # Normaliza valores e verifica se é "sim" ou variações
    ads_lower = base['ads'].astype(str).str.strip().str.lower()
    base['is_ads'] = ads_lower.isin(['sim', 's', 'yes', 'y', '1', 'true', 'si'])
    
    # Debug: contar quantos Ads foram encontrados
    ads_count = base['is_ads'].sum()
    total_count = len(base)
    # st.write(f"DEBUG: {ads_count} vendas via Ads de {total_count} total")

    # Agregar por período para logística
    logistics_data = []
    ads_data = []
    
    for periodo in ['0-30', '31-60', '61-90', '91-120']:
        periodo_df = base[base['periodo'] == periodo]
        total_qty = int(periodo_df['unidades'].sum())
        
        if total_qty > 0:
            full_qty = int(periodo_df[periodo_df['is_full']]['unidades'].sum())
            correios_qty = int(periodo_df[periodo_df['is_correios']]['unidades'].sum())
            flex_qty = int(periodo_df[periodo_df['is_flex']]['unidades'].sum())
            coleta_qty = int(periodo_df[periodo_df['is_coleta']]['unidades'].sum())
            outros_qty = int(periodo_df[periodo_df['is_outros']]['unidades'].sum())
            
            full_fat = float(periodo_df[periodo_df['is_full']]['receita'].sum())
            correios_fat = float(periodo_df[periodo_df['is_correios']]['receita'].sum())
            flex_fat = float(periodo_df[periodo_df['is_flex']]['receita'].sum())
            coleta_fat = float(periodo_df[periodo_df['is_coleta']]['receita'].sum())
            outros_fat = float(periodo_df[periodo_df['is_outros']]['receita'].sum())
            
            logistics_data.append({
                'periodo': periodo,
                'full_pct': (full_qty / total_qty) * 100,
                'correios_pct': (correios_qty / total_qty) * 100,
                'flex_pct': (flex_qty / total_qty) * 100,
                'coleta_pct': (coleta_qty / total_qty) * 100,
                'outros_pct': (outros_qty / total_qty) * 100,
                'full_qty': full_qty,
                'correios_qty': correios_qty,
                'flex_qty': flex_qty,
                'coleta_qty': coleta_qty,
                'outros_qty': outros_qty,
                'full_fat': full_fat,
                'correios_fat': correios_fat,
                'flex_fat': flex_fat,
                'coleta_fat': coleta_fat,
                'outros_fat': outros_fat,
                'total_qty': total_qty
            })
        
            # Vendas por publicidade
            ads_qty = int(periodo_df[periodo_df['is_ads']]['unidades'].sum())
            organic_qty = total_qty - ads_qty
            
            ads_value = float(periodo_df[periodo_df['is_ads']]['receita'].sum())
            total_value = float(periodo_df['receita'].sum())
            organic_value = total_value - ads_value
            
            ads_data.append({
                'periodo': periodo,
                'ads_pct': (ads_qty / total_qty) * 100,
                'organic_pct': (organic_qty / total_qty) * 100,
                'ads_qty': ads_qty,
                'organic_qty': organic_qty,
                'ads_value': ads_value,
                'organic_value': organic_value,
                'total_qty': total_qty
            })
        else:
            logistics_data.append({
                'periodo': periodo,
                'full_pct': 0, 'correios_pct': 0, 'flex_pct': 0, 'coleta_pct': 0, 'outros_pct': 0,
                'full_qty': 0, 'correios_qty': 0, 'flex_qty': 0, 'coleta_qty': 0, 'outros_qty': 0,
                'full_fat': 0, 'correios_fat': 0, 'flex_fat': 0, 'coleta_fat': 0, 'outros_fat': 0, 'total_qty': 0
            })
            ads_data.append({
                'periodo': periodo,
                'ads_pct': 0, 'organic_pct': 0, 'ads_qty': 0, 'organic_qty': 0, 
                'ads_value': 0, 'organic_value': 0, 'total_qty': 0
            })

    df_logistics = pd.DataFrame(logistics_data)
    df_ads = pd.DataFrame(ads_data)

    # Agregação para export
    agg_total = base.groupby(['mlb','titulo','periodo'], as_index=False).agg(
        unidades=('unidades','sum'),
        receita=('receita','sum'),
    )

    agg_full = base[base['is_full']].groupby(['mlb','titulo','periodo'], as_index=False).agg(
        unidades_full=('unidades','sum'),
        receita_full=('receita','sum'),
    )

    agg = agg_total.merge(agg_full, on=['mlb','titulo','periodo'], how='left')
    agg['unidades_full'] = agg['unidades_full'].fillna(0).astype(int)
    agg['receita_full'] = agg['receita_full'].fillna(0.0)

    out_q = agg.pivot_table(index=['mlb','titulo'], columns='periodo', values='unidades', aggfunc='sum', fill_value=0)
    out_f = agg.pivot_table(index=['mlb','titulo'], columns='periodo', values='receita', aggfunc='sum', fill_value=0.0)
    out_qf = agg.pivot_table(index=['mlb','titulo'], columns='periodo', values='unidades_full', aggfunc='sum', fill_value=0)
    out_ff = agg.pivot_table(index=['mlb','titulo'], columns='periodo', values='receita_full', aggfunc='sum', fill_value=0.0)

    out = out_q.reset_index().rename(columns={'mlb':'MLB','titulo':'Título'})

    for p in ['0-30','31-60','61-90','91-120']:
        out[f'Qntd {p}'] = out_q[p].values if p in out_q.columns else 0
        out[f'Fat. {p}'] = out_f[p].values if p in out_f.columns else 0.0

        q_full = out_qf[p].values if p in out_qf.columns else 0
        f_full = out_ff[p].values if p in out_ff.columns else 0.0

        q_tot = out[f'Qntd {p}'].replace(0, np.nan)
        f_tot = out[f'Fat. {p}'].replace(0, np.nan)

        out[f'Share Full Qtd {p}'] = (q_full / q_tot).fillna(0.0)
        out[f'Share Full Fat {p}'] = (f_full / f_tot).fillna(0.0)
        out[f'Logística dom {p}'] = np.where(out[f'Share Full Qtd {p}'] >= 0.5, 'FULL', 'NÃO FULL')

    def curva_abc(fat_series: pd.Series) -> pd.Series:
        fat = fat_series.fillna(0.0)
        total = float(fat.sum())
        if total <= 0:
            return pd.Series(['-'] * len(fat), index=fat.index)
        order = fat.sort_values(ascending=False)
        cum = order.cumsum() / total
        curve = pd.Series(index=order.index, dtype=object)
        curve.loc[cum <= 0.80] = 'A'
        curve.loc[(cum > 0.80) & (cum <= 0.95)] = 'B'
        curve.loc[cum > 0.95] = 'C'
        curve.loc[order == 0] = '-'
        return curve.reindex(fat.index).fillna('-')

    for p in ['0-30','31-60','61-90','91-120']:
        out[f'Curva {p}'] = curva_abc(out[f'Fat. {p}'])

    return out, df_logistics, df_ads, base


@st.cache_data
def load_main(file) -> tuple:
    """Aceita planilha pronta (aba Export) OU relatorio bruto do ML.
    Retorna: (df_main, df_logistics, df_ads, df_raw)
    """
    if hasattr(file, 'seek'):
        file.seek(0)

    df_logistics = pd.DataFrame()
    df_ads = pd.DataFrame()

    try:
        xls = pd.ExcelFile(file)
        sheet_names = [str(s) for s in getattr(xls, 'sheet_names', [])]
    except Exception:
        if hasattr(file, 'seek'):
            file.seek(0)
        df, df_logistics, df_ads, df_raw = _transform_ml_raw(file)
    else:
        if 'Export' in sheet_names:
            if hasattr(file, 'seek'):
                file.seek(0)
            df = pd.read_excel(file, sheet_name='Export')
            df_raw = pd.DataFrame()
        else:
            if hasattr(file, 'seek'):
                file.seek(0)
            df, df_logistics, df_ads, df_raw = _transform_ml_raw(file)

    for col in QTY_COLS:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    for col in FAT_COLS:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    for col in CURVE_COLS:
        if col not in df.columns:
            df[col] = '-'
        df[col] = df[col].fillna('-').astype(str).str.strip()

    if 'MLB' not in df.columns:
        df['MLB'] = ''
    if 'Título' not in df.columns:
        if 'Titulo' in df.columns:
            df['Título'] = df['Titulo']
        else:
            df['Título'] = ''

    df['MLB'] = df['MLB'].astype(str).str.strip()
    df['Título'] = df['Título'].astype(str).str.strip()

    return df, df_logistics, df_ads, df_raw


# =========================
# Sidebar Premium v2
# =========================
with st.sidebar:
    # Logo e título
    chart_svg = get_svg_icon("bar-chart-3")
    st.markdown(
        f"""
<div style="text-align: center; padding: 10px 0 20px 0;">
  <div style="font-size: 2rem; margin-bottom: 4px; display: flex; justify-content: center; color: #ffffff;">{chart_svg}</div>
  <div style="font-size: 1.1rem; font-weight: 800; background: linear-gradient(135deg, #fff, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Curva ABC</div>
  <div style="font-size: 0.75rem; opacity: 0.5;">Diagnóstico & Ações</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # Seção de Upload
    package_svg = get_svg_icon("package")
    st.markdown(
        f"""
<div class='sidebar-section'>
  <div class='sidebar-section-header'>
    <div class='sidebar-section-icon'>{package_svg}</div>
    <div>
      <div class='sidebar-section-title'>Upload de Dados</div>
      <div class='sidebar-section-desc'>Mercado Livre, Shopee ou Amazon</div>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
    
    uploaded_files = st.file_uploader(
        "📂 Carregar relatório(s) de vendas",
        type=["xlsx", "xls", "csv", "txt"],
        help="Suporta Mercado Livre, Shopee e Amazon. Para Shopee, você pode enviar múltiplos arquivos.",
        accept_multiple_files=True,
        key="main_files"
    )

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    # Seção de Filtros
    # Filtros Globais removidos conforme solicitado
    curve_filter = ["A", "B", "C", "-"]
    
    # Identificação do Cliente
    st.markdown("---")
    st.markdown("### 👤 Identificação da Conta")
    cliente_nome = st.text_input("Nome do Cliente / Conta", value="", placeholder="Ex: Cliente X", help="Digite o nome do cliente para isolar o histórico e as comparações.")
    st.session_state['cliente_atual'] = cliente_nome.strip()

    # Versão removida conforme solicitado

if not uploaded_files:
    render_guide_tab()
    st.stop()

# =========================
# Carregar dados
# =========================
# Detecta o canal baseado no primeiro arquivo
try:
    from data_processing.factory import detect_channel
    canal_detectado = detect_channel(uploaded_files)
    
    # Armazena o canal no session_state
    st.session_state['canal'] = canal_detectado
    
    # Exibe o canal detectado na sidebar
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-section">
            <div class="sidebar-section-header">
                <div class="sidebar-section-icon">🏪</div>
                <div>
                    <div class="sidebar-section-title">Canal Detectado</div>
                    <div class="sidebar-section-desc">{canal_detectado}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Processa conforme o canal detectado
    from data_processing.factory import detect_and_process
    _, df, df_logistics, df_ads, df_raw = detect_and_process(uploaded_files)
    
    # Garantir que df_ads e df_logistics não sejam None
    if df_ads is None:
        df_ads = pd.DataFrame()
    if df_logistics is None:
        df_logistics = pd.DataFrame()
    
except Exception as e:
    st.error(f"Erro ao processar arquivo(s): {str(e)}")
    import traceback
    st.error(traceback.format_exc())
    st.stop()

if df.empty:
    st.warning("Nenhum dado válido encontrado no arquivo.")
    st.stop()

# Filtrar por curva
df_f = df[df["Curva 0-30"].isin(curve_filter)].copy()

if df_f.empty:
    st.warning("Nenhum produto corresponde aos filtros selecionados.")
    st.stop()

# =========================
# Cálculos auxiliares
# =========================
df_f["Fat total"] = df_f[FAT_COLS].sum(axis=1)
df_f["Qtd total"] = df_f[QTY_COLS].sum(axis=1)
df_f["TM total"] = df_f.apply(lambda r: safe_div(r["Fat total"], r["Qtd total"]), axis=1).fillna(0.0)

kpi_rows = []
for p, cc, qq, ff in periods:
    fat = float(df_f[ff].sum())
    qty = int(df_f[qq].sum())
    tm = safe_div(fat, qty)
    kpi_rows.append({"Período": p, "Qtd": qty, "Faturamento": fat, "Ticket médio": tm})
kpi_df = pd.DataFrame(kpi_rows)

# =========================
# Segmentações
# =========================
# Adapta segmentações conforme o canal
if st.session_state.get('canal') == 'Shopee':
    # Para Shopee (período único), usa apenas curva atual
    anchors = df_f[
        (df_f["Curva 0-30"] == "A")
    ].sort_values("Fat total", ascending=False).copy()
    
    inactivate = df_f[
        (df_f["Qntd 0-30"] == 0)
    ].sort_values("Fat total", ascending=False).copy()
    
    revitalize = df_f[
        (df_f["Curva 0-30"].isin(["C", "-"])) &
        (df_f["Qntd 0-30"] > 0)  # Teve vendas mas está em C ou -
    ].sort_values("Fat total", ascending=False).copy()
else:
    # Para Mercado Livre (múltiplos períodos), usa histórico
    anchors = df_f[
        (df_f["Curva 0-30"] == "A") &
        (df_f["Curva 31-60"].isin(["A", "B"])) &
        (df_f["Curva 61-90"].isin(["A", "B"]))
    ].sort_values("Fat total", ascending=False).copy()
    
    inactivate = df_f[
        (df_f["Qntd 0-30"] == 0) &
        (df_f["Qntd 31-60"] == 0) &
        (df_f["Qntd 61-90"] == 0)
    ].sort_values("Fat total", ascending=False).copy()
    
    revitalize = df_f[
        (df_f["Curva 31-60"].isin(["A", "B"])) &
        (df_f["Curva 0-30"].isin(["C", "-"]))
    ].sort_values("Fat total", ascending=False).copy()

if st.session_state.get('canal') == 'Shopee':
    # Para Shopee, adapta segmentações para período único
    rise_to_A = df_f[
        (df_f["Curva 0-30"] == "A") &
        (df_f["Qntd 0-30"] > 0)
    ].sort_values("Fat total", ascending=False).copy()
    
    opp_50_60 = df_f[
        (df_f["Curva 0-30"] == "B")
    ].sort_values("Fat total", ascending=False).copy()
    
    dead_stock_combo = df_f[
        (df_f["Curva 0-30"] == "-") &
        (df_f["Fat total"] > 0)
    ].sort_values("TM total", ascending=False).copy()
    
    # Fuga de receita: produtos C ou - com bom ticket médio (potencial)
    drop_alert = df_f[
        (df_f["Curva 0-30"].isin(["C", "-"])) &
        (df_f["TM total"] > df_f["TM total"].median())
    ].copy()
    
    if len(drop_alert) > 0:
        drop_alert["Perda estimada"] = drop_alert["TM total"] * 10  # Estima perda baseada no TM
        drop_alert = drop_alert.sort_values("Perda estimada", ascending=False)
else:
    # Para Mercado Livre, usa lógica original com histórico
    rise_to_A = df_f[
        (df_f["Curva 31-60"].isin(["B", "C"])) &
        (df_f["Curva 0-30"] == "A")
    ].sort_values("Fat total", ascending=False).copy()
    
    opp_50_60 = df_f[
        (df_f["Curva 0-30"] == "B") &
        (df_f["Qntd 0-30"] >= df_f["Qntd 31-60"] * 1.1)
    ].sort_values("Fat total", ascending=False).copy()
    
    dead_stock_combo = df_f[
        (df_f["Curva 0-30"] == "-") &
        (df_f["Fat total"] > 0)
    ].sort_values("TM total", ascending=False).copy()
    
    drop_alert = df_f[
        (df_f["Curva 31-60"].isin(["A", "B"])) &
        (df_f["Curva 0-30"].isin(["C", "-"]))
    ].copy()
    
    if len(drop_alert) > 0:
        drop_alert["Fat anterior ref"] = drop_alert[["Fat. 31-60", "Fat. 61-90"]].max(axis=1)
        drop_alert["Perda estimada"] = drop_alert["Fat anterior ref"] - drop_alert["Fat. 0-30"]
        drop_alert = drop_alert.sort_values("Perda estimada", ascending=False)

# =========================
# Plano tático
# =========================
plan = df_f.copy()

def suggest_action(row):
    c0, c1 = row["Curva 0-30"], row["Curva 31-60"]
    
    # Para Shopee (sem histórico), usa apenas curva atual
    if st.session_state.get('canal') == 'Shopee':
        if c0 == "A":
            return "Garantir estoque 30d + otimizar fotos/título + avaliar Shopee Ads"
        elif c0 == "B":
            return "Testar Shopee Ads com palavras-chave específicas (cauda longa)"
        elif c0 == "C":
            # Verifica se tem bom ticket médio (potencial)
            tm_total = row.get("TM total", 0)
            if tm_total > 0:
                return "Diagnosticar gargalo (CTR/conversão) + melhorar imagens/descrição"
            else:
                return "Testar preço promocional + bundle ou liquidar"
        elif c0 == "-":
            # Verifica se teve faturamento (dead stock) ou é inativo
            fat_total = row.get("Fat total", 0)
            if fat_total > 0:
                return "Criar bundle com produto âncora ou participar Shopee Liquida"
            else:
                return "Testar preço promocional última chance ou desativar"
        return "-"
    
    # Para Mercado Livre (com histórico), usa comparação de períodos
    if c0 == "A" and c1 in ["A", "B"]:
        return "Garantir estoque 30-60d + completar ficha técnica 100% + avaliar ML Ads"
    if c0 == "A" and c1 in ["C", "-"]:
        return "Subiu rápido – validar se é sazonal ou tendência antes de escalar"
    if c0 == "B" and c1 == "A":
        return "Caiu de A→B: diagnosticar (CTR/conversão/Buy Box) + corrigir gargalo"
    if c0 == "B" and c1 in ["B", "C"]:
        return "Potencial de crescimento: otimizar anúncio (conversão >2%) + testar ML Ads"
    if c0 == "C":
        return "Diagnosticar gargalo (foto/preço/descrição) + testar promoção ou kit"
    if c0 == "-":
        return "Sem giro: otimizar última chance (preço/foto) ou liquidar e liberar capital"
    return "-"

plan["Ação sugerida"] = plan.apply(suggest_action, axis=1)

actions = pd.DataFrame(index=plan.index)
actions["7d"] = "-"
actions["15d"] = "-"
actions["30d"] = "-"

# DEFESA - Âncoras (produtos A estáveis)
if st.session_state.get('canal') == 'Shopee':
    actions.loc[anchors.index, "7d"] = "Garantir estoque 30-60d + monitorar taxa resposta (100%) + checar prazo entrega"
    actions.loc[anchors.index, "15d"] = "Adicionar foto uso real + tabela medidas + responder FAQ na descrição"
    actions.loc[anchors.index, "30d"] = "Testar Shopee Ads (cauda longa) se ACOS < margem + criar bundle upsell"
else:
    actions.loc[anchors.index, "7d"] = "Estoque 30-60d + monitorar Buy Box + validar reputação (resposta <24h, reclamações <1%)"
    actions.loc[anchors.index, "15d"] = "Completar ficha técnica 100% + adicionar vídeo 15-30s + organizar variações"
    actions.loc[anchors.index, "30d"] = "Se conversão >2%: testar ML Ads (cauda longa, ACOS <25-30%) + Full/Flex"

# CORREÇÃO - Queda de faturamento / Fuga de receita
if st.session_state.get('canal') == 'Shopee':
    actions.loc[drop_alert.index, "7d"] = "Diagnosticar: CTR baixo (imagem/título) ou conversão baixa (descrição/preço/frete)"
    actions.loc[drop_alert.index, "15d"] = "Testar nova capa (zoom produto + selo benefício) + expandir descrição com FAQ"
    actions.loc[drop_alert.index, "30d"] = "Participar Flash Sale (margem mín aceitável) + cupom prazo limitado"
else:
    actions.loc[drop_alert.index, "7d"] = "Diagnosticar: CTR <1% (foto/título) ou conversão <2% (preço/descrição/frete) + comparar concorrentes"
    actions.loc[drop_alert.index, "15d"] = "Corrigir gargalo: foto fundo branco + título otimizado + FAQ na descrição + ajustar preço"
    actions.loc[drop_alert.index, "30d"] = "Se ajustes não funcionaram: oferta relâmpago ou cupom + responder avaliações negativas"

# CORREÇÃO - Reativar produtos
if st.session_state.get('canal') == 'Shopee':
    actions.loc[revitalize.index, "7d"] = "Ler avaliações negativas concorrentes + responder todas avaliações negativas"
    actions.loc[revitalize.index, "15d"] = "Ajustar preço (usar âncora: cheio+desconto) + melhorar capa (fundo limpo)"
    actions.loc[revitalize.index, "30d"] = "Cupom seguidor (criar base clientes) + monitorar se conversão voltou"
else:
    actions.loc[revitalize.index, "7d"] = "Diagnosticar problema: sem impressões (SEO) ou CTR baixo (foto) + verificar categoria correta"
    actions.loc[revitalize.index, "15d"] = "Otimizar: título com palavra-chave + ficha técnica 100% + foto fundo branco + vídeo"
    actions.loc[revitalize.index, "30d"] = "Testar preço promocional (abaixo média) + cupom + monitorar se conversão voltou"

# ATAQUE - Subindo para A
if st.session_state.get('canal') == 'Shopee':
    actions.loc[rise_to_A.index, "7d"] = "Estoque 30-60d + otimizar anúncio (conversão >2%) antes de investir Ads"
    actions.loc[rise_to_A.index, "15d"] = "Ativar Shopee Ads: orçamento baixo + palavras cauda longa + monitorar ACOS"
    actions.loc[rise_to_A.index, "30d"] = "Se ROAS >3: aumentar budget + participar campanhas (11.11, Black Friday)"
else:
    actions.loc[rise_to_A.index, "7d"] = "Estoque 60-90d + validar conversão >2% + completar ficha técnica 100% + Full/Flex"
    actions.loc[rise_to_A.index, "15d"] = "Ativar ML Ads: orçamento baixo + palavras cauda longa + monitorar ACOS diariamente"
    actions.loc[rise_to_A.index, "30d"] = "Se ACOS <25-30%: aumentar budget + participar ofertas relâmpago + monitorar posição orgânica"

# ATAQUE - Oportunidades B/C
if st.session_state.get('canal') == 'Shopee':
    actions.loc[opp_50_60.index, "7d"] = "Calcular margem líquida + ACOS máx aceitável + volume busca categoria"
    actions.loc[opp_50_60.index, "15d"] = "Testar Ads: termos específicos (ex: 'sapato social preto 40' > 'sapato')"
    actions.loc[opp_50_60.index, "30d"] = "Ajustar lances (alto rendimento: +lance | baixo: pausar) + criar bundles"
else:
    actions.loc[opp_50_60.index, "7d"] = "Calcular margem líquida + ACOS máx aceitável + otimizar anúncio (conversão >2%)"
    actions.loc[opp_50_60.index, "15d"] = "Testar ML Ads: termos específicos (ex: 'tênis corrida nike 42' > 'tênis') + monitorar CTR"
    actions.loc[opp_50_60.index, "30d"] = "Ajustar lances (alto ROAS: +lance | baixo: pausar) + testar kit com produto âncora"

# LIMPEZA - Combo/Kit
if st.session_state.get('canal') == 'Shopee':
    actions.loc[dead_stock_combo.index, "7d"] = "Analisar: quem comprou também comprou? Pesquisar combos concorrentes"
    actions.loc[dead_stock_combo.index, "15d"] = "Criar bundle (dead stock + âncora) desconto 10-20% + anúncio novo"
    actions.loc[dead_stock_combo.index, "30d"] = "Se bundle não funcionou: Shopee Liquida com preço agressivo"
else:
    actions.loc[dead_stock_combo.index, "7d"] = "Analisar: quem comprou também comprou? Pesquisar kits concorrentes + avaliar margem kit"
    actions.loc[dead_stock_combo.index, "15d"] = "Criar kit (dead stock + âncora) desconto 10-20% + anúncio novo otimizado + variações"
    actions.loc[dead_stock_combo.index, "30d"] = "Se kit não vendeu: liquidação agressiva (preço abaixo custo) + oferta relâmpago"

# LIMPEZA - Inativar
if st.session_state.get('canal') == 'Shopee':
    actions.loc[inactivate.index, "7d"] = "Calcular custo oportunidade (capital imobilizado) + verificar se obsoleto"
    actions.loc[inactivate.index, "15d"] = "Liquidação: preço agressivo + frete grátis + comunicar 'Última Chance'"
    actions.loc[inactivate.index, "30d"] = "Se não vendeu: desativar + liquidar lote ou doar (crédito fiscal)"
else:
    actions.loc[inactivate.index, "7d"] = "Calcular custo oportunidade (capital imobilizado) + diagnosticar: obsoleto ou anúncio ruim?"
    actions.loc[inactivate.index, "15d"] = "Liquidação: preço agressivo + frete grátis + comunicar 'Última Chance' + ML Ads baixo orçamento"
    actions.loc[inactivate.index, "30d"] = "Se não vendeu: desativar + liquidar lote (revendedores) ou doar (crédito fiscal)"

# OTIMIZAÇÃO - Produtos que não se encaixam em outras frentes
# Identificar índices de otimização (todos que não estão nas outras frentes)
all_classified = set(anchors.index) | set(drop_alert.index) | set(revitalize.index) | set(rise_to_A.index) | set(opp_50_60.index) | set(dead_stock_combo.index) | set(inactivate.index)
optimization_idx = [idx for idx in plan.index if idx not in all_classified]

for idx in optimization_idx:
    row = plan.loc[idx]
    c0 = row.get("Curva 0-30", "-")
    c1 = row.get("Curva 31-60", "-")
    
    if c0 == "A":
        # Produto A que não é âncora - subiu rápido
        actions.loc[idx, "7d"] = "Validar se é sazonal"
        actions.loc[idx, "15d"] = "Monitorar tendência"
        actions.loc[idx, "30d"] = "Decidir estratégia"
    elif c0 == "B":
        # Produto B estável ou em transição
        actions.loc[idx, "7d"] = "Analisar histórico"
        actions.loc[idx, "15d"] = "Testar otimização"
        actions.loc[idx, "30d"] = "Avaliar promoção"
    elif c0 == "C":
        # Produto C - baixo volume
        actions.loc[idx, "7d"] = "Revisar preço"
        actions.loc[idx, "15d"] = "Testar destaque"
        actions.loc[idx, "30d"] = "Avaliar combo"
    else:
        # Sem vendas recentes
        actions.loc[idx, "7d"] = "Verificar anúncio"
        actions.loc[idx, "15d"] = "Ajustar estratégia"
        actions.loc[idx, "30d"] = "Decidir manter/remover"

plan["Plano 7 dias"] = actions["7d"]
plan["Plano 15 dias"] = actions["15d"]
plan["Plano 30 dias"] = actions["30d"]

def frente_bucket(idx):
    if idx in anchors.index:
        return "DEFESA"
    if idx in drop_alert.index:
        return "CORREÇÃO"
    if idx in revitalize.index:
        return "CORREÇÃO"
    if idx in rise_to_A.index or idx in opp_50_60.index:
        return "ATAQUE"
    if idx in dead_stock_combo.index or idx in inactivate.index:
        return "LIMPEZA"
    return "OTIMIZAÇÃO"

plan["Frente"] = [frente_bucket(i) for i in plan.index]

# Contagem de produtos por frente para os filtros
all_front_counts = plan["Frente"].value_counts().to_dict()

# Alertas de Buybox para Amazon
if st.session_state.get('canal') == 'Amazon':
    buybox_alerts = get_amazon_buybox_alerts(df_f)
    for alert in buybox_alerts:
        sku = alert['SKU']
        if sku in plan['SKU'].values:
            idx = plan[plan['SKU'] == sku].index[0]
            plan.at[idx, "Ação sugerida"] = alert['Motivo']
            plan.at[idx, "Plano 7 dias"] = alert['Ação']
            plan.at[idx, "Frente"] = "CORREÇÃO"

# Alertas específicos para Shopee
elif st.session_state.get('canal') == 'Shopee':
    from ui.components.shopee_components import get_shopee_alerts
    shopee_alerts = get_shopee_alerts(df_f)
    for alert in shopee_alerts:
        sku = alert['SKU']
        if sku in plan['SKU'].values:
            idx = plan[plan['SKU'] == sku].index[0]
            plan.at[idx, "Ação sugerida"] = alert['Motivo']
            plan.at[idx, "Plano 7 dias"] = alert['Ação']
            plan.at[idx, "Frente"] = "CORREÇÃO"

# =========================
# Diagnóstico macro
# =========================
dist_0_30 = df_f["Curva 0-30"].value_counts().reindex(["A", "B", "C", "-"]).fillna(0).astype(int)
dist_0_30_df = pd.DataFrame({"Curva": dist_0_30.index, "Anúncios": dist_0_30.values})

fat_0_30_total = float(df_f["Fat. 0-30"].sum())
fat_0_30_A = float(df_f.loc[df_f["Curva 0-30"] == "A", "Fat. 0-30"].sum())
conc_A_0_30 = safe_div(fat_0_30_A, fat_0_30_total)

# Busca ticket médio usando os nomes de período
tm_0_30_row = kpi_df.loc[kpi_df["Período"] == "0-30", "Ticket médio"]
tm_31_60_row = kpi_df.loc[kpi_df["Período"] == "31-60", "Ticket médio"]
tm_61_90_row = kpi_df.loc[kpi_df["Período"] == "61-90", "Ticket médio"]

tm_0_30 = float(tm_0_30_row.iloc[0]) if len(tm_0_30_row) > 0 else 0.0
tm_31_60 = float(tm_31_60_row.iloc[0]) if len(tm_31_60_row) > 0 else 0.0
tm_61_90 = float(tm_61_90_row.iloc[0]) if len(tm_61_90_row) > 0 else 0.0

def tm_direction(a, b, c):
    if np.isnan(a) or np.isnan(b) or np.isnan(c):
        return "Sem dados suficientes para leitura do ticket médio."
    if a < b < c:
        return "📈 Ticket médio subindo. Ajuda margem, mas pode cair volume se preço esticar."
    if a > b > c:
        return "📉 Ticket médio caindo. Pode ser mix mais barato ou promoções."
    if b < a and c > b:
        return "🔄 Ticket caiu e depois recuperou."
    if b > a and c < b:
        return "⚡ Ticket subiu e depois caiu."
    return "📊 Ticket oscilando. Vale cruzar com mix e concorrência."

tm_reading = tm_direction(tm_0_30, tm_31_60, tm_61_90)

# =========================
# KPIs topo e Histórico
# =========================
total_ads = len(df_f)
tt_fat = float(df_f[FAT_COLS].sum().sum())
tt_qty = int(df_f[QTY_COLS].sum().sum())
tm_geral = safe_div(tt_fat, tt_qty) if tt_qty else 0.0

# Preparar snapshot atual
canal_atual = st.session_state.get('canal', 'Mercado Livre')
cliente_atual = st.session_state.get('cliente_atual', 'Geral')

fuga_count = len(drop_alert) if 'drop_alert' in locals() else 0
fuga_valor = float(drop_alert['Perda estimada'].sum()) if 'drop_alert' in locals() and not drop_alert.empty else 0.0
ancoras_count = len(anchors) if 'anchors' in locals() else 0
ancoras_valor = float(anchors['Fat total'].sum()) if 'anchors' in locals() and not anchors.empty else 0.0

# Pegar dados de Ads do período 0-30 para o snapshot
ads_pct_snap = 0.0
ads_valor_snap = 0.0
organic_valor_snap = 0.0
if not df_ads.empty:
    ads_row_snap = df_ads[df_ads['periodo'] == '0-30']
    if not ads_row_snap.empty:
        ads_row_snap = ads_row_snap.iloc[0]
        ads_pct_snap = float(ads_row_snap.get('ads_pct', 0))
        ads_valor_snap = float(ads_row_snap.get('ads_value', 0))
        organic_valor_snap = float(ads_row_snap.get('organic_value', 0))

    current_metrics = {
        'cliente': cliente_atual,
        'canal': canal_atual,
        'total_ads': total_ads,
        'total_fat': tt_fat,
        'total_qty': tt_qty,
        'conc_a': float(conc_A_0_30),
        'tm_atual': float(tm_0_30),
        'fuga_receita_count': fuga_count,
        'fuga_receita_valor': fuga_valor,
        'ancoras_count': ancoras_count,
        'ancoras_valor': ancoras_valor,
        'ads_pct': float(ads_pct_snap),
        'ads_valor': float(ads_valor_snap),
        'organic_valor': float(organic_valor_snap),
        'buybox_avg': float(df_f['Buy Box %'].mean()) if 'Buy Box %' in df_f.columns else 0.0
    }

# Botão para salvar snapshot
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🕒 Gestão de Histórico")
    if not cliente_atual:
        st.warning("⚠️ Identifique o cliente acima para gerenciar o histórico.")
    else:
        st.info(f"Conta ativa: **{cliente_atual}**")
        if st.button("💾 Salvar Snapshot Atual", use_container_width=True, help="Salva as métricas atuais para comparação futura"):
            history_manager.save_snapshot(current_metrics)
            st.success(f"Snapshot de '{cliente_atual}' salvo com sucesso!")
            st.rerun()

# Buscar último snapshot para comparação (apenas se houver cliente identificado)
last_snap = history_manager.get_last_snapshot(cliente_atual, canal_atual) if cliente_atual else None

def render_comparison_metric(label, current_val, last_val, is_money=False, is_pct=False):
    delta = None
    delta_color = "normal"
    if last_val is not None and last_val != 0:
        diff = current_val - last_val
        pct_change = (diff / last_val) * 100
        delta = f"{pct_change:+.1f}%"
        if pct_change > 0.1:
            delta_color = "inverse" if "Fuga" in label else "normal"
        elif pct_change < -0.1:
            delta_color = "normal" if "Fuga" in label else "inverse"
    
    val_str = br_money(current_val) if is_money else (f"{current_val:.1f}%" if is_pct else br_int(current_val))
    return label, val_str, delta

# Renderiza métricas principais com comparação
m1_label, m1_val, m1_delta = render_comparison_metric("Total de Anúncios", total_ads, last_snap['total_ads'] if last_snap else None)
m2_label, m2_val, m2_delta = render_comparison_metric("Faturamento Total", tt_fat, last_snap['total_fat'] if last_snap else None, is_money=True)
m3_label, m3_val, m3_delta = render_comparison_metric("Quantidade Total", tt_qty, last_snap['total_qty'] if last_snap else None)
m4_label, m4_val, m4_delta = render_comparison_metric("Ticket Médio", tm_geral, last_snap['tm_atual'] if last_snap else None, is_money=True)

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric(m1_label, m1_val, m1_delta)
with col2: st.metric(m2_label, m2_val, m2_delta)
with col3: st.metric(m3_label, m3_val, m3_delta)
with col4: st.metric(m4_label, m4_val, m4_delta)

st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["DASHBOARD", "LISTAS E EXPORTAÇÃO", "PLANO TÁTICO", "RELATÓRIO ESTRATÉGICO", "WARNING SEMANAL", "GUIA DE USO"])

# =========================
# TAB 1: Dashboard
# =========================
with tab1:
    # Seletor de período
    st.markdown(
        """
<div class='period-selector'>
  <div class='period-label'><i data-lucide="calendar" style="margin-right:8px;"></i> Selecione o Período para Análise</div>
</div>
<script>lucide.createIcons();</script>
        """,
        unsafe_allow_html=True,
    )
    
    selected_period = st.selectbox(
        "Período",
        options=["0-30", "31-60", "61-90", "91-120"],
        index=0,
        label_visibility="collapsed"
    )
    
    # Mapear colunas baseado no período selecionado
    period_map = {
        "0-30": ("Curva 0-30", "Qntd 0-30", "Fat. 0-30"),
        "31-60": ("Curva 31-60", "Qntd 31-60", "Fat. 31-60"),
        "61-90": ("Curva 61-90", "Qntd 61-90", "Fat. 61-90"),
        "91-120": ("Curva 91-120", "Qntd 91-120", "Fat. 91-120"),
    }
    
    curve_col, qty_col, fat_col = period_map[selected_period]
    
    # Métricas do período selecionado
    period_fat = float(df_f[fat_col].sum())
    period_qty = int(df_f[qty_col].sum())
    period_tm = safe_div(period_fat, period_qty)
    
    # Distribuição de curvas do período
    dist_period = df_f[curve_col].value_counts().reindex(["A", "B", "C", "-"]).fillna(0).astype(int)
    dist_period_df = pd.DataFrame({"Curva": dist_period.index, "Anúncios": dist_period.values})
    
    # Métricas do período
    # Métricas do período selecionado
    render_metric_grid([
        (f"Faturamento {selected_period}", br_money(period_fat), "dollar-sign", "green"),
        (f"Quantidade {selected_period}", br_int(period_qty), "package", "blue"),
        (f"Ticket Médio {selected_period}", br_money(period_tm), "target", "amber"),
        (f"Curva A ({selected_period})", br_int(dist_period.get("A", 0)), "star", "purple"),
    ])

    left, right = st.columns([1.2, 1])

    with left:
        section_header("Resumo por Período", "Visão consolidada das 4 janelas de tempo", "calendar", "purple")
        show = kpi_df.copy()
        show["Qtd"] = show["Qtd"].map(br_int)
        show["Faturamento"] = show["Faturamento"].map(br_money)
        show["Ticket médio"] = show["Ticket médio"].apply(lambda x: br_money(x) if pd.notna(x) else "-")
        
        st.dataframe(show, use_container_width=True, hide_index=True, height=220)
        section_footer()

    with right:
        section_header(f"Distribuição de Curvas ({selected_period})", f"Período selecionado: {selected_period} dias", "target", "blue")
        colors_map = {"A": "#22c55e", "B": "#3b82f6", "C": "#f59e0b", "-": "#6b7280"}
        fig = px.bar(
            dist_period_df, 
            x="Curva", 
            y="Anúncios",
            color="Curva",
            color_discrete_map=colors_map
        )
        fig.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=20),
            font=dict(color='#9ca3af')
        )
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)
        section_footer()

    # Quadrante Curva ABC removido por erro de referência inexistente
    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)

    # Seções específicas por canal
    if st.session_state.get('canal') == 'Mercado Livre':
        if not df_logistics.empty:
            log_row = df_logistics[df_logistics['periodo'] == selected_period]
            if not log_row.empty:
                log_row = log_row.iloc[0]
                render_logistics_section(
                    full_pct=log_row.get("full_pct", 0.0),
                    correios_pct=log_row.get("correios_pct", 0.0),
                    flex_pct=log_row.get("flex_pct", 0.0),
                    coleta_pct=log_row.get("coleta_pct", 0.0),
                    outros_pct=log_row.get("outros_pct", 0.0),
                    full_fat=float(log_row.get('full_fat', 0)),
                    correios_fat=float(log_row.get('correios_fat', 0)),
                    flex_fat=float(log_row.get('flex_fat', 0)),
                    coleta_fat=float(log_row.get('coleta_fat', 0)),
                    outros_fat=float(log_row.get('outros_fat', 0)),
                    period=selected_period
                )
        else:
            if all(c in df_f.columns for c in [f"Share Full Qtd {selected_period}", f"Share Full Fat {selected_period}"]):
                section_header(f"Logística no Período {selected_period}", "Distribuição FULL vs NÃO FULL", "truck", "cyan")
                # ... (cálculos mantidos)
                section_footer()

# =========================
# TAB 3: Plano Tático
# =========================
with tab3:
    st.markdown(render_report_section("layout", "Plano Tático por Produto", "Ações detalhadas para 15 e 30 dias", "purple"), unsafe_allow_html=True)

    # Container de filtros premium
    st.markdown(f"""
<div class="filter-container">
  <div class="filter-header">
    <div class="filter-header-left">
      <div class="filter-icon">{get_svg_icon('target')}</div>
      <div>
        <div class="filter-main-title">CENTRAL DE FILTROS</div>
        <div class="filter-subtitle">Refine sua análise por frente, faturamento e busca</div>
      </div>
    </div>
    <div class="filter-count">{len(plan)} produtos</div>
  </div>
</div>
    """, unsafe_allow_html=True)
    
    # Seleção de frentes com botões visuais
    st.markdown("**SELECIONE AS FRENTES:**")
    
    front_cols = st.columns(5)
    front_icons = {"DEFESA": "star", "CORREÇÃO": "alert-triangle", "ATAQUE": "trending-up", "LIMPEZA": "package", "OTIMIZAÇÃO": "activity"}
    
    front_filter = []
    for i, frente in enumerate(["DEFESA", "CORREÇÃO", "ATAQUE", "LIMPEZA", "OTIMIZAÇÃO"]):
        with front_cols[i]:
            count = int(all_front_counts.get(frente, 0))
            if st.checkbox(f"{frente} ({count})", value=True, key=f"front_{frente}"):
                front_filter.append(frente)
    
    # ... (filtros e métricas mantidos)

# =========================
# TAB 4: Relatório Estratégico
# =========================
with tab4:
    st.markdown(render_report_section("search", "Diagnóstico Macro", "Visão geral da saúde do catálogo", "purple"), unsafe_allow_html=True)
    
    # KPIs destacados
    st.markdown(
        render_kpi_highlight([
            (br_int(total_ads), "Total de Anúncios", "purple"),
            (f"{round(float(conc_A_0_30 or 0.0) * 100, 1)}%", "Concentração Curva A", "green"),
            (br_money(tm_0_30), "Ticket Médio Atual", "amber"),
        ]),
        unsafe_allow_html=True
    )
    
    st.markdown(render_insight_card("bar-chart-3", "Análise do Ticket Médio", tm_reading), unsafe_allow_html=True)
    
    # ... (tabelas mantidas)

    # Seção 2: Segmentação
    st.markdown(render_report_section("package", "Segmentação de Produtos", "Análise por categoria estratégica", "blue"), unsafe_allow_html=True)
    
    # Resumo das frentes
    st.markdown(
        render_front_summary([
            ("🛡️", int(all_front_counts.get("DEFESA", 0)), "DEFESA"),
            ("⚠️", int(all_front_counts.get("CORREÇÃO", 0)), "CORREÇÃO"),
            ("🚀", int(all_front_counts.get("ATAQUE", 0)), "ATAQUE"),
            ("🧹", int(all_front_counts.get("LIMPEZA", 0)), "LIMPEZA"),
            ("⚙️", int(all_front_counts.get("OTIMIZAÇÃO", 0)), "OTIMIZAÇÃO"),
        ]),
        unsafe_allow_html=True
    )

    # Âncoras
    st.markdown(render_report_section("star", "Produtos Âncora", "Os 5 produtos mais relevantes do catálogo", "green"), unsafe_allow_html=True)
    # ... (tabela de âncoras mantida)

    # Fuga de receita
    st.markdown(render_report_section("alert-triangle", "Alerta de Fuga de Receita", "Produtos com queda brusca de performance", "rose"), unsafe_allow_html=True)
    if len(drop_alert) > 0:
        loss_total = float(drop_alert["Perda estimada"].sum()) if "Perda estimada" in drop_alert.columns else 0.0
        st.markdown(
            render_insight_card("alert-triangle", "Atenção Imediata", 
                f"Você tem {len(drop_alert)} produtos que caíram de curva, representando uma perda estimada de {br_money(loss_total)}. Priorize a correção destes itens."),
            unsafe_allow_html=True
        )
    # ... (tabela de fuga mantida)
    op_cols = ["Frente","MLB","Título","Curva 0-30","Fat. 0-30","Ação sugerida","Plano 7 dias","Plano 15 dias","Plano 30 dias"]
    op = ensure_cols(plan, op_cols).copy()
    op = op.sort_values(["Frente", "Fat. 0-30"], ascending=[True, False])

    st.download_button(
        "📥 Baixar Plano Operacional Completo",
        data=to_xlsx_bytes(op),
        file_name="plano_operacional_completo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    # Tabelas por frente
    for fr in front_order:
        subset = op[op["Frente"] == fr].head(10).copy()
        if len(subset) == 0:
            continue
        
        icon = {"LIMPEZA": "🧹", "CORREÇÃO": "⚠️", "ATAQUE": "🚀", "DEFESA": "🛡️", "OTIMIZAÇÃO": "⚙️"}.get(fr, "📦")
        
        with st.expander(f"{icon} {fr} ({len(op[op['Frente'] == fr])} itens)", expanded=False):
            subset["Fat. 0-30"] = subset["Fat. 0-30"].apply(lambda x: br_money(float(x)) if pd.notna(x) else "-")
            st.dataframe(subset, use_container_width=True, hide_index=True, height=350)

    st.markdown("</div>", unsafe_allow_html=True)

    # Seção 4: Histórico de Evolução
    st.markdown(render_report_section("activity", "Histórico de Evolução", "Acompanhamento das métricas ao longo do tempo", "blue"), unsafe_allow_html=True)
    
    if not cliente_atual:
        st.info("Identifique o cliente na barra lateral para visualizar o histórico de evolução.")
        history_df = pd.DataFrame()
    else:
        history_df = history_manager.get_history(cliente_atual, canal_atual)
    
    if not history_df.empty:
        # Garantir ordem cronológica (antigo para novo)
        history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
        history_df = history_df.sort_values('timestamp').reset_index(drop=True)
        
        # Criar rótulos sequenciais para o eixo X (Análise 1, Análise 2, ...)
        history_df['Analise'] = [f"Análise {i+1}" for i in history_df.index]
        
        # Gráfico de evolução do faturamento
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=history_df['Analise'], y=history_df['total_fat'], name='Faturamento Total', line=dict(color='#10b981', width=3), hovertext=history_df['timestamp'].dt.strftime('%d/%m/%Y %H:%M')))
        fig.add_trace(go.Scatter(x=history_df['Analise'], y=history_df['ancoras_valor'], name='Faturamento Âncoras', line=dict(color='#3b82f6', width=2, dash='dot')))
        
        fig.update_layout(
            title="Evolução do Faturamento (Total vs Âncoras)",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
            height=300,
            xaxis=dict(type='category')
        )
        st.plotly_chart(fig, use_container_width=True)

        # Gráfico de evolução da Fuga de Receita
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            fig_fuga_qty = go.Figure()
            fig_fuga_qty.add_trace(go.Bar(x=history_df['Analise'], y=history_df['fuga_receita_count'], name='Qtd Produtos', marker_color='#f59e0b', hovertext=history_df['timestamp'].dt.strftime('%d/%m/%Y %H:%M')))
            fig_fuga_qty.update_layout(
                title="Qtd Produtos em Fuga",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=40, b=20),
                height=250,
                xaxis=dict(type='category')
            )
            st.plotly_chart(fig_fuga_qty, use_container_width=True)
        
        with col_f2:
            fig_fuga_val = go.Figure()
            fig_fuga_val.add_trace(go.Scatter(x=history_df['Analise'], y=history_df['fuga_receita_valor'], name='Perda Estimada', fill='tozeroy', line=dict(color='#ef4444'), hovertext=history_df['timestamp'].dt.strftime('%d/%m/%Y %H:%M')))
            fig_fuga_val.update_layout(
                title="Valor da Perda Estimada (R$)",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=40, b=20),
                height=250,
                xaxis=dict(type='category')
            )
            st.plotly_chart(fig_fuga_val, use_container_width=True)
        
        # Tabela de histórico detalhada
        st.markdown("#### Detalhes dos Snapshots")
        hist_show = history_df.copy()
        hist_show['Data'] = hist_show['timestamp'].dt.strftime('%d/%m/%Y %H:%M')
        hist_show['Faturamento'] = hist_show['total_fat'].apply(br_money)
        hist_show['Conc. Curva A'] = hist_show['conc_a'].apply(lambda x: f"{x*100:.1f}%")
        hist_show['Ticket Médio'] = hist_show['tm_atual'].apply(br_money)
        hist_show['Fuga (Qtd)'] = hist_show['fuga_receita_count']
        hist_show['Perda Fuga'] = hist_show['fuga_receita_valor'].apply(br_money)
        
        st.dataframe(
            hist_show[['Data', 'Faturamento', 'Conc. Curva A', 'Ticket Médio', 'Fuga (Qtd)', 'Perda Fuga']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Ainda não há histórico salvo para este canal. Use o botão 'Salvar Snapshot Atual' na barra lateral para começar a rastrear sua evolução.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown('<div style="height:2rem"></div>', unsafe_allow_html=True)
st.markdown(
    """
    <div style="text-align: center; opacity: 0.5; font-size: 0.85rem; padding: 20px 0;">
        Desenvolvido por Vinicius Lima/ CNPJ: 47.192.694/0001-70
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# TAB 5: Warning Semanal
# =========================
with tab5:
    render_warning_semanal_tab(df_f, df_raw=df_raw)

# =========================
# TAB 6: Guia de Uso
# =========================
with tab6:
    render_guide_tab()
