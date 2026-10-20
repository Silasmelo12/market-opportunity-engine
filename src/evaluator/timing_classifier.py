"""
Timing Status Classifier (Semáforo de Atraso / "Entrei Atrasado?").
Compares the current asset price with the recommended execution price P_exec
(or active reference line level) and historical strategy forward returns for both BUY and SELL directions.
"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass(frozen=True)
class TimingStatus:
    status_category: str            # "IDEAL" | "EXTENDED" | "LATE"
    status_label: str               # Display badge string
    distance_pct: float             # Distância percentual do preço atual em relação ao preço sugerido
    recommended_price: float        # Preço sugerido de entrada (P_exec ou Linha de Referência)
    current_price: float            # Preço de fechamento da última barra
    strategy_sub_id: str
    strategy_label: str
    advice_text: str                # Recomendação objetiva
    direction: str = "BUY"          # "BUY" | "SELL"


def classify_timing_status(
    current_price: float,
    recommended_price: float,
    strategy_sub_id: str,
    strategy_label: Optional[str] = None,
    mean_forward_return: Optional[float] = None,
    is_awaiting_retest: bool = False,
    direction: str = "BUY",
) -> TimingStatus:
    """
    Classifies entry timing based on price distance from recommended entry:
    For BUY:
      - IDEAL: awaiting retest touch OR current_price <= recommended_price * 1.015 (up to +1.5%)
      - EXTENDED: +1.5% < distance <= +4.0%
      - LATE: distance > +4.0% OR consumed > 30% of strategy mean forward return
    For SELL:
      - IDEAL: awaiting retest touch OR current_price >= recommended_price * 0.985 (up to -1.5% from top)
      - EXTENDED: -4.0% <= distance < -1.5% (fell between 1.5% and 4.0% from top)
      - LATE: distance < -4.0% (fell > 4% from top, already dumped)
    """
    strat_name = strategy_label or strategy_sub_id
    is_buy = (direction == "BUY")

    if recommended_price <= 0 or current_price <= 0:
        return TimingStatus(
            status_category="IDEAL",
            status_label="🟢 ZONA IDEAL" if not is_buy else "🟢 ZONA IDEAL / DESCONTO",
            distance_pct=0.0,
            recommended_price=recommended_price,
            current_price=current_price,
            strategy_sub_id=strategy_sub_id,
            strategy_label=strat_name,
            advice_text="Entrada no nível planejado.",
            direction=direction,
        )

    dist_pct = ((current_price / recommended_price) - 1.0) * 100.0

    if is_buy:
        # BUY Logic
        if is_awaiting_retest or dist_pct <= 1.5:
            category = "IDEAL"
            label = "🟢 ZONA IDEAL / DESCONTO"
            if dist_pct < 0:
                advice = f"Preço com {abs(dist_pct):.1f}% de desconto sobre a entrada recomendada."
            elif is_awaiting_retest:
                advice = "Aguardando toque na linha de suporte no reteste."
            else:
                advice = f"Dentro da janela ideal de execução (+{dist_pct:.1f}%)."
        elif 1.5 < dist_pct <= 4.0:
            if mean_forward_return and mean_forward_return > 0 and (dist_pct > 0.30 * mean_forward_return):
                category = "LATE"
                label = "🔴 ATRASADO (BONDE ANDOU)"
                advice = f"Já consumiu {dist_pct:.1f}% do retorno médio esperado ({mean_forward_return:.1f}%). Risco/retorno desfavorável."
            else:
                category = "EXTENDED"
                label = "🟡 ESTENDIDO (CAUTELA)"
                advice = f"Preço subiu +{dist_pct:.1f}% acima da entrada. Recomenda-se aguardar um recuo (pullback)."
        else:
            category = "LATE"
            label = "🔴 ATRASADO (BONDE ANDOU)"
            advice = f"Preço estendido (+{dist_pct:.1f}% acima do ponto de compra). Aguarde novo ciclo/suporte."
    else:
        # SELL Logic
        # dist_pct = (Current - P_exec)/P_exec * 100. If current is 99 and P_exec is 100, dist_pct is -1.0%.
        if is_awaiting_retest or dist_pct >= -1.5:
            category = "IDEAL"
            label = "🟢 ZONA IDEAL (TOPO)"
            if dist_pct > 0:
                advice = f"Preço ainda acima da ativação (+{dist_pct:.1f}%). Excelente oportunidade no topo."
            elif is_awaiting_retest:
                advice = "Aguardando toque na linha de resistência no reteste."
            else:
                advice = f"Dentro da janela ideal de venda no topo ({dist_pct:.1f}%)."
        elif -4.0 <= dist_pct < -1.5:
            category = "EXTENDED"
            label = "🟡 ESTENDIDO (TOPO RECUOU)"
            advice = f"Preço já caiu {abs(dist_pct):.1f}% abaixo da máxima recomendada. Aguardar repique se possível."
        else:
            category = "LATE"
            label = "🔴 ATRASADO (PREÇO DERRETEU)"
            advice = f"Preço já despencou {abs(dist_pct):.1f}% abaixo do topo. Risco/retorno de venda desfavorável."

    return TimingStatus(
        status_category=category,
        status_label=label,
        distance_pct=round(dist_pct, 2),
        recommended_price=round(recommended_price, 2),
        current_price=round(current_price, 2),
        strategy_sub_id=strategy_sub_id,
        strategy_label=strat_name,
        advice_text=advice,
        direction=direction,
    )
