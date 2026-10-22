# Quickstart & Verification Guide: Correção da Aba Gráfico e Persistência de Abas

## 1. Verificação Automatizada
Executar a suíte de testes de endpoints web e de servidor:
```powershell
python -m pytest tests/unit/test_api_endpoints.py -v
```

Executar toda a suíte de regressão (81 testes):
```powershell
python -m pytest tests/ -v
```

---

## 2. Verificação Manual no Navegador

1. Iniciar o servidor local:
   ```powershell
   python -m uvicorn src.api.server:app --reload --port 8000
   ```
2. Acessar `http://localhost:8000` no navegador.

### Teste A: Filtragem Inicial na Aba Gráfico
1. Clique na aba **Gráfico** mantendo o botão "Compra" selecionado no topo.
2. Observe a barra lateral esquerda de estratégias:
   - Os grupos de Venda (Topo) devem estar **invisíveis**.
   - Os grupos de Compra (Fundo) devem estar **visíveis**, incluindo o novo grupo "Indicadores Quantitativos de Fundo".
3. Alterne o botão para "Venda": os grupos de venda devem aparecer e os de compra devem sumir.

### Teste B: Plotagem dos Novos Indicadores
1. Na barra lateral da aba Gráfico, abra o acordeão "Indicadores Quantitativos de Fundo".
2. Marque a caixa de seleção de "Bandas de Bollinger" ou "Keltner Squeeze".
3. Verifique se os marcadores correspondentes aparecem plotados sobre as velas do gráfico TradingView.

### Teste C: Persistência de Aba com F5
1. Estando na aba **Gráfico**, pressione **F5** no teclado (ou clique no botão de recarregar da página).
2. A página deve recarregar e permanecer na aba **Gráfico** (a URL manterá `#terminal`), sem voltar para o Radar.
3. Repita o mesmo teste para a aba **Simulador** (a URL manterá `#simulator`).
