"""
Processador de dados da Shopee.
Transforma relatórios da Shopee no formato padronizado de curva ABC.
"""
import pandas as pd
import numpy as np
import re
from typing import Tuple, Optional
from .base_processor import BaseProcessor


class ShopeeProcessor(BaseProcessor):
    """Processador para relatórios da Shopee."""
    
    def __init__(self):
        super().__init__()
        self.canal_name = "Shopee"
    
    def detect(self, file) -> bool:
        """
        Detecta se o arquivo é um relatório da Shopee.
        Verifica cabeçalhos característicos da Shopee.
        """
        try:
            file.seek(0)
            # Tenta ler as primeiras linhas
            df_preview = pd.read_excel(file, nrows=5)
            file.seek(0)
            
            # Colunas características da Shopee
            shopee_indicators = [
                'ID do Item',
                'SKU Principle',
                'Visitantes do Produto',
                'Taxa de conversão (Pedido pago)',
                'Vendas (Pedido pago) (BRL)'
            ]
            
            # Verifica se pelo menos 2 indicadores estão presentes
            matches = sum(1 for col in df_preview.columns if any(ind in str(col) for ind in shopee_indicators))
            return matches >= 2
            
        except Exception:
            return False
    
    def process(self, files: list) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        Processa relatórios da Shopee.
        
        Arquivos esperados:
        - parentskudetail: Performance por produto
        - sales_overview: Visão geral de vendas (opcional)
        - traffic_overview: Visão geral de tráfego (opcional)
        """
        # Identifica cada tipo de arquivo
        product_file = None
        sales_file = None
        traffic_file = None
        
        for file in files:
            file.seek(0)
            try:
                df_test = pd.read_excel(file, nrows=2)
                cols = [str(c).lower() for c in df_test.columns]
                
                if 'id do item' in cols or 'sku principle' in cols:
                    product_file = file
                elif 'compradores (pedidos feitos)' in cols:
                    sales_file = file
                elif 'visualizações da página' in cols and 'taxa de devolução' in cols:
                    traffic_file = file
                    
                file.seek(0)
            except Exception:
                file.seek(0)
                continue
        
        if product_file is None:
            raise ValueError("Arquivo de performance de produtos da Shopee não encontrado")
        
        # Processa arquivo principal de produtos
        df_export = self._process_product_performance(product_file)
        
        # Processa arquivos complementares se disponíveis
        df_sales = self._process_sales_overview(sales_file) if sales_file else None
        df_traffic = self._process_traffic_overview(traffic_file) if traffic_file else None
        
        # Extrai dados de PC vs Aplicativo do traffic_overview
        if traffic_file:
            pc_app_data = self._extract_pc_app_data(traffic_file)
            if pc_app_data:
                # Adiciona como colunas no DataFrame principal (replicado para todas as linhas para facilitar acesso na UI)
                df_export['_shopee_visitantes_pc'] = pc_app_data['pc']
                df_export['_shopee_visitantes_app'] = pc_app_data['app']
        
        # Shopee não tem dados de logística e ads no formato do ML
        df_logistics = pd.DataFrame()
        df_ads = pd.DataFrame()
        
        return df_export, df_logistics, df_ads
    
    def _process_product_performance(self, file) -> pd.DataFrame:
        """
        Processa o arquivo de performance de produtos (parentskudetail).
        """
        file.seek(0)
        df = pd.read_excel(file, sheet_name=0)
        
        # Remove linhas vazias
        df = df.dropna(how='all')
        
        # Filtra apenas produtos pai (linhas com dados agregados)
        # Produtos pai têm valores em 'Visitantes do Produto (Visita)'
        df_pai = df[df['Visitantes do Produto (Visita)'].notna()].copy()
        
        if df_pai.empty:
            raise ValueError("Nenhum produto pai encontrado no relatório da Shopee")
        
        # Mapeia colunas para o formato padronizado
        df_export = pd.DataFrame()
        
        df_export['MLB'] = df_pai['SKU Principle'].astype(str).str.strip()
        df_export['Título'] = df_pai['Produto'].astype(str).str.strip()
        df_export['SKU'] = df_pai['SKU Principle'].astype(str).str.strip()
        
        # Métricas de vendas (Pedidos Pagos é o mais confiável)
        df_export['Qtd total'] = pd.to_numeric(df_pai['Unidades (Pedido pago)'], errors='coerce').fillna(0).astype(int)
        
        # Converte valores monetários (formato: "1.234,56")
        def parse_brl(value):
            if pd.isna(value):
                return 0.0
            if isinstance(value, (int, float)):
                return float(value)
            
            s = str(value).replace('R$', '').replace('$', '').replace('\xa0', '').strip()
            if not s: return 0.0
            
            # Lógica para tratar 1.234,56 ou 1,234.56 ou 1234,56
            if ',' in s and '.' in s:
                if s.find('.') < s.find(','): # 1.234,56
                    s = s.replace('.', '').replace(',', '.')
                else: # 1,234.56
                    s = s.replace(',', '')
            elif ',' in s:
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
        
        df_export['Fat total'] = df_pai['Vendas (Pedido pago) (BRL)'].apply(parse_brl)
        
        # Calcula ticket médio
        df_export['TM total'] = df_export.apply(
            lambda row: row['Fat total'] / row['Qtd total'] if row['Qtd total'] > 0 else 0,
            axis=1
        )
        
        # Calcula curva ABC baseada no faturamento total
        df_export = self.calculate_abc_curve(df_export, 'Fat total')
        
        # Como Shopee tem apenas um período no relatório padrão, replica para todos os períodos
        # para não quebrar a lógica de "Produtos Âncora" e "Plano Tático"
        for periodo in ['0-30', '31-60', '61-90', '91-120']:
            df_export[f'Qntd {periodo}'] = df_export['Qtd total'] if periodo == '0-30' else 0
            df_export[f'Fat. {periodo}'] = df_export['Fat total'] if periodo == '0-30' else 0.0
            df_export[f'Curva {periodo}'] = df_export['curva_abc']
        
        # Dados específicos da Shopee
        df_export['_shopee_visitantes'] = pd.to_numeric(df_pai['Visitantes do Produto (Visita)'], errors='coerce').fillna(0).astype(int)
        df_export['_shopee_visualizacoes'] = pd.to_numeric(df_pai['Visualizações da Página do Produto'], errors='coerce').fillna(0).astype(int)
        
        # Taxa de rejeição (formato: "31,93%")
        def parse_pct(value):
            if pd.isna(value):
                return 0.0
            if isinstance(value, (int, float)):
                return float(value) / 100 if float(value) > 1 else float(value)
            
            value_str = str(value).replace('%', '').replace(',', '.').strip()
            try:
                cleaned = re.sub(r'[^0-9.]', '', value_str)
                return float(cleaned) / 100 if cleaned else 0.0
            except:
                return 0.0
        
        df_export['_shopee_taxa_rejeicao'] = df_pai['Taxa de Rejeição do Produto'].apply(parse_pct)
        df_export['_shopee_taxa_conversao'] = df_pai['Taxa de conversão (Pedido pago)'].apply(parse_pct)
        
        # Adiciona ao carrinho
        df_export['_shopee_add_carrinho'] = pd.to_numeric(df_pai['Unidades (adicionar ao carrinho)'], errors='coerce').fillna(0).astype(int)
        df_export['_shopee_compradores'] = pd.to_numeric(df_pai['Compradores (Pedidos pago)'], errors='coerce').fillna(0).astype(int)
        
        # Remove coluna temporária
        df_export = df_export.drop(columns=['curva_abc'], errors='ignore')
        
        return df_export
    
    def _process_sales_overview(self, file) -> Optional[pd.DataFrame]:
        """
        Processa o arquivo de visão geral de vendas (sales_overview).
        """
        try:
            file.seek(0)
            df = pd.read_excel(file, sheet_name=0)
            
            # Remove linhas vazias
            df = df.dropna(how='all')
            
            # Pula a primeira linha (resumo) e pega dados diários
            df_daily = df[df['Data'].notna()].copy()
            df_daily = df_daily[df_daily['Data'] != 'Data']  # Remove header duplicado
            
            return df_daily
            
        except Exception as e:
            print(f"Erro ao processar sales_overview: {e}")
            return None
    
    def _process_traffic_overview(self, file) -> Optional[pd.DataFrame]:
        """
        Processa o arquivo de visão geral de tráfego (traffic_overview).
        """
        try:
            file.seek(0)
            # Lê todas as sheets (Todos, PC, Aplicativo)
            dfs = pd.read_excel(file, sheet_name=None)
            
            traffic_data = {}
            for sheet_name, df in dfs.items():
                # Remove linhas vazias
                df = df.dropna(how='all')
                
                # Pula a primeira linha (resumo) e pega dados diários
                df_daily = df[df['Data'].notna()].copy()
                df_daily = df_daily[df_daily['Data'] != 'Data']  # Remove header duplicado
                
                traffic_data[sheet_name] = df_daily
            
            return traffic_data
            
        except Exception as e:
            print(f"Erro ao processar traffic_overview: {e}")
            return None
    
    def _extract_pc_app_data(self, file) -> Optional[dict]:
        """
        Extrai dados de visitantes por origem (PC vs Aplicativo).
        """
        try:
            file.seek(0)
            # Lê todas as abas disponíveis
            xl = pd.ExcelFile(file)
            sheet_names = xl.sheet_names
            
            visitantes_pc = 0
            visitantes_app = 0
            
            if 'PC' in sheet_names:
                df_pc_raw = pd.read_excel(file, sheet_name='PC')
                # Localiza a linha que contém 'Data' para ser o header
                header_idx = df_pc_raw[df_pc_raw.iloc[:, 0] == 'Data'].index
                if not header_idx.empty:
                    idx = header_idx[0]
                    df_pc = df_pc_raw.iloc[idx+1:].copy()
                    df_pc.columns = df_pc_raw.iloc[idx].values
                    visitantes_pc = pd.to_numeric(df_pc['Visitantes'], errors='coerce').sum()
            
            if 'Aplicativo' in sheet_names:
                file.seek(0)
                df_app_raw = pd.read_excel(file, sheet_name='Aplicativo')
                header_idx = df_app_raw[df_app_raw.iloc[:, 0] == 'Data'].index
                if not header_idx.empty:
                    idx = header_idx[0]
                    df_app = df_app_raw.iloc[idx+1:].copy()
                    df_app.columns = df_app_raw.iloc[idx].values
                    visitantes_app = pd.to_numeric(df_app['Visitantes'], errors='coerce').sum()
            
            return {
                'pc': int(visitantes_pc) if not np.isnan(visitantes_pc) else 0,
                'app': int(visitantes_app) if not np.isnan(visitantes_app) else 0
            }
            
        except Exception as e:
            print(f"Erro ao extrair dados PC/App: {e}")
            return None
