"""
Processador de dados da Amazon.
Transforma relatórios da Amazon no formato padronizado de curva ABC.
"""
import pandas as pd
import numpy as np
import io
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
        Verifica cabeçalhos característicos da Amazon em CSV ou TXT.
        """
        try:
            file.seek(0)
            filename = getattr(file, 'name', '').lower()
            
            # Tenta ler como CSV/TXT
            # Relatórios da Amazon costumam ser tab-separated (.txt) ou comma-separated (.csv)
            content = file.read(2048).decode('utf-8', errors='ignore')
            file.seek(0)
            
            # Indicadores comuns em relatórios da Amazon (Business Reports ou Sales Reports)
            amazon_indicators = [
                '(parent) ASIN',
                '(child) ASIN',
                'sku',
                'product-name',
                'sessions',
                'order-item-session-percentage',
                'units-ordered',
                'ordered-product-sales',
                'total-order-items',
                'Nome do produto',
                'ASIN pai',
                'ASIN filho',
                'Sessões',
                'Percentual de sessões de itens do pedido',
                'Unidades pedidas',
                'Vendas de produtos pedidos'
            ]
            
            content_lower = content.lower()
            matches = sum(1 for ind in amazon_indicators if ind.lower() in content_lower)
            
            # Se encontrar pelo menos 2 indicadores ou o nome do arquivo sugerir Amazon
            if matches >= 2:
                return True
            
            if "businessreport" in filename or "salesdashboard" in filename:
                return True
                
            return False
            
        except Exception:
            return False
    
    def process(self, files: list) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        Processa relatórios da Amazon.
        """
        if not files:
            raise ValueError("Nenhum arquivo fornecido")
            
        file = files[0]
        file.seek(0)
        
        # Detecta separador
        content = file.read(4096).decode('utf-8', errors='ignore')
        file.seek(0)
        
        sep = ','
        if '\t' in content and content.count('\t') > content.count(','):
            sep = '\t'
        elif ';' in content and content.count(';') > content.count(','):
            sep = ';'
            
        try:
            df = pd.read_csv(file, sep=sep)
        except Exception as e:
            file.seek(0)
            # Tenta com encoding diferente se falhar
            try:
                df = pd.read_csv(file, sep=sep, encoding='latin1')
            except:
                raise ValueError(f"Não foi possível ler o arquivo da Amazon: {str(e)}")
        
        # Mapeamento de colunas (Amazon pode estar em PT ou EN)
        col_map = {
            'sku': 'SKU',
            'SKU': 'SKU',
            '(parent) ASIN': 'MLB',
            'ASIN pai': 'MLB',
            '(child) ASIN': 'ASIN_FILHO',
            'ASIN filho': 'ASIN_FILHO',
            'product-name': 'Título',
            'Nome do produto': 'Título',
            'units-ordered': 'Qtd total',
            'Unidades pedidas': 'Qtd total',
            'ordered-product-sales': 'Fat total',
            'Vendas de produtos pedidos': 'Fat total',
            'sessions': '_amazon_sessoes',
            'Sessões': '_amazon_sessoes',
            'order-item-session-percentage': '_amazon_taxa_conversao',
            'Percentual de sessões de itens do pedido': '_amazon_taxa_conversao'
        }
        
        # Normaliza colunas do DF para facilitar busca
        df.columns = [c.strip() for c in df.columns]
        
        # Cria DF de exportação
        df_export = pd.DataFrame()
        
        # Busca colunas correspondentes
        found_cols = {}
        for key, target in col_map.items():
            if key in df.columns and target not in found_cols:
                found_cols[target] = key
        
        if 'SKU' not in found_cols and 'ASIN_FILHO' in found_cols:
             found_cols['SKU'] = found_cols['ASIN_FILHO']
        
        if 'MLB' not in found_cols and 'SKU' in found_cols:
             found_cols['MLB'] = found_cols['SKU']

        for target, source in found_cols.items():
            if target == 'Fat total':
                # Limpeza de valores monetários
                val = df[source].astype(str).str.replace(r'[^0-9,.]', '', regex=True)
                # Se tiver virgula e ponto, assume 1.234,56
                if val.str.contains(r'\.').any() and val.str.contains(r',').any():
                    val = val.str.replace('.', '').str.replace(',', '.')
                # Se tiver só virgula, assume 1234,56
                elif val.str.contains(r',').any():
                    val = val.str.replace(',', '.')
                df_export[target] = pd.to_numeric(val, errors='coerce').fillna(0.0)
            elif target == '_amazon_taxa_conversao':
                val = df[source].astype(str).str.replace('%', '').str.replace(',', '.')
                df_export[target] = pd.to_numeric(val, errors='coerce').fillna(0.0) / 100
            else:
                df_export[target] = df[source]

        # Preenche colunas obrigatórias faltantes
        if 'MLB' not in df_export.columns: df_export['MLB'] = 'N/A'
        if 'Título' not in df_export.columns: df_export['Título'] = 'Produto sem título'
        if 'SKU' not in df_export.columns: df_export['SKU'] = df_export['MLB']
        if 'Qtd total' not in df_export.columns: df_export['Qtd total'] = 0
        if 'Fat total' not in df_export.columns: df_export['Fat total'] = 0.0
        
        df_export['Qtd total'] = pd.to_numeric(df_export['Qtd total'], errors='coerce').fillna(0).astype(int)
        
        # Ticket Médio
        df_export['TM total'] = df_export.apply(
            lambda row: row['Fat total'] / row['Qtd total'] if row['Qtd total'] > 0 else 0,
            axis=1
        )
        
        # Períodos (Amazon report costuma ser um snapshot)
        for periodo in ['0-30', '31-60', '61-90', '91-120']:
            df_export[f'Qntd {periodo}'] = df_export['Qtd total'] if periodo == '0-30' else 0
            df_export[f'Fat. {periodo}'] = df_export['Fat total'] if periodo == '0-30' else 0.0
            
        # Curva ABC
        df_export = self.calculate_abc_curve(df_export, 'Fat total')
        df_export['Curva 0-30'] = df_export['curva_abc']
        df_export['Curva 31-60'] = '-'
        df_export['Curva 61-90'] = '-'
        df_export['Curva 91-120'] = '-'
        
        df_export = df_export.drop(columns=['curva_abc'], errors='ignore')
        
        return df_export, pd.DataFrame(), pd.DataFrame()
