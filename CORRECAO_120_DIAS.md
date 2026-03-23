# Correção: Filtro de 120 Dias para Mercado Livre

## Problema Identificado
O aplicativo estava acumulando dados de múltiplos meses (4, 5, 6 meses) quando um relatório de 6 meses era enviado. O esperado é que apenas os últimos **120 dias (4 meses)** sejam processados.

## Solução Implementada
Adicionado um filtro no arquivo `data_processing/mercado_livre_processor.py` na função `_transform_ml_raw()` que garante que apenas registros com até 120 dias sejam considerados.

### Código Alterado
**Arquivo:** `data_processing/mercado_livre_processor.py`
**Função:** `_transform_ml_raw()` (linha ~238-240)

```python
# Antes:
ref = base['data'].max()
base['dias'] = (ref - base['data']).dt.days

def bucket(d):
    if d <= 30:
        return '0-30'
    # ...

# Depois:
ref = base['data'].max()
base['dias'] = (ref - base['data']).dt.days

# Filtra para considerar apenas os últimos 120 dias (4 meses)
# Isso evita que dados de 5 ou 6 meses sejam acumulados no último bucket
base = base[base['dias'] <= 120].copy()

def bucket(d):
    if d <= 30:
        return '0-30'
    # ...
```

## Como Funciona
1. **Cálculo de dias:** O código calcula quantos dias cada venda tem em relação à data mais recente do relatório
2. **Filtro de 120 dias:** Apenas registros com `dias <= 120` são mantidos
3. **Classificação em buckets:** Os dados filtrados são então classificados em períodos:
   - **0-30:** Últimos 30 dias
   - **31-60:** 31 a 60 dias atrás
   - **61-90:** 61 a 90 dias atrás
   - **91-120:** 91 a 120 dias atrás

## Impacto
- ✅ Evita acumulação de dados de 5º e 6º mês no bucket '91-120'
- ✅ Mantém a estrutura de 4 períodos intacta
- ✅ Não afeta as funcionalidades existentes (logística, ads, curva ABC)
- ✅ Compatível com relatórios de qualquer tamanho (120 dias, 6 meses, 1 ano, etc.)

## Teste Recomendado
1. Enviar um relatório de 6 meses do Mercado Livre
2. Verificar que os dados mostrados correspondem apenas aos últimos 120 dias
3. Confirmar que os buckets 0-30, 31-60, 61-90, 91-120 têm valores corretos
4. Validar que as métricas de logística e ads não foram afetadas

