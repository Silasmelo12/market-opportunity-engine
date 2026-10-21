# Quickstart / Validação: Feature 006

## Pré-requisitos
- `pip install -r requirements.txt`
- Opcional: Redis local (`docker run -p 6379:6379 redis:7`) e `$env:REDIS_URL="redis://localhost:6379/0"`

## Testes automatizados
```powershell
pytest tests/test_double_patterns.py tests/test_radar_pagination.py -q
```
Esperado:
- Nenhum sinal `double_bottom_bos` com `close >= max(High[t-60:t])` ou `rsi[t] > 60`.
- Nenhum sinal `sell_double_top_bos` com `close <= min(Low[t-60:t])` ou `rsi[t] < 40`.
- Datas de `sell_double_bottom_inverted` == datas da lógica original do fundo duplo (idem topo/compra).
- `/api/radar?page=1` retorna `RadarPage` com ≤ 20 ativos; `page` fora do range → `items` vazio.
- Com Redis indisponível (`REDIS_URL` inválida) o endpoint responde 200.

## Validação manual
1. `python run_server.py` → abrir o terminal web.
2. Radar abre em **Compra**; botões na ordem Compra | Venda | Ambos; filtro de estratégias todo desmarcado.
3. Paginação visível; trocar de página; segunda abertura no mesmo dia ≤ 1s (`cached: true`).
4. Ausentes: badge de versão/FPS, "Terminal Quantitativo…", "Zona Ideal (Topo) 0,0%", "S.A." nos nomes.
5. Gráfico: botões +, −, Reset funcionam.
6. `GET /api/health` mostra `cache_backend`.
