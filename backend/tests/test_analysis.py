import pytest


class TestRegimeDetector:
    """Test regime detection logic."""

    def test_classify_goldilocks(self):
        from app.analysis.regime_detector import RegimeDetector
        detector = RegimeDetector()
        indicators = {
            "gdp_growth": 3.0,
            "cpi_yoy": 2.0,
            "yield_curve": 0.5,
            "vix": 12,
        }
        regime, confidence = detector._classify(indicators)
        assert regime == "goldilocks"
        assert confidence > 0

    def test_classify_stagflation(self):
        from app.analysis.regime_detector import RegimeDetector
        detector = RegimeDetector()
        indicators = {
            "gdp_growth": -1.0,
            "cpi_yoy": 6.0,
            "yield_curve": -0.5,
            "vix": 30,
        }
        regime, confidence = detector._classify(indicators)
        assert regime == "stagflation"

    def test_sub_regimes(self):
        from app.analysis.regime_detector import RegimeDetector
        detector = RegimeDetector()
        indicators = {"vix": 35, "yield_curve": -0.8, "unemployment": 3.5}
        sub = detector._detect_sub_regimes(indicators)
        assert sub["volatility"] == "crisis"
        assert sub["yield_curve"] == "deeply_inverted"
        assert sub["labor"] == "tight"
