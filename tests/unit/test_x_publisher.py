import pytest
from unittest.mock import MagicMock, patch
from src.integrations.x_publisher import XPublisher


def test_validate_credentials_missing():
    publisher = XPublisher(
        consumer_key="",
        consumer_secret="",
        access_token="",
        access_token_secret="",
    )
    with pytest.raises(ValueError, match="Credenciais do X incompletas"):
        publisher.validate_credentials()


def test_format_opportunities_tweet_fit_280():
    opps = [
        {"ticker": "PETR4", "current_price": 38.50, "historical_win_rate": 78.4, "timing_label": "Zona de Compra"},
        {"ticker": "VALE3", "current_price": 61.20, "historical_win_rate": 72.1, "timing_label": "Zona de Compra"},
        {"ticker": "BBAS3", "current_price": 28.10, "historical_win_rate": 69.5, "timing_label": "Zona de Compra"},
    ]
    tweet = XPublisher.format_opportunities_tweet(opps, date_str="30/10")
    assert "PETR4" in tweet
    assert "VALE3" in tweet
    assert "Não é recomendação" in tweet
    assert len(tweet) <= 280


@patch("tweepy.Client")
def test_post_tweet_mock(mock_client_class):
    mock_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.data = {"id": "1234567890"}
    mock_instance.create_tweet.return_value = mock_response
    mock_client_class.return_value = mock_instance

    publisher = XPublisher(
        consumer_key="test_key",
        consumer_secret="test_secret",
        access_token="test_token",
        access_token_secret="test_token_secret",
    )
    result = publisher.post_tweet("Teste de tweet")
    assert result["success"] is True
    assert result["tweet_id"] == "1234567890"
    assert "https://x.com/i/web/status/1234567890" in result["url"]
