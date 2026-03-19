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
            content = file.read(8192).decode('utf-8', errors='ignore')
            file.seek(0)
            
            amazon_indicators = [
                '(parent) ASIN', '(child) ASIN', 'sku', 'product-name',
                'sessions', 'order-item-session-percentage', 'units-ordered',
                'ordered-product-sales', 'total-order-items', 'Nome do produto',
                'ASIN pai', 'ASIN filho', 'Sessões', 'Unidades pedidas',
                'Vendas de produtos pedidos', 'vendas-pedidas', 'unidades-pedidas',
                'asin', 'seller-sku', 'product-title', 'sales-channel', 'order-id'
            ]
            
            content_lower = content.lower()
            matches = sum(1 for ind in amazon_indicators if ind.lower() in content_lower)
            
            # Detecção mais agressiva baseada em nomes de arquivos comuns da Amazon
            if matches >= 2 or any(x in filename for x in ["businessreport", "salesdashboard", "amazon", "pedidos", "sales"]):
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
            
        all_dfs = []
        
        for file in files:
            file.seek(0)
            df_file = None
            encodings = ['utf-8', 'latin1', 'iso-8859-1', 'utf-16', 'cp1252']
            separators = [',', '\t', ';', '|']
            
            for enc in encodings:
                for sep in separators:
                    try:
                        file.seek(0)
                        df_tmp = pd.read_csv(file, sep=sep, encoding=enc, nrows=10)
                        if len(df_tmp.columns) > 1:
                            file.seek(0)
                            df_file = pd.read_csv(file, sep=sep, encoding=enc)
                            if df_file.shape[1] <= 1:
                                df_file = None
                                continue
                            break
                    except:
                        continue
                if df_file is not None:
                    break
            
            if df_file is not None:
                # Limpeza de nomes de colunas
                df_file.columns = [str(c).strip() for c in df_file.columns]
                
                # Processar este arquivo individualmente
                df_processed = self._process_single_df(df_file)
                if not df_processed.empty:
                    all_dfs.append(df_processed)
        
        if not all_dfs:
            # Se nenhum arquivo foi processado com sucesso, tenta dar um erro informativo baseado no primeiro arquivo
            try:
                file = files[0]
                file.seek(0)
                # Lê o conteúdo como string para evitar erro de bytes no Sniffer do pandas
                content = file.read(1024).decode('utf-8', errors='ignore')
                file.seek(0)
                df_err = pd.read_csv(io.StringIO(content), sep=None, engine='python', nrows=5)
                cols_found = ", ".join(df_err.columns[:15])
            except:
                cols_found = "Desconhecidas"
                
            raise ValueError(
                f"Nenhum dado de venda ou faturamento encontrado nos arquivos enviados. "
                f"Colunas detectadas: [{cols_found}]. "
                "Verifique se os arquivos contêm dados de pedidos/vendas com valores maiores que zero."
            )

        # Combinar todos os DataFrames processados
        df_final = pd.concat(all_dfs, ignore_index=True)
        
        # Agrupar por SKU/MLB para consolidar dados de múltiplos arquivos
        # Usamos 'first' para o Título para manter o primeiro encontrado
        # Para Buy Box, usamos a média se houver múltiplos registros
        # Se houver faturamento sem Buybox (ex: arquivos diferentes), tentamos preservar o valor de Buybox
        df_final = df_final.groupby(['MLB', 'SKU']).agg({
            'Título': 'first',
            'Qtd total': 'sum',
            'Fat total': 'sum',
            'Buy Box %': lambda x: x[x > 0].mean() if (x > 0).any() else 0.0
        }).reset_index()

        # Filtro final para garantir que temos dados
        df_final = df_final[(df_final['Fat total'] > 0) | (df_final['Qtd total'] > 0)].copy()
        
        if df_final.empty:
            raise ValueError("Após processar todos os arquivos, nenhum dado de venda ou faturamento válido foi encontrado.")

        # Preenchimento de métricas padrão
        df_final['TM total'] = df_final.apply(lambda row: row['Fat total'] / row['Qtd total'] if row['Qtd total'] > 0 else 0, axis=1)
        for p in ['0-30', '31-60', '61-90', '91-120']:
            df_final[f'Qntd {p}'] = df_final['Qtd total'] if p == '0-30' else 0
            df_final[f'Fat. {p}'] = df_final['Fat total'] if p == '0-30' else 0.0
            
        # Curva ABC
        df_final = self.calculate_abc_curve(df_final, 'Fat total')
        df_final['Curva 0-30'] = df_final['curva_abc']
        for p in ['31-60', '61-90', '91-120']: df_final[f'Curva {p}'] = '-'
        df_final = df_final.drop(columns=['curva_abc'], errors='ignore')
        
        return df_final, pd.DataFrame(), pd.DataFrame()

    def _process_single_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Processa um único DataFrame da Amazon."""
        
        # Funções de limpeza de dados
        def clean_money(v):
            if pd.isna(v): return 0.0
            s = str(v).replace('R$', '').replace('$', '').replace('\xa0', '').strip()
            if not s: return 0.0
            
            # Lógica para tratar 1.234,56 ou 1,234.56 ou 1234,56
            if ',' in s and '.' in s:
                if s.find('.') < s.find(','): # 1.234,56
                    s = s.replace('.', '').replace(',', '.')
                else: # 1,234.56
                    s = s.replace(',', '')
            elif ',' in s:
                # Verifica se a vírgula parece decimal (ex: 10,50) ou milhar (ex: 1,000)
                parts = s.split(',')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    s = s.replace(',', '.')
                else:
                    s = s.replace(',', '')
            
            try:
                cleaned = re.sub(r'[^0-9.]', '', s)
                return float(cleaned) if cleaned else 0.0
            except:
                return 0.0

        def clean_int(v):
            if pd.isna(v): return 0
            try:
                s = str(v).split('.')[0].split(',')[0]
                cleaned = re.sub(r'[^0-9]', '', s)
                return int(cleaned) if cleaned else 0
            except:
                return 0

        def clean_pct(v):
            if pd.isna(v): return 0.0
            try:
                # Remove símbolos, espaços e lida com separadores decimais (vírgula para ponto)
                s = str(v).replace('%', '').replace('\xa0', '').strip()
                if ',' in s and '.' in s:
                    if s.find('.') < s.find(','): s = s.replace('.', '').replace(',', '.')
                    else: s = s.replace(',', '')
                elif ',' in s:
                    parts = s.split(',')
                    if len(parts) == 2 and len(parts[1]) <= 2: s = s.replace(',', '.')
                    else: s = s.replace(',', '')
                
                cleaned = re.sub(r'[^0-9.]', '', s)
                return float(cleaned) if cleaned else 0.0
            except:
                return 0.0

        df_export = pd.DataFrame()
        
        # 1. Identificadores (ASIN/SKU)
        mlb_patterns = ['(parent) asin', 'asin pai', 'parent-asin', 'asin', 'sku', 'seller-sku', 'item-id']
        mlb_col = next((c for c in df.columns if any(p in c.lower() for p in mlb_patterns)), df.columns[0])
        df_export['MLB'] = df[mlb_col].astype(str)
        df_export['SKU'] = df_export['MLB']
        
        # 2. Título
        title_patterns = ['product-name', 'nome do produto', 'title', 'título', 'titulo', 'product-title', 'nome']
        title_col = next((c for c in df.columns if any(p in c.lower() for p in title_patterns)), None)
        if title_col:
            df_export['Título'] = df[title_col].astype(str)
        else:
            # Se não achar título, tenta a segunda coluna se for string
            if df.shape[1] > 1 and df.iloc[:, 1].dtype == object:
                df_export['Título'] = df.iloc[:, 1].astype(str)
            else:
                df_export['Título'] = "Produto " + df_export['MLB']
        
        # 3. Quantidade
        qty_patterns = ['units-ordered', 'unidades pedidas', 'units ordered', 'unidades-pedidas', 'total units', 'quantidade', 'qtd', 'units', 'quantity']
        qty_col = next((c for c in df.columns if any(p in c.lower() for p in qty_patterns)), None)
        if qty_col:
            df_export['Qtd total'] = df[qty_col].apply(clean_int)
        else:
            df_export['Qtd total'] = 0
            
        # 4. Faturamento
        fat_patterns = ['ordered-product-sales', 'vendas de produtos pedidos', 'ordered product sales', 'vendas-de-produtos-pedidos', 'revenue', 'faturamento', 'vendas', 'sales', 'total-sales', 'price', 'preço', 'valor', 'item-price']
        fat_col = next((c for c in df.columns if any(p in c.lower() for p in fat_patterns)), None)
        if fat_col:
            df_export['Fat total'] = df[fat_col].apply(clean_money)
        else:
            df_export['Fat total'] = 0.0

        # 5. Buy Box % (Oferta em Destaque)
        buybox_patterns = ['porcentagem de ofertas em destaque', 'buy box percentage', 'buy box %', 'featured offer percentage', 'oferta em destaque']
        buybox_col = next((c for c in df.columns if any(p in c.lower() for p in buybox_patterns)), None)
        if buybox_col:
            df_export['Buy Box %'] = df[buybox_col].apply(clean_pct)
        else:
            df_export['Buy Box %'] = 0.0

        # BUSCA AGRESSIVA por conteúdo se as colunas nomeadas falharem
        if df_export['Fat total'].sum() == 0 or df_export['Qtd total'].sum() == 0:
            for c in df.columns:
                # Pula colunas que já sabemos serem de texto
                if c in [mlb_col, title_col]: continue
                
                sample = df[c].dropna().head(20).astype(str)
                if sample.empty: continue
                
                # Testa se parece faturamento (tem símbolo de moeda ou decimais)
                sample_str = "".join(sample)
                if any(curr in sample_str for curr in ['R$', '$', ',']) or ('.' in sample_str and not all(x.isdigit() for x in sample)):
                    vals = df[c].apply(clean_money)
                    if vals.sum() > df_export['Fat total'].sum():
                        df_export['Fat total'] = vals
                
                # Testa se parece quantidade (apenas números inteiros)
                if all(re.match(r'^\d+$', str(x).split('.')[0]) for x in sample if str(x).strip()):
                    vals_int = df[c].apply(clean_int)
                    # Se a coluna de faturamento ainda estiver vazia e essa tiver valores altos, 
                    # pode ser faturamento sem formatação. Se forem valores baixos, é quantidade.
                    if vals_int.mean() > 100 and df_export['Fat total'].sum() == 0:
                        df_export['Fat total'] = vals_int.astype(float)
                    elif vals_int.sum() > df_export['Qtd total'].sum():
                        df_export['Qtd total'] = vals_int

        # Filtro para remover linhas sem dados
        df_export = df_export[(df_export['Fat total'] > 0) | (df_export['Qtd total'] > 0)].copy()
        
        return df_export
