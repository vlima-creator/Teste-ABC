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
        Verifica cabeçalhos característicos da Amazon em CSV ou TXT.
        """
        try:
            file.seek(0)
            filename = getattr(file, 'name', '').lower()
            
            # Tenta ler como CSV/TXT
            content = file.read(4096).decode('utf-8', errors='ignore')
            file.seek(0)
            
            # Indicadores comuns em relatórios da Amazon
            amazon_indicators = [
                '(parent) ASIN', '(child) ASIN', 'sku', 'product-name',
                'sessions', 'order-item-session-percentage', 'units-ordered',
                'ordered-product-sales', 'total-order-items', 'Nome do produto',
                'ASIN pai', 'ASIN filho', 'Sessões', 'Unidades pedidas',
                'Vendas de produtos pedidos', 'vendas-pedidas', 'unidades-pedidas'
            ]
            
            content_lower = content.lower()
            matches = sum(1 for ind in amazon_indicators if ind.lower() in content_lower)
            
            # Se encontrar indicadores ou o nome do arquivo sugerir Amazon
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
        
        # Tenta ler o arquivo com diferentes encodings e separadores
        df = None
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'utf-16']
        separators = [',', '\t', ';']
        
        for enc in encodings:
            for sep in separators:
                try:
                    file.seek(0)
                    df_tmp = pd.read_csv(file, sep=sep, encoding=enc, nrows=100)
                    # Se tiver mais de uma coluna, provavelmente acertamos o separador
                    if len(df_tmp.columns) > 1:
                        file.seek(0)
                        df = pd.read_csv(file, sep=sep, encoding=enc)
                        break
                except:
                    continue
            if df is not None:
                break
                
        if df is None:
            raise ValueError("Não foi possível determinar o formato do arquivo da Amazon (CSV/TXT).")

        # Limpeza de nomes de colunas
        df.columns = [str(c).strip() for c in df.columns]
        
        # Mapeamento flexível de colunas
        mapping = {
            'MLB': ['(parent) ASIN', 'ASIN pai', 'Parent ASIN', 'parent-asin', 'asin'],
            'SKU': ['sku', 'SKU', 'Seller SKU', 'seller-sku', '(child) ASIN', 'ASIN filho'],
            'Título': ['product-name', 'Nome do produto', 'Title', 'title', 'nome-do-produto'],
            'Qtd total': ['units-ordered', 'Unidades pedidas', 'Units Ordered', 'unidades-pedidas', 'Total Units'],
            'Fat total': ['ordered-product-sales', 'Vendas de produtos pedidos', 'Ordered Product Sales', 'vendas-de-produtos-pedidos', 'Revenue'],
            '_amazon_sessoes': ['sessions', 'Sessões', 'Sessions', 'sessões'],
            '_amazon_taxa_conversao': ['order-item-session-percentage', 'Percentual de sessões de itens do pedido', 'Unit Session Percentage']
        }
        
        df_export = pd.DataFrame()
        
        # Encontra as colunas reais no DF
        found_mapping = {}
        for target, potentials in mapping.items():
            for pot in potentials:
                # Busca exata ou parcial insensível a maiúsculas
                match = next((c for c in df.columns if c.lower() == pot.lower()), None)
                if match:
                    found_mapping[target] = match
                    break
        
        # Se não achou SKU mas achou ASIN, usa como SKU
        if 'SKU' not in found_mapping and 'MLB' in found_mapping:
            found_mapping['SKU'] = found_mapping['MLB']

        # Processa cada coluna encontrada
        for target, source in found_mapping.items():
            if target == 'Fat total':
                # Limpeza de valores monetários
                def clean_money(v):
                    if pd.isna(v): return 0.0
                    v = str(v).replace('R$', '').replace('$', '').replace('\xa0', '').strip()
                    # Se tiver ponto e virgula: 1.234,56 -> 1234.56
                    if '.' in v and ',' in v:
                        v = v.replace('.', '').replace(',', '.')
                    # Se tiver só virgula: 1234,56 -> 1234.56
                    elif ',' in v:
                        v = v.replace(',', '.')
                    try:
                        return float(re.sub(r'[^0-9.]', '', v))
                    except:
                        return 0.0
                df_export[target] = df[source].apply(clean_money)
            elif target == '_amazon_taxa_conversao':
                def clean_pct(v):
                    if pd.isna(v): return 0.0
                    v = str(v).replace('%', '').replace(',', '.').strip()
                    try:
                        return float(v) / 100
                    except:
                        return 0.0
                df_export[target] = df[source].apply(clean_pct)
            elif target == 'Qtd total':
                df_export[target] = pd.to_numeric(df[source].astype(str).str.replace(r'[^0-9]', '', regex=True), errors='coerce').fillna(0).astype(int)
            else:
                df_export[target] = df[source]

        # Garantia de colunas mínimas
        if 'MLB' not in df_export.columns: 
            # Se não achou ASIN pai, tenta qualquer coluna que pareça um ID
            id_cols = [c for c in df.columns if 'asin' in c.lower() or 'id' in c.lower() or 'sku' in c.lower()]
            df_export['MLB'] = df[id_cols[0]] if id_cols else "N/A"
            
        if 'Título' not in df_export.columns:
            title_cols = [c for c in df.columns if 'name' in c.lower() or 'nome' in c.lower() or 'título' in c.lower() or 'titulo' in c.lower()]
            df_export['Título'] = df[title_cols[0]] if title_cols else "Produto sem título"
            
        if 'SKU' not in df_export.columns: df_export['SKU'] = df_export['MLB']
        if 'Qtd total' not in df_export.columns: df_export['Qtd total'] = 0
        if 'Fat total' not in df_export.columns: df_export['Fat total'] = 0.0
        
        # Remove linhas onde faturamento e quantidade são zero (lixo de relatório)
        df_export = df_export[(df_export['Fat total'] > 0) | (df_export['Qtd total'] > 0)].copy()
        
        if df_export.empty:
            raise ValueError("Nenhum dado de venda ou faturamento encontrado no arquivo da Amazon.")

        # Ticket Médio
        df_export['TM total'] = df_export.apply(
            lambda row: row['Fat total'] / row['Qtd total'] if row['Qtd total'] > 0 else 0,
            axis=1
        )
        
        # Períodos (Snapshot)
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
