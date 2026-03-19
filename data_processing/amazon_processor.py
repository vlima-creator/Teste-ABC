"""
Processador de dados da Amazon.
Transforma relatórios da Amazon no formato padronizado de curva ABC.
"""
import pandas as pd
import numpy as np
import io
import re
from typing import Tuple, Optional
from .base_processor import BaseProcessor


class AmazonProcessor(BaseProcessor):
    """Processador para relatórios da Amazon."""
    
    def __init__(self):
        super().__init__()
        self.canal_name = "Amazon"
    
    def detect(self, file) -> bool:
        """
        Detecta se o arquivo é um relatório da Amazon.
        """
        try:
            file.seek(0)
            filename = getattr(file, 'name', '').lower()
            content = file.read(4096).decode('utf-8', errors='ignore')
            file.seek(0)
            
            amazon_indicators = [
                '(parent) ASIN', '(child) ASIN', 'sku', 'product-name',
                'sessions', 'order-item-session-percentage', 'units-ordered',
                'ordered-product-sales', 'total-order-items', 'Nome do produto',
                'ASIN pai', 'ASIN filho', 'Sessões', 'Unidades pedidas',
                'Vendas de produtos pedidos', 'vendas-pedidas', 'unidades-pedidas',
                'asin', 'seller-sku', 'product-title'
            ]
            
            content_lower = content.lower()
            matches = sum(1 for ind in amazon_indicators if ind.lower() in content_lower)
            
            if matches >= 2 or "businessreport" in filename or "salesdashboard" in filename:
                return True
                
            return False
        except Exception:
            return False
    
    def process(self, files: list) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        Processa relatórios da Amazon com busca profunda de colunas.
        """
        if not files:
            raise ValueError("Nenhum arquivo fornecido")
            
        file = files[0]
        file.seek(0)
        
        df = None
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'utf-16']
        separators = [',', '\t', ';']
        
        for enc in encodings:
            for sep in separators:
                try:
                    file.seek(0)
                    df_tmp = pd.read_csv(file, sep=sep, encoding=enc, nrows=100)
                    if len(df_tmp.columns) > 1:
                        file.seek(0)
                        df = pd.read_csv(file, sep=sep, encoding=enc)
                        break
                except:
                    continue
            if df is not None:
                break
                
        if df is None:
            raise ValueError("Não foi possível ler o arquivo da Amazon. Verifique o formato CSV/TXT.")

        df.columns = [str(c).strip() for c in df.columns]
        
        # Funções auxiliares de limpeza
        def clean_money(v):
            if pd.isna(v): return 0.0
            v = str(v).replace('R$', '').replace('$', '').replace('\xa0', '').strip()
            if '.' in v and ',' in v:
                v = v.replace('.', '').replace(',', '.')
            elif ',' in v:
                # Se houver apenas uma vírgula e ela parecer um separador decimal
                if len(v.split(',')) == 2:
                    v = v.replace(',', '.')
            try:
                cleaned = re.sub(r'[^0-9.]', '', v)
                return float(cleaned) if cleaned else 0.0
            except:
                return 0.0

        def clean_int(v):
            if pd.isna(v): return 0
            try:
                cleaned = re.sub(r'[^0-9]', '', str(v))
                return int(cleaned) if cleaned else 0
            except:
                return 0

        # Mapeamento flexível com busca profunda
        df_export = pd.DataFrame()
        
        # 1. Busca por MLB (ASIN Pai)
        mlb_col = next((c for c in df.columns if any(p in c.lower() for p in ['(parent) asin', 'asin pai', 'parent-asin', 'asin'])), None)
        df_export['MLB'] = df[mlb_col].astype(str) if mlb_col else "N/A"
        
        # 2. Busca por SKU
        sku_col = next((c for c in df.columns if any(p in c.lower() for p in ['sku', 'seller-sku', '(child) asin', 'asin filho'])), None)
        df_export['SKU'] = df[sku_col].astype(str) if sku_col else df_export['MLB']
        
        # 3. Busca por Título
        title_col = next((c for c in df.columns if any(p in c.lower() for p in ['product-name', 'nome do produto', 'title', 'título', 'titulo', 'nome-do-produto'])), None)
        df_export['Título'] = df[title_col].astype(str) if title_col else "Produto sem título"
        
        # 4. Busca por Quantidade (Busca profunda)
        qty_potentials = ['units-ordered', 'unidades pedidas', 'units ordered', 'unidades-pedidas', 'total units', 'quantidade', 'qtd']
        qty_col = next((c for c in df.columns if any(p in c.lower() for p in qty_potentials)), None)
        if qty_col:
            df_export['Qtd total'] = df[qty_col].apply(clean_int)
        else:
            # Se não achou pelo nome, tenta colunas numéricas que não sejam IDs
            for c in df.columns:
                if 'id' not in c.lower() and 'sku' not in c.lower() and 'asin' not in c.lower():
                    sample = df[c].dropna().head(10)
                    if all(str(x).isdigit() for x in sample) and len(sample) > 0:
                        df_export['Qtd total'] = df[c].apply(clean_int)
                        break
        
        # 5. Busca por Faturamento (Busca profunda)
        fat_potentials = ['ordered-product-sales', 'vendas de produtos pedidos', 'ordered product sales', 'vendas-de-produtos-pedidos', 'revenue', 'faturamento', 'vendas', 'sales']
        fat_col = next((c for c in df.columns if any(p in c.lower() for p in fat_potentials)), None)
        if fat_col:
            df_export['Fat total'] = df[fat_col].apply(clean_money)
        else:
            # Se não achou pelo nome, tenta colunas que pareçam monetárias
            for c in df.columns:
                sample = df[c].astype(str).dropna().head(10)
                if any(curr in str(x) for x in sample for curr in ['R$', '$', ',']):
                    df_export['Fat total'] = df[c].apply(clean_money)
                    if df_export['Fat total'].sum() > 0:
                        break

        # Garantia de valores padrão se nada for encontrado
        if 'Qtd total' not in df_export.columns: df_export['Qtd total'] = 0
        if 'Fat total' not in df_export.columns: df_export['Fat total'] = 0.0
        
        # Remove linhas sem dados
        df_export = df_export[(df_export['Fat total'] > 0) | (df_export['Qtd total'] > 0)].copy()
        
        if df_export.empty:
            # Fallback final: se não achou nada, tenta as colunas que têm os maiores valores numéricos
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= 1:
                df_export['Fat total'] = df[numeric_cols[0]].fillna(0)
                df_export['Qtd total'] = df[numeric_cols[0]].fillna(0).astype(int)
                # Recria as colunas básicas se necessário
                if 'MLB' not in df_export.columns: df_export['MLB'] = df.index.astype(str)
                if 'Título' not in df_export.columns: df_export['Título'] = "Produto " + df_export['MLB']
                if 'SKU' not in df_export.columns: df_export['SKU'] = df_export['MLB']
            else:
                raise ValueError("Nenhum dado de venda ou faturamento encontrado no arquivo. Verifique se o relatório contém dados de pedidos.")

        # Métricas extras (opcional)
        conv_col = next((c for c in df.columns if any(p in c.lower() for p in ['percentage', 'conversão', 'conversao', 'taxa'])), None)
        if conv_col:
            def clean_pct(v):
                if pd.isna(v): return 0.0
                v = str(v).replace('%', '').replace(',', '.').strip()
                try:
                    return float(v) / 100
                except:
                    return 0.0
            df_export['_amazon_taxa_conversao'] = df[conv_col].apply(clean_pct)

        # Ticket Médio e Períodos
        df_export['TM total'] = df_export.apply(lambda row: row['Fat total'] / row['Qtd total'] if row['Qtd total'] > 0 else 0, axis=1)
        for periodo in ['0-30', '31-60', '61-90', '91-120']:
            df_export[f'Qntd {periodo}'] = df_export['Qtd total'] if periodo == '0-30' else 0
            df_export[f'Fat. {periodo}'] = df_export['Fat total'] if periodo == '0-30' else 0.0
            
        # Curva ABC
        df_export = self.calculate_abc_curve(df_export, 'Fat total')
        df_export['Curva 0-30'] = df_export['curva_abc']
        for p in ['31-60', '61-90', '91-120']: df_export[f'Curva {p}'] = '-'
        df_export = df_export.drop(columns=['curva_abc'], errors='ignore')
        
        return df_export, pd.DataFrame(), pd.DataFrame()
