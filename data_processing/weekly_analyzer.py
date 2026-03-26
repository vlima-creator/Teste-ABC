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
        # Suporta: 'Data', 'Data da venda', 'Date', 'Order Date', 'Data do pedido'
        date_col = next((c for c in df.columns if c.lower() in ['data', 'data da venda', 'date', 'order date', 'data do pedido']), None)
        
        if date_col:
            # Para formatos como '26/01/2026-24/02/2026' (Shopee Overview), pegamos a data final ou ignoramos se for range
            # Mas o ideal é que o df_raw contenha transações individuais ou diárias
            df['data_processada'] = pd.to_datetime(df[date_col], errors='coerce')
        else:
            # Se não houver coluna de data, não podemos fazer análise semanal
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
        Calcula curvas ABC semanais com suporte a múltiplas plataformas (ML, Amazon, Shopee).
        """
        df = WeeklyAnalyzer.add_weekly_analysis(df_raw, base_date)
        
        if df.empty:
            # Se não houver dados temporais, tentamos processar como dados agregados se as colunas existirem
            if 'Qtd Total' in df_raw.columns or 'Fat Total' in df_raw.columns:
                return df_raw
            return pd.DataFrame()
            
        # Identificar colunas de ID dinamicamente
        # ML: 'MLB', 'SKU'
        # Amazon: 'ASIN (child)', 'ASIN (parent)', 'SKU'
        # Shopee: 'ID do Item', 'SKU da Variação', 'SKU Principle'
        id_priority = ['MLB', 'ASIN (child)', 'SKU da Variação', 'SKU Principle', 'ID do Item', 'SKU', 'ASIN', 'ID']
        id_col = next((c for c in id_priority if c in df.columns), df.columns[0])
        
        # Identificar colunas de Título
        title_priority = ['Título', 'Produto', 'Product Name', 'Nome do Produto', 'Item Name', 'titulo']
        title_col = next((c for c in title_priority if c in df.columns), df.columns[1])
        
        # Identificar colunas de Quantidade
        qty_priority = ['Unidades pedidas', 'Unidades (Pedido pago)', 'Unidades', 'Quantidade', 'Quantity', 'Qty', 'unidades vendidas', 'Produto Pago']
        qty_col = next((c for c in qty_priority if c in df.columns), None)
        
        # Identificar colunas de Faturamento
        rev_priority = ['Vendas de produtos pedidos', 'Vendas (Pedido pago) (BRL)', 'Receita', 'Faturamento', 'Revenue', 'Total (BRL)', 'Valor Total']
        rev_col = next((c for c in rev_priority if c in df.columns), None)

        # Fallback se não encontrar colunas de valores
        if not qty_col: qty_col = df.columns[2] if len(df.columns) > 2 else None
        if not rev_col: rev_col = df.columns[3] if len(df.columns) > 3 else None

        if not qty_col or not rev_col:
            return pd.DataFrame()

        # Normalizar nomes para o agrupamento
        df_grouped = df.rename(columns={id_col: 'temp_id', title_col: 'temp_title', qty_col: 'temp_qty', rev_col: 'temp_rev'})

        # Garantir que os valores são numéricos
        df_grouped['temp_qty'] = pd.to_numeric(df_grouped['temp_qty'], errors='coerce').fillna(0)
        df_grouped['temp_rev'] = pd.to_numeric(df_grouped['temp_rev'], errors='coerce').fillna(0)

        # Agregar por ID, Título e Semana
        agg = df_grouped.groupby(['temp_id', 'temp_title', 'semana']).agg({
            'temp_qty': 'sum',
            'temp_rev': 'sum'
        }).reset_index()
        
        # Pivot para ter colunas por semana
        piv_qty = agg.pivot_table(index=['temp_id', 'temp_title'], columns='semana', values='temp_qty', fill_value=0).reset_index()
        piv_rev = agg.pivot_table(index=['temp_id', 'temp_title'], columns='semana', values='temp_rev', fill_value=0.0).reset_index()
        
        # Garantir todas as 5 semanas
        for sem in ['Sem1', 'Sem2', 'Sem3', 'Sem4', 'Sem5']:
            if sem not in piv_qty.columns: piv_qty[sem] = 0
            if sem not in piv_rev.columns: piv_rev[sem] = 0.0
        
        piv_qty = piv_qty.rename(columns={sem: f'Qntd {sem}' for sem in ['Sem1', 'Sem2', 'Sem3', 'Sem4', 'Sem5']})
        piv_rev = piv_rev.rename(columns={sem: f'Fat. {sem}' for sem in ['Sem1', 'Sem2', 'Sem3', 'Sem4', 'Sem5']})
        
        export = piv_qty.merge(piv_rev, on=['temp_id', 'temp_title'], how='outer')
        export = export.rename(columns={'temp_id': id_col, 'temp_title': title_col})
        
        # Calcular curvas ABC semanais
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
    def calculate_abc_curve(df: pd.DataFrame, revenue_col: str, id_col: str, title_col: str) -> pd.DataFrame:
        """Calcula curva ABC baseada em faturamento."""
        result = df.copy()
        if revenue_col not in result.columns:
            result['curva_abc'] = '-'
            return result
            
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
        
        # Merge de volta garantindo as chaves corretas
        result = result.merge(sorted_df[[id_col, title_col, 'curva_abc']], on=[id_col, title_col], how='left')
        result['curva_abc'] = result['curva_abc'].fillna('-')
        result.loc[result[revenue_col] == 0, 'curva_abc'] = '-'
        
        return result
    
    @staticmethod
    def calculate_warnings(df: pd.DataFrame) -> pd.DataFrame:
        """Calcula alertas de mudança de curva."""
        result = df.copy()
        result['Curva Anterior'] = result.get('Curva Sem2', '-')
        result['Curva Atual'] = result.get('Curva Sem1', '-')
        
        fat_sem1 = result.get('Fat. Sem1', 0)
        fat_sem2 = result.get('Fat. Sem2', 0)
        
        result['Delta Fat'] = fat_sem1 - fat_sem2
        result['Delta %'] = result.apply(
            lambda r: ((r.get('Fat. Sem1', 0) - r.get('Fat. Sem2', 0)) / r.get('Fat. Sem2', 1) * 100) 
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
