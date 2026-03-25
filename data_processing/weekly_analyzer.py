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
        
        Args:
            df_raw: DataFrame com colunas ['data', 'unidades', 'receita', 'mlb', 'titulo']
            base_date: Data de referência (padrão: data máxima do dataset)
            
        Returns:
            DataFrame com colunas de buckets semanais adicionadas
        """
        if df_raw.empty:
            return df_raw
        
        df = df_raw.copy()
        
        # Garantir que 'data' é datetime
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'], errors='coerce')
        else:
            return df
        
        # Remover linhas sem data
        df = df.dropna(subset=['data'])
        
        if df.empty:
            return df
        
        # Data de referência é a mais recente do dataset
        if base_date is None:
            base_date = df['data'].max()
        
        # Calcular dias desde a data de referência
        df['dias'] = (base_date - df['data']).dt.days
        
        # Definir buckets semanais
        def weekly_bucket(dias):
            """Classifica em buckets semanais: Sem1 (0-7), Sem2 (8-14), Sem3 (15-21), Sem4 (22-28), Sem5 (29-35)"""
            if dias < 0:
                return None
            if dias <= 7:
                return 'Sem1'
            elif dias <= 14:
                return 'Sem2'
            elif dias <= 21:
                return 'Sem3'
            elif dias <= 28:
                return 'Sem4'
            elif dias <= 35:
                return 'Sem5'
            else:
                return None
        
        df['semana'] = df['dias'].apply(weekly_bucket)
        df = df.dropna(subset=['semana'])
        
        return df
    
    @staticmethod
    def calculate_weekly_curves(df_raw: pd.DataFrame, base_date: datetime = None) -> pd.DataFrame:
        """
        Calcula curvas ABC semanais a partir do DataFrame bruto.
        
        Args:
            df_raw: DataFrame com colunas ['data', 'unidades', 'receita', 'mlb', 'titulo']
            base_date: Data de referência
            
        Returns:
            DataFrame com colunas de buckets semanais e curvas ABC
        """
        # Adicionar análise semanal
        df = WeeklyAnalyzer.add_weekly_analysis(df_raw, base_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # Agregar por MLB, título e semana
        agg = df.groupby(['mlb', 'titulo', 'semana']).agg({
            'unidades': 'sum',
            'receita': 'sum'
        }).reset_index()
        
        # Pivot para ter colunas por semana
        piv_qty = agg.pivot_table(
            index=['mlb', 'titulo'],
            columns='semana',
            values='unidades',
            fill_value=0
        ).reset_index()
        
        piv_rev = agg.pivot_table(
            index=['mlb', 'titulo'],
            columns='semana',
            values='receita',
            fill_value=0.0
        ).reset_index()
        
        # Garantir que todas as semanas existem
        for sem in ['Sem1', 'Sem2', 'Sem3', 'Sem4', 'Sem5']:
            if sem not in piv_qty.columns:
                piv_qty[sem] = 0
            if sem not in piv_rev.columns:
                piv_rev[sem] = 0.0
        
        # Renomear colunas
        piv_qty = piv_qty.rename(columns={sem: f'Qntd {sem}' for sem in ['Sem1', 'Sem2', 'Sem3', 'Sem4', 'Sem5']})
        piv_rev = piv_rev.rename(columns={sem: f'Fat. {sem}' for sem in ['Sem1', 'Sem2', 'Sem3', 'Sem4', 'Sem5']})
        
        # Merge
        export = piv_qty.merge(piv_rev, on=['mlb', 'titulo'], how='outer')
        export = export.rename(columns={'mlb': 'MLB', 'titulo': 'Título'})
        
        # Calcular curva ABC para cada semana
        for sem in ['Sem1', 'Sem2', 'Sem3', 'Sem4', 'Sem5']:
            fat_col = f'Fat. {sem}'
            curva_col = f'Curva {sem}'
            export = WeeklyAnalyzer.calculate_abc_curve(export, fat_col)
            export = export.rename(columns={'curva_abc': curva_col})
        
        # Totais
        export['Qtd Total'] = export[[f'Qntd Sem{i}' for i in range(1, 6)]].sum(axis=1)
        export['Fat Total'] = export[[f'Fat. Sem{i}' for i in range(1, 6)]].sum(axis=1)
        export['TM Total'] = export.apply(
            lambda r: r['Fat Total'] / r['Qtd Total'] if r['Qtd Total'] > 0 else 0.0,
            axis=1
        ).fillna(0.0)
        
        return export
    
    @staticmethod
    def calculate_abc_curve(df: pd.DataFrame, revenue_col: str) -> pd.DataFrame:
        """
        Calcula curva ABC baseada em faturamento.
        
        Args:
            df: DataFrame com dados
            revenue_col: Coluna de faturamento
            
        Returns:
            DataFrame com coluna 'curva_abc'
        """
        result = df.copy()
        
        # Ordenar por faturamento decrescente
        sorted_df = result.sort_values(revenue_col, ascending=False)
        
        # Calcular percentual acumulado
        total_revenue = sorted_df[revenue_col].sum()
        
        if total_revenue > 0:
            sorted_df['_pct_acum'] = (sorted_df[revenue_col].cumsum() / total_revenue) * 100
        else:
            sorted_df['_pct_acum'] = 0
        
        # Classificar em curvas
        def classify_curve(pct):
            if pct <= 80:
                return 'A'
            elif pct <= 95:
                return 'B'
            else:
                return 'C'
        
        sorted_df['curva_abc'] = sorted_df['_pct_acum'].apply(classify_curve)
        
        # Merge de volta ao DataFrame original
        result = result.merge(sorted_df[['MLB', 'Título', 'curva_abc']], 
                             on=['MLB', 'Título'], how='left')
        
        # Produtos sem vendas ficam como "-"
        result['curva_abc'] = result['curva_abc'].fillna('-')
        result.loc[result[revenue_col] == 0, 'curva_abc'] = '-'
        
        return result
    
    @staticmethod
    def calculate_warnings(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula alertas de mudança de curva entre semanas consecutivas.
        
        Args:
            df: DataFrame com colunas de curva semanal
            
        Returns:
            DataFrame com colunas de alertas
        """
        result = df.copy()
        
        # Comparar Sem1 (atual) com Sem2 (semana anterior)
        result['Curva Anterior'] = result.get('Curva Sem2', '-')
        result['Curva Atual'] = result.get('Curva Sem1', '-')
        
        # Calcular delta de faturamento
        fat_sem1 = result.get('Fat. Sem1', 0)
        fat_sem2 = result.get('Fat. Sem2', 0)
        
        result['Delta Fat'] = fat_sem1 - fat_sem2
        result['Delta %'] = result.apply(
            lambda r: ((r['Fat. Sem1'] - r['Fat. Sem2']) / r['Fat. Sem2'] * 100) 
                     if r['Fat. Sem2'] > 0 else 0,
            axis=1
        ).fillna(0)
        
        # Classificar alertas
        def classify_warning(row):
            curva_atual = row.get('Curva Atual', '-')
            curva_anterior = row.get('Curva Anterior', '-')
            delta_pct = row.get('Delta %', 0)
            
            # Queda crítica: de A para B/C ou de B para C
            if (curva_anterior == 'A' and curva_atual in ['B', 'C', '-']) or \
               (curva_anterior == 'B' and curva_atual in ['C', '-']):
                return '🔴 Queda Crítica'
            
            # Recuperação: sobe de curva
            elif (curva_anterior in ['B', 'C', '-'] and curva_atual == 'A') or \
                 (curva_anterior in ['C', '-'] and curva_atual == 'B'):
                return '🟢 Recuperação'
            
            # Atenção: queda de faturamento > 30% mesmo mantendo curva
            elif delta_pct < -30 and curva_atual == curva_anterior:
                return '🟡 Atenção'
            
            # Estável
            else:
                return '🟢 Estável'
        
        result['Status Warning'] = result.apply(classify_warning, axis=1)
        
        return result
    
    @staticmethod
    def get_warning_summary(df: pd.DataFrame) -> Dict[str, int]:
        """
        Retorna resumo de alertas.
        
        Args:
            df: DataFrame com coluna 'Status Warning'
            
        Returns:
            Dicionário com contagem de alertas por tipo
        """
        if 'Status Warning' not in df.columns:
            return {}
        
        return df['Status Warning'].value_counts().to_dict()
