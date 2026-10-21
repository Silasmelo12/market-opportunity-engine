"""
Unit tests for stripping corporate suffixes (S.A., S/A, SA) from asset names.
"""

from src.data_loader.normalizer import strip_corporate_suffix


def test_strip_corporate_suffix():
    assert strip_corporate_suffix("Petrobras S.A.") == "Petrobras"
    assert strip_corporate_suffix("Petrobras S/A") == "Petrobras"
    assert strip_corporate_suffix("Petrobras SA") == "Petrobras"
    assert strip_corporate_suffix("Petróleo Brasileiro S.A. - Petrobras") == "Petróleo Brasileiro - Petrobras"
    assert strip_corporate_suffix("Vale S.A.") == "Vale"
    assert strip_corporate_suffix("Itaú Unibanco Holding SA") == "Itaú Unibanco Holding"
    assert strip_corporate_suffix("Apple Inc.") == "Apple Inc."
    assert strip_corporate_suffix(None) == ""
    assert strip_corporate_suffix("") == ""
