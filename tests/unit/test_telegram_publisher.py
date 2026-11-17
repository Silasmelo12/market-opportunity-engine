import pytest
from unittest.mock import MagicMock, patch
from src.integrations.telegram_publisher import TelegramPublisher


def test_telegram_validate_credentials_missing():
    pub = TelegramPublisher(bot_token="", chat_id="")
    with pytest.raises(ValueError, match="Credenciais do Telegram ausentes"):
        pub.validate_credentials()


def test_format_opportunities_html():
    opps = [
        {
            "ticker": "PETR4",
            "category": "Ações Brasil",
            "current_price": 38.50,
            "historical_win_rate": 82.5,
            "timing_label": "Zona Ideal",
            "strategy": "Z-Score Extremo",
        }
    ]
    html = TelegramPublisher.format_opportunities_html(opps, date_str="30/10/2026")
    assert "PETR4" in html
    assert "82.5%" in html
    assert "R$ 38.50" in html
    assert "<b>" in html
    assert "Não constitui recomendação" in html


@patch("httpx.Client")
def test_send_message_mock(mock_client_class):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "ok": True,
        "result": {
            "message_id": 999,
            "chat": {"title": "Canal de Alertas", "first_name": "Canal"},
        },
    }
    mock_client.__enter__.return_value.post.return_value = mock_response
    mock_client_class.return_value = mock_client

    pub = TelegramPublisher(bot_token="test_token", chat_id="12345")
    res = pub.send_message("<b>Teste</b>")
    assert res["success"] is True
    assert res["message_id"] == 999
