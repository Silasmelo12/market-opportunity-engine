"""
Contrato do schema PortfolioAdviseRequest (spec 024 / US1).

Garante que a ausência de caixa na importação B3 seja tratada como zero e que
valores negativos sejam rejeitados. Teste puramente unitário: não importa o
servidor, não chama yfinance e não acessa a rede.
"""

import pytest
from pydantic import ValidationError

from src.api.schemas import PortfolioAdviseRequest


def test_portfolio_advise_request_defaults_available_cash_to_zero():
    """Sem available_cash informado, o caixa deve ser 0.0 (nunca R$ 10.000)."""
    request = PortfolioAdviseRequest()

    assert request.available_cash == 0.0


def test_portfolio_advise_request_accepts_explicit_zero_cash():
    """Caixa explicitamente zero continua válido (importação B3 sem caixa)."""
    request = PortfolioAdviseRequest(available_cash=0.0)

    assert request.available_cash == 0.0


@pytest.mark.parametrize("invalid_cash", [-1, -0.01])
def test_portfolio_advise_request_rejects_negative_available_cash(invalid_cash):
    """Caixa negativo é inválido e deve falhar na validação do schema."""
    with pytest.raises(ValidationError):
        PortfolioAdviseRequest(available_cash=invalid_cash)
