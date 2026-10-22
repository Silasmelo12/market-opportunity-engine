# Quickstart & Verification Guide: Refatoração da Tabela do Radar

## 1. Verificação Automatizada
Executar a suíte de testes de endpoints web e de servidor:
```powershell
python -m pytest tests/unit/test_api_endpoints.py -v
```

Executar toda a suíte de regressão (82 testes):
```powershell
python -m pytest tests/ -v
```

---

## 2. Verificação Manual no Navegador

1. Iniciar o servidor local:
   ```powershell
   python -m uvicorn src.api.server:app --reload --port 8000
   ```
2. Acessar `http://localhost:8000` na aba **Radar de Oportunidades**.

### Teste A: Verificação das Colunas Removidas
1. Inspecione o cabeçalho da tabela:
   - As colunas **Categoria**, **Preço Atual** e **Ação** não devem existir.
   - O número total de colunas é exatamente 8.

### Teste B: Direção Compacta e Semáforo Minimalista
1. Observe a coluna **Dir**:
   - Cada linha deve exibir uma bolinha compacta com **`C`** (verde) para compras ou **`V`** (vermelho) para vendas.
2. Observe a coluna **Timing**:
   - Deve exibir apenas uma bolinha circular colorida (🟢, 🟡, ou 🔴).
   - Passe o mouse sobre a bolinha: o tooltip do navegador deve mostrar o nome do timing (ex: *"Ideal / Reteste Imediato"*).

### Teste C: Ordenação por Qtd Sinais e Win Rate
1. Clique no cabeçalho **Win Rate (%)**:
   - As linhas devem ser reordenadas imediatamente da maior assertividade para a menor, com uma seta indicadora.
   - Dê um segundo clique: a ordem deve se inverter para crescente.
2. Clique no cabeçalho **Qtd Sinais**:
   - As linhas devem ser reordenadas imediatamente pela quantidade $N$ de sinais históricos.
