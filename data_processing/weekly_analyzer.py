"""
Módulo de análise semanal para Warning Semanal.
Calcula buckets semanais, classificação ABC semanal e alertas de mudança de curva.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, Dict, List


class WeeklyAnalyzer:
    """Analisa dados de vendas em buckets semanais com sistema de alertas."""
    
    @staticmethod
    def add_weekly_analysis(df_raw: pd.DataFrame, base_date: datetime = None) -> pd.DataFrame:
        """
        Adiciona análise semanal ao DataFrame bruto de vendas.
        """
        if df_raw.empty:
            return df_raw
        
        df = df_raw.copy()
        
        # Identificar coluna de data dinamicamente
        date_col = next((c for c in df.columns if c.lower() in ['data', 'data da venda', 'date', 'order date']), None)
        
        if date_col:
            df['data_processada'] = pd.to_datetime(df[date_col], errors='coerce')
        else:
            return df
        
        # Remover linhas sem data
        df = df.dropna(subset=['data_processada'])
        
        if df.empty:
            return df
        
        # Data de referência
        if base_date is None:
            base_date = df['data_processada'].max()
        
        df['dias'] = (base_date - df['data_processada']).dt.days
        
        def weekly_bucket(dias):
            if dias < 0: return None
            if dias <= 7: return 'Sem1'
            elif dias <= 14: return 'Sem2'
            elif dias <= 21: return 'Sem3'
            elif dias <= 28: return 'Sem4'
            elif dias <= 35: return 'Sem5'
            else: return None
        
        df['semana'] = df['dias'].apply(weekly_bucket)
        df = df.dropna(subset=['semana'])
        
        return df
    
    @staticmethod
    def calculate_weekly_curves(df_raw: pd.DataFrame, base_date: datetime = None) -> pd.DataFrame:
        """
        Calcula curvas ABC semanais com suporte a múltiplas plataformas.
        """
        df = WeeklyAnalyzer.add_weekly_analysis(df_raw, base_date)
        
        if df.empty:
            return pd.DataFrame()
            
        # Identificar colunas dinamicamente
        id_col = next((c for c in df.columns if c.upper() in ['MLB', 'SKU', 'ASIN', 'ID']), df.columns[0])
        title_col = next((c for c in df.columns if c.lower() in ['título', 'titulo', 'product name', 'nome do produto', 'item name']), df.columns[1])
        qty_col = next((c for c in df.columns if c.lower() in ['unidades', 'quantidade', 'quantity', 'qty', 'unidades vendidas']), None)
        rev_col = next((c for c in df.columns if c.lower() in ['receita', 'faturamento', 'revenue', 'total (brl)', 'valor total']), None)

        # Fallback se não encontrar colunas de valores
        if not qty_col: qty_col = df.columns[2]
        if not rev_col: rev_col = df.columns[3]

        # Normalizar nomes para o agrupamento
        df = df.rename(columns={id_col: 'temp_id', title_col: 'temp_title', qty_col: 'temp_qty', rev_col: 'temp_rev'})

        # Agregar
        agg = df.groupby(['temp_id', 'temp_title', 'semana']).agg({
            'temp_qty': 'sum',
            'temp_rev': 'sum'
        }).reset_index()
        
        # Pivot
        piv_qty = agg.pivot_table(index=['temp_id', 'temp_title'], columns='semana', values='temp_qty', fill_value=0).reset_index()
        piv_rev = agg.pivot_table(index=['temp_id', 'temp_title'], columns='semana', values='temp_rev', fill_value=0.0).reset_index()
        
        for sem in ['Sem1', 'Sem2', 'Sem3', 'Sem4', 'Sem5']:
            if sem not in piv_qty.columns: piv_qty[sem] = 0
            if sem not in piv_rev.columns: piv_rev[sem] = 0.0
        
        piv_qty = piv_qty.rename(columns={sem: f'Qntd {sem}' for sem in ['Sem1', 'Sem2', 'Sem3', 'Sem4', 'Sem5']})
        piv_rev = piv_rev.rename(columns={sem: f'Fat. {sem}' for sem in ['Sem1', 'Sem2', 'Sem3', 'Sem4', 'Sem5']})
        
        export = piv_qty.merge(piv_rev, on=['temp_id', 'temp_title'], how='outer')
        export = export.rename(columns={'temp_id': id_col, 'temp_title': title_col})
        
        # Calcular curvas
        for sem in ['Sem1', 'Sem2', 'Sem3', 'Sem4', 'Sem5']:
            fat_col = f'Fat. {sem}'
            curva_col = f'Curva {sem}'
            export = WeeklyAnalyzer.calculate_abc_curve(export, fat_col, id_col, title_col)
            export = export.rename(columns={'curva_abc': curva_col})
        
        # Totais
        export['Qtd Total'] = export[[f'Qntd Sem{i}' for i in range(1, 6)]].sum(axis=1)
        export['Fat Total'] = export[[f'Fat. Sem{i}' for i in range(1, 6)]].sum(axis=1)
        export['TM Total'] = export.apply(lambda r: r['Fat Total'] / r['Qtd Total'] if r['Qtd Total'] > 0 else 0.0, axis=1).fillna(0.0)
        
        return export
    
    @staticmethod
    def calculate_abc_curve(df: pd.DataFrame, revenue_col: str, id_col: str = 'MLB', title_col: str = 'Título') -> pd.DataFrame:
        result = df.copy()
        sorted_df = result.sort_values(revenue_col, ascending=False)
        total_revenue = sorted_df[revenue_col].sum()
        
        if total_revenue > 0:
            sorted_df['_pct_acum'] = (sorted_df[revenue_col].cumsum() / total_revenue) * 100
        else:
            sorted_df['_pct_acum'] = 0
        
        def classify_curve(pct):
            if pct <= 80: return 'A'
            elif pct <= 95: return 'B'
            else: return 'C'
        
        sorted_df['curva_abc'] = sorted_df['_pct_acum'].apply(classify_curve)
        result = result.merge(sorted_df[[id_col, title_col, 'curva_abc']], on=[id_col, title_col], how='left')
        result['curva_abc'] = result['curva_abc'].fillna('-')
        result.loc[result[revenue_col] == 0, 'curva_abc'] = '-'
        
        return result
    
    @staticmethod
    def calculate_warnings(df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        result['Curva Anterior'] = result.get('Curva Sem2', '-')
        result['Curva Atual'] = result.get('Curva Sem1', '-')
        
        fat_sem1 = result.get('Fat. Sem1', 0)
        fat_sem2 = result.get('Fat. Sem2', 0)
        
        result['Delta Fat'] = fat_sem1 - fat_sem2
        result['Delta %'] = result.apply(
            lambda r: ((r['Fat. Sem1'] - r['Fat. Sem2']) / r['Fat. Sem2'] * 100) 
                     if r.get('Fat. Sem2', 0) > 0 else 0,
            axis=1
        ).fillna(0)
        
        def classify_warning(row):
            curva_atual = row.get('Curva Atual', '-')
            curva_anterior = row.get('Curva Anterior', '-')
            delta_pct = row.get('Delta %', 0)
            
            if (curva_anterior == 'A' and curva_atual in ['B', 'C', '-']) or \
               (curva_anterior == 'B' and curva_atual in ['C', '-']):
                return '🔴 Queda Crítica'
            elif (curva_anterior in ['B', 'C', '-'] and curva_atual == 'A') or \
                 (curva_anterior in ['C', '-'] and curva_atual == 'B'):
                return '🟢 Recuperação'
            elif delta_pct < -30 and curva_atual == curva_anterior:
                return '🟡 Atenção'
            else:
                return '🟢 Estável'
        
        result['Status Warning'] = result.apply(classify_warning, axis=1)
        return result

    @staticmethod
    def get_warning_summary(df: pd.DataFrame) -> Dict[str, int]:
        if 'Status Warning' not in df.columns: return {}
        return df['Status Warning'].value_counts().to_dict()
