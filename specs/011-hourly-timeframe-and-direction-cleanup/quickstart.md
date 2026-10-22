# Quickstart & Validation: Suporte ao Timeframe 1h e Ocultação do Seletor de Direção

**Feature**: `011-hourly-timeframe-and-direction-cleanup`  
**Date**: 2026-10-21  

---

## 1. Validação do Timeframe 1h / 60m

1. Inicie a aplicação com `python run_server.py`.
2. Acesse a aba **Simulador** em `http://localhost:8000`.
3. Selecione o ativo (ex: `PETR4.SA`) e o tempo gráfico **"60 Minutos (1 Hora)"**.
4. Clique em **"Simular"**:
   - Confirme que a requisição retorna HTTP 200 com sucesso.
   - Verifique que as métricas de retorno, trades e curva patrimonial são renderizadas sem nenhum erro 400.
5. Clique em **"Mais Lucrativa"**:
   - Confirme que a otimização de combinações executa com sucesso em sub-segundo.

---

## 2. Validação da Ocultação do Seletor de Direção

1. Na aba **Radar**:
   - Verifique que o seletor segmentado "Compra", "Venda" e "Ambos" está visível no cabeçalho.
2. Clique na aba **Simulador**:
   - Confirme que o seletor "Compra, Venda, Ambos" desaparece imediatamente do cabeçalho.
3. Clique na aba **Playbook**:
   - Confirme que o seletor permanece oculto.
4. Clique na aba **Gráfico**:
   - Confirme que o seletor reaparece preservando a opção selecionada anteriormente.
