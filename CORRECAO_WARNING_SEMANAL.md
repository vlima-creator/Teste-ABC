# Correção: Warning Semanal - Últimas 5 Semanas

## Problema Identificado

A aba de **Warning Semanal** estava exibindo dados que poderiam incluir o período completo do relatório, em vez de se limitar às **últimas 5 semanas** como deveria.

### Cenário do Problema
- Quando um relatório de **6 meses** era carregado, as métricas e alertas da aba Warning Semanal poderiam refletir dados de todo o período
- Isso tornava impossível analisar o **comportamento recente** das vendas
- O usuário precisava entender o que aconteceu nos **últimos dias**, não em todo o período

## Solução Implementada

### 1. **WeeklyAnalyzer.calculate_warnings()** (data_processing/weekly_analyzer.py)

**Adição de Filtro Explícito:**
```python
# Garantir que apenas as 5 semanas mais recentes estão presentes
cols_to_keep = [col for col in result.columns if not (col.startswith('Qntd ') or col.startswith('Fat. ') or col.startswith('Curva ')) or col in ['Qntd Sem1', 'Qntd Sem2', 'Qntd Sem3', 'Qntd Sem4', 'Qntd Sem5', 'Fat. Sem1', 'Fat. Sem2', 'Fat. Sem3', 'Fat. Sem4', 'Fat. Sem5', 'Curva Sem1', 'Curva Sem2', 'Curva Sem3', 'Curva Sem4', 'Curva Sem5']]
result = result[cols_to_keep]
```

**Benefício:** Remove qualquer coluna de semanas anteriores a Sem5, garantindo que APENAS as últimas 5 semanas sejam processadas.

### 2. **Documentação Explícita**

Adicionados comentários e docstrings em:
- `render_warning_semanal_tab()` - Deixa claro que a aba SEMPRE mostra apenas 5 semanas
- `calculate_warnings()` - Documenta que o método trabalha SEMPRE com Sem1 a Sem5
- `calculate_weekly_curves()` - Reforça que filtra para as últimas 5 semanas

### 3. **Garantias de Integridade**

Os cálculos de **Delta** (comparação entre semanas) SEMPRE usam:
- **Sem1** (semana mais recente) vs **Sem2** (semana anterior)
- Independentemente de quantas semanas existem no relatório original

```python
# Delta de Faturamento (SEMPRE comparando Sem1 vs Sem2)
result['Delta % Fat'] = result.apply(
    lambda r: ((r.get('Fat. Sem1', 0) - r.get('Fat. Sem2', 0)) / r.get('Fat. Sem2', 1) * 100) 
             if r.get('Fat. Sem2', 0) > 0 else 0,
    axis=1
).fillna(0)
```

## Impacto das Mudanças

| Aspecto | Antes | Depois |
|--------|-------|--------|
| **Período Analisado** | Variável (todo o relatório) | Fixo (últimas 5 semanas) |
| **Comparação de Curva ABC** | Sem1 vs Sem2 (correto) | Sem1 vs Sem2 (garantido) |
| **Alertas de Queda** | Poderia incluir dados antigos | Apenas últimas 5 semanas |
| **Análise de Comportamento** | Confusa em relatórios longos | Clara e focada |

## Teste de Validação

Para validar que a correção funciona:

1. **Carregue um relatório de 6+ meses**
2. **Acesse a aba "Warning Semanal"**
3. **Verifique que:**
   - Apenas 5 colunas de semanas aparecem (Sem1 a Sem5)
   - Os deltas comparam Sem1 vs Sem2
   - Os alertas refletem apenas o comportamento recente
   - Os totais correspondem apenas às últimas 5 semanas

## Arquivos Modificados

- `data_processing/weekly_analyzer.py` - Adicionado filtro em `calculate_warnings()`
- `ui/tabs/warning_semanal_tab.py` - Adicionados comentários de documentação

## Notas Importantes

- ✅ A lógica de cálculo semanal em `add_weekly_analysis()` já estava correta
- ✅ O pivot de dados já limitava a Sem1-Sem5
- ✅ A correção garante que nenhuma coluna de semanas anteriores seja processada
- ✅ Compatível com todos os processadores (Mercado Livre, Amazon, Shopee)
