# Quickstart: Validação do Otimizador de Acumulação DCA

## Cenários de Teste

### Cenário 1: Otimização de DCA via API
Executar requisição POST para `/api/simulate/optimize` com:
```json
{
  "ticker": "PETR4.SA",
  "interval": "1d",
  "period": "2y",
  "simulation_mode": "accumulation",
  "contribution_amount": 1000.0,
  "initial_capital": 1000.0
}
```
**Resultado Esperado**:
- Resposta HTTP 200.
- `simulation_mode`: `"accumulation"`.
- `champion`: Preenchido com a melhor estratégia de compra (ex: `buy_sub_id` não nulo, `sell_sub_id` nulo ou "-").
- `top_combinations`: Lista contendo as melhores estratégias ordenadas por rentabilidade percentual.

### Cenário 2: Ergonomia Visual na Aba Simulador
1. Abrir a aplicação web em `http://localhost:8000`.
2. Acessar a aba **Simulador**.
3. No dropdown "Modo de Operação", selecionar **"Acumulação (DCA Fundos)"**.
4. Confirmar que o container de **"Estratégia de Venda (Saída / Topo)"** desaparece imediatamente.
5. Clicar no botão **"Mais Lucrativa"**.
6. Confirmar que o card da Campeã destaca a estratégia de compra mais rentável em DCA com seu retorno percentual, preço médio e total aportado.
7. Clicar em **"Aplicar e Simular"** e validar convergência de 100% dos KPIs.
