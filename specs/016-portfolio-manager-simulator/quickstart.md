# Quickstart & Validation Guide: Gestor, Consultor de Rebalanceamento e Simulador Multiativos de Carteira

**Feature**: `016-portfolio-manager-simulator`  
**Date**: 2026-10-22

---

## 1. Pré-requisitos

- Ambiente virtual Python 3.10+ com dependências de `requirements.txt` instaladas (`fastapi`, `uvicorn`, `numpy`, `pandas`, `pydantic`, `pytest`).
- Cache de dados local em `.cache/data/` populado (ou conexão à internet para download via `yfinance`).

---

## 2. Executando os Testes Automatizados

Para validar matematicamente o Score de Potencial, as 3 regras de saída/rebalanceamento (`SELL_FULL`, `SELL_PARTIAL_REBALANCE`, `ROTATE`), a conservação de caixa, o *Zero Look-Ahead Bias* e os contratos REST (`/api/portfolio/advise` e `/api/portfolio/simulate`):

```powershell
pytest -v
```

Para executar apenas a suíte dedicada ao motor de carteira:

```powershell
pytest tests/unit/test_portfolio_simulator.py tests/unit/test_api_endpoints.py -v
```

---

## 3. Cenários de Validação End-to-End no Terminal Web

1. **Inicie o servidor**:
   ```powershell
   python run_server.py
   ```
2. **Acesse no navegador**: `http://localhost:8000`
3. **Cenário A — Alocação Inicial de R$ 10.000,00 em Caixa**:
   - Clique na 5ª aba principal **"Carteira"** no topo.
   - Verifique que o seletor global "Compra / Venda / Ambos" é ocultado automaticamente.
   - Com `Caixa Disponível = 10000`, `Posições Atuais = vazio (100% em caixa)`, `Universo = Destaques` e `Limite Máx. por Ativo = 25%`, clique em **"Gerar Plano de Hoje & Simular Carteira"**.
   - **Resultado esperado**:
     - Na seção **Plano de Ação de Hoje**, o sistema lista quais ativos comprar agora (priorizando sinais em timing `IDEAL` e maior Score de Potencial), a quantidade exata de cotas e o valor em R$ (nunca ultrapassando R$ 2.500,00 por ativo nem os R$ 10.000,00 totais).
     - Na seção **Simulador Histórico da Carteira**, exibe os KPIs consolidados, o gráfico comparativo (Carteira Dinâmica vs. Buy & Hold Equal-Weight da Cesta) e o livro razão de todas as compras, vendas de topo, vendas parciais de rebalanceamento e rotações táticas.
4. **Cenário B — Rebalanceamento de uma Carteira já Existente**:
   - Adicione manualmente no editor lateral uma posição com excesso de peso (ex: `PETR4.SA`, `300 cotas`, preço médio `32.00`) junto com `R$ 2.000,00` de caixa.
   - Clique em **"Gerar Plano de Hoje & Simular Carteira"**.
   - **Resultado esperado**: O Consultor de Rebalanceamento identifica que `PETR4.SA` excede o teto de 25% + banda de 5% (ou verifica se há sinal de topo) e emite uma ordem `VENDER PARCIAL / REBALANCEAR` (ou `VENDER TOTAL`), indicando quantas cotas vender e em quais ativos de maior potencial realocar o recurso.
5. **Cenário C — Persistência e Tema Claro/Escuro**:
   - Recarregue a página (`F5`) e confirme que o caixa e os ativos cadastrados na carteira foram preservados via `localStorage`.
   - Alterne o botão de tema (`🌙 Escuro` / `☀️ Claro`) e confirme a adaptação imediata dos gráficos Plotly e badges da aba "Carteira".
