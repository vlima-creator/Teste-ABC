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
                    # Tenta ler as primeiras linhas para validar o separador
                    df_tmp = pd.read_csv(file, sep=sep, encoding=enc, nrows=5)
                    if len(df_tmp.columns) > 1:
                        file.seek(0)
                        df = pd.read_csv(file, sep=sep, encoding=enc)
                        # Se leu apenas uma coluna ou poucas linhas, pode ser o separador errado
                        if df.shape[1] <= 1:
                            df = None
                            continue
                        break
                except:
                    continue
            if df is not None:
                break
                
        if df is None:
            raise ValueError("Não foi possível ler o arquivo da Amazon. Verifique o formato CSV/TXT.")

        # Limpeza básica de nomes de colunas
        df.columns = [str(c).strip() for c in df.columns]
        
        # Funções auxiliares de limpeza
        def clean_money(v):
            if pd.isna(v): return 0.0
            v = str(v).replace('R$', '').replace('$', '').replace('\xa0', '').strip()
            # Trata casos como "1.234,56" -> "1234.56"
            if '.' in v and ',' in v:
                v = v.replace('.', '').replace(',', '.')
            elif ',' in v:
                # Se houver apenas uma vírgula e ela parecer um separador decimal
                if len(v.split(',')) == 2:
                    v = v.replace(',', '.')
                else:
                    v = v.replace(',', '')
            try:
                cleaned = re.sub(r'[^0-9.]', '', v)
                return float(cleaned) if cleaned else 0.0
            except:
                return 0.0

        def clean_int(v):
            if pd.isna(v): return 0
            try:
                # Remove decimais se existirem (ex: "10.0")
                v_str = str(v).split('.')[0].split(',')[0]
                cleaned = re.sub(r'[^0-9]', '', v_str)
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
        title_col = next((c for c in df.columns if any(p in c.lower() for p in ['product-name', 'nome do produto', 'title', 'título', 'titulo', 'nome-do-produto', 'product-title'])), None)
        df_export['Título'] = df[title_col].astype(str) if title_col else "Produto sem título"
        
        # 4. Busca por Quantidade (Busca profunda)
        qty_potentials = ['units-ordered', 'unidades pedidas', 'units ordered', 'unidades-pedidas', 'total units', 'quantidade', 'qtd', 'units']
        qty_col = next((c for c in df.columns if any(p in c.lower() for p in qty_potentials)), None)
        if qty_col:
            df_export['Qtd total'] = df[qty_col].apply(clean_int)
        else:
            # Tenta encontrar qualquer coluna que tenha "unidades" ou "units" no nome
            qty_col = next((c for c in df.columns if 'unid' in c.lower() or 'unit' in c.lower()), None)
            if qty_col:
                df_export['Qtd total'] = df[qty_col].apply(clean_int)
            else:
                df_export['Qtd total'] = 0
        
        # 5. Busca por Faturamento (Busca profunda)
        fat_potentials = ['ordered-product-sales', 'vendas de produtos pedidos', 'ordered product sales', 'vendas-de-produtos-pedidos', 'revenue', 'faturamento', 'vendas', 'sales', 'total-sales']
        fat_col = next((c for c in df.columns if any(p in c.lower() for p in fat_potentials)), None)
        if fat_col:
            df_export['Fat total'] = df[fat_col].apply(clean_money)
        else:
            # Tenta encontrar colunas que pareçam faturamento pelo nome
            fat_col = next((c for c in df.columns if 'venda' in c.lower() or 'fatur' in c.lower() or 'price' in c.lower()), None)
            if fat_col:
                df_export['Fat total'] = df[fat_col].apply(clean_money)
            else:
                df_export['Fat total'] = 0.0

        # Se não encontrou dados pelas colunas nomeadas, tenta busca por tipo de conteúdo
        if df_export['Fat total'].sum() == 0 and df_export['Qtd total'].sum() == 0:
            for c in df.columns:
                if any(p in c.lower() for p in ['id', 'sku', 'asin', 'nome', 'title', 'date', 'data']):
                    continue
                
                sample = df[c].astype(str).dropna().head(20)
                # Tenta detectar se é monetário
                sample_str = "".join(sample.astype(str))
                if any(curr in sample_str for curr in ['R$', '$', ',']) or '.' in sample_str:
                    vals = df[c].apply(clean_money)
                    if vals.sum() > 0:
                        # Se já tivermos faturamento, não substitui a menos que o novo seja maior (mais provável ser o total)
                        if 'Fat total' not in df_export.columns or vals.sum() > df_export['Fat total'].sum():
                            df_export['Fat total'] = vals
                        continue
                
                # Tenta detectar se é inteiro (quantidade)
                try:
                    vals_int = df[c].apply(clean_int)
                    if vals_int.sum() > 0 and df_export['Qtd total'].sum() == 0:
                        df_export['Qtd total'] = vals_int
                except:
                    pass

        # Garantia de valores padrão se nada for encontrado
        if 'Qtd total' not in df_export.columns: df_export['Qtd total'] = 0
        if 'Fat total' not in df_export.columns: df_export['Fat total'] = 0.0
        
        # Se MLB ou SKU ainda estão vazios ou N/A, tenta usar a primeira coluna do DF original
        if (df_export['MLB'] == "N/A").all() or (df_export['SKU'] == "N/A").all():
            df_export['MLB'] = df.iloc[:, 0].astype(str)
            df_export['SKU'] = df_export['MLB']
            if df_export['Título'].iloc[0] == "Produto sem título":
                # Tenta a segunda coluna para título se a primeira for ID
                if df.shape[1] > 1:
                    df_export['Título'] = df.iloc[:, 1].astype(str)

        # Remove linhas sem dados significativos
        df_export = df_export[(df_export['Fat total'] > 0) | (df_export['Qtd total'] > 0)].copy()
        
        if df_export.empty:
            # Fallback final: se não achou nada, mas o arquivo tem colunas numéricas, usa a primeira que encontrar
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= 1:
                df_export = pd.DataFrame()
                df_export['Fat total'] = df[numeric_cols[0]].fillna(0)
                df_export['Qtd total'] = df[numeric_cols[0]].fillna(0).astype(int)
                df_export['MLB'] = df.iloc[:, 0].astype(str)
                df_export['SKU'] = df_export['MLB']
                df_export['Título'] = "Produto " + df_export['MLB']
                
                # Re-filtra
                df_export = df_export[(df_export['Fat total'] > 0) | (df_export['Qtd total'] > 0)].copy()

        # Se AINDA estiver vazio, levanta o erro original
        if df_export.empty:
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
