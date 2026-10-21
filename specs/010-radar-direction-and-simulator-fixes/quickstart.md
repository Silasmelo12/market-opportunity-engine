# Quickstart & Validation Guide: Correção do Radar e Seletor de Modelo de Ciclo

**Feature**: `010-radar-direction-and-simulator-fixes`  
**Date**: 2026-10-21  

---

## 1. Validação da Direção no Radar

1. Inicie a aplicação com `python run_server.py`.
2. Acesse `http://localhost:8000` e permaneça na aba **Radar**.
3. Clique no botão **"Venda"**:
   - Verifique que a tabela recarrega e passa a exibir oportunidades de topo/venda (com badges semânticos de timing).
   - Abra o dropdown de estratégias do radar e confirme que apenas estratégias de Venda são listadas.
4. Clique no botão **"Ambos"**:
   - Confirme que oportunidades de compra e venda aparecem simultaneamente.
5. Clique no botão **"Compra"**:
   - Confirme o retorno imediato à exibição exclusiva de compras.

---

## 2. Validação do Seletor de Modo de Entrada (1x vs Multi-Buy) no Simulador

1. Vá para a aba **Simulador**.
2. Selecione o ativo (ex: `NVDA`), tempo gráfico (ex: `5 Minutos`) e capital inicial (ex: `100`).
3. Selecione o modo **"Compra Única (1x por Ciclo)"**:
   - Clique em **"Mais Lucrativa"**: observe as métricas da campeã (ex: +22.5% e PnL de R$ 22,51).
   - Clique em **"Aplicar e Simular"**: verifique que os cards de KPI exibem exatamente as mesmas métricas (+22.5% de Retorno, R$ 22,51 de PnL e capital investido correspondente).
4. Alterne para o modo **"Acumulação Multi-Buy (Nx por Ciclo)"**:
   - Clique em **"Mais Lucrativa"**: observe que o ranking agora reflete compras acumuladas com preço médio.
   - Clique em **"Aplicar e Simular"**: confirme que as métricas do card da campeã coincidem fielmente com o resultado da simulação.

---

## 3. Validação Automatizada de Testes Unitários

```bash
# Executar a suíte de testes unitários garantindo 100% de aprovação
python -m pytest tests/unit/ -v
```
