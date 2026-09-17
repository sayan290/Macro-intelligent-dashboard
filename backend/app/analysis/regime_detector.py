import numpy as np
from typing import Optional
from datetime import datetime
import structlog

from app.ingestion.fred import FredClient
from app.ingestion.yahoo import YahooFinanceClient

logger = structlog.get_logger()

REGIMES = {
    "goldilocks": {
        "label": "Goldilocks",
        "description": "Strong growth, low inflation — risk assets thrive",
        "color": "#10B981",
    },
    "reflation": {
        "label": "Reflation",
        "description": "Rising growth, rising inflation — commodities & cyclicals benefit",
        "color": "#F59E0B",
    },
    "stagflation": {
        "label": "Stagflation",
        "description": "Weak growth, high inflation — defensive positioning needed",
        "color": "#EF4444",
    },
    "deflation": {
        "label": "Deflation",
        "description": "Falling growth, falling inflation — bonds outperform",
        "color": "#3B82F6",
    },
    "unknown": {
        "label": "Transitional",
        "description": "Mixed signals — regime transition in progress",
        "color": "#6B7280",
    },
}


class RegimeDetector:
    """Multi-factor macro regime detection engine."""

    def __init__(self):
        self.fred = FredClient()
        self.yahoo = YahooFinanceClient()

    async def detect(self) -> dict:
        """Run full regime detection analysis."""
        indicators = await self._gather_indicators()
        regime, confidence = self._classify(indicators)
        sub_regimes = self._detect_sub_regimes(indicators)

        return {
            "regime": regime,
            "confidence": confidence,
            "sub_regimes": sub_regimes,
            "indicators": indicators,
            "description": REGIMES.get(regime, REGIMES["unknown"])["description"],
            "label": REGIMES.get(regime, REGIMES["unknown"])["label"],
            "color": REGIMES.get(regime, REGIMES["unknown"])["color"],
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def _gather_indicators(self) -> dict:
        """Gather all macro indicators for regime classification."""
        indicators = {}

        # Growth indicators
        try:
            gdp = await self.fred.get_latest("GDP")
            indicators["gdp_growth"] = gdp.get("change_pct")
        except Exception:
            indicators["gdp_growth"] = None

        try:
            payrolls = await self.fred.get_latest("PAYEMS")
            indicators["payrolls_change"] = payrolls.get("change")
        except Exception:
            indicators["payrolls_change"] = None

        try:
            unemployment = await self.fred.get_latest("UNRATE")
            indicators["unemployment"] = unemployment.get("value")
        except Exception:
            indicators["unemployment"] = None

        # Inflation indicators
        try:
            cpi = await self.fred.get_latest("CPIAUCSL")
            indicators["cpi_yoy"] = cpi.get("change_pct")
        except Exception:
            indicators["cpi_yoy"] = None

        try:
            breakeven = await self.fred.get_latest("T10YIE")
            indicators["breakeven_10y"] = breakeven.get("value")
        except Exception:
            indicators["breakeven_10y"] = None

        # Rates
        try:
            fed_rate = await self.fred.get_latest("FEDFUNDS")
            indicators["fed_funds"] = fed_rate.get("value")
        except Exception:
            indicators["fed_funds"] = None

        try:
            spread = await self.fred.get_latest("T10Y2Y")
            indicators["yield_curve"] = spread.get("value")
        except Exception:
            indicators["yield_curve"] = None

        # Market volatility
        try:
            vix = await self.fred.get_latest("VIXCLS")
            indicators["vix"] = vix.get("value")
        except Exception:
            indicators["vix"] = None

        # Equity market
        try:
            spy = await self.yahoo.get_quote("SPY")
            if spy:
                indicators["spy_change"] = spy.get("change_pct")
        except Exception:
            indicators["spy_change"] = None

        return indicators

    def _classify(self, indicators: dict) -> tuple[str, float]:
        """Classify regime based on indicators."""
        scores = {"goldilocks": 0, "reflation": 0, "stagflation": 0, "deflation": 0}
        total_weight = 0

        # Growth assessment
        gdp = indicators.get("gdp_growth")
        if gdp is not None:
            weight = 2
            total_weight += weight
            if gdp > 2:
                scores["goldilocks"] += weight
                scores["reflation"] += weight * 0.5
            elif gdp > 0:
                scores["goldilocks"] += weight * 0.5
            else:
                scores["stagflation"] += weight * 0.5
                scores["deflation"] += weight

        # Inflation assessment
        cpi = indicators.get("cpi_yoy")
        if cpi is not None:
            weight = 2
            total_weight += weight
            if cpi is not None and cpi > 4:
                scores["reflation"] += weight
                scores["stagflation"] += weight
            elif cpi is not None and cpi > 2:
                scores["goldilocks"] += weight * 0.5
                scores["reflation"] += weight * 0.5
            else:
                scores["deflation"] += weight

        # Yield curve
        yc = indicators.get("yield_curve")
        if yc is not None:
            weight = 1.5
            total_weight += weight
            if yc < 0:
                scores["stagflation"] += weight * 0.5
                scores["deflation"] += weight * 0.5
            else:
                scores["goldilocks"] += weight * 0.5
                scores["reflation"] += weight * 0.5

        # VIX
        vix = indicators.get("vix")
        if vix is not None:
            weight = 1
            total_weight += weight
            if vix > 25:
                scores["stagflation"] += weight
                scores["deflation"] += weight * 0.5
            elif vix < 15:
                scores["goldilocks"] += weight

        if total_weight == 0:
            return "unknown", 0.0

        # Normalize
        max_regime = max(scores, key=scores.get)
        max_score = scores[max_regime]
        confidence = min(max_score / (total_weight * 1.5), 1.0)

        return max_regime, round(confidence, 2)

    def _detect_sub_regimes(self, indicators: dict) -> dict:
        """Detect sub-regime conditions."""
        sub = {}

        vix = indicators.get("vix")
        if vix is not None:
            if vix > 30:
                sub["volatility"] = "crisis"
            elif vix > 20:
                sub["volatility"] = "elevated"
            else:
                sub["volatility"] = "calm"

        yc = indicators.get("yield_curve")
        if yc is not None:
            if yc < -0.5:
                sub["yield_curve"] = "deeply_inverted"
            elif yc < 0:
                sub["yield_curve"] = "inverted"
            else:
                sub["yield_curve"] = "normal"

        ue = indicators.get("unemployment")
        if ue is not None:
            if ue < 4:
                sub["labor"] = "tight"
            elif ue < 6:
                sub["labor"] = "moderate"
            else:
                sub["labor"] = "weak"

        return sub
