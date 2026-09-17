import structlog
from typing import Optional

from app.ingestion.fred import FredClient

logger = structlog.get_logger()


class LiquidityTracker:
    """Global liquidity and Fed balance sheet tracker."""

    def __init__(self):
        self.fred = FredClient()

    async def fed_net_liquidity(self) -> dict:
        """Calculate Fed net liquidity = Balance Sheet - TGA - RRP."""
        bs = await self.fred.get_latest("WALCL")
        tga = await self.fred.get_latest("WTREGEN")
        rrp = await self.fred.get_latest("RRPONTSYD")

        bs_val = bs.get("value")
        tga_val = tga.get("value")
        rrp_val = rrp.get("value")

        if all(v is not None for v in [bs_val, tga_val, rrp_val]):
            net_liquidity = bs_val - tga_val - rrp_val
        else:
            net_liquidity = None

        return {
            "net_liquidity": net_liquidity,
            "components": {
                "balance_sheet": bs_val,
                "tga": tga_val,
                "rrp": rrp_val,
            },
            "change": {
                "balance_sheet_change": bs.get("change"),
                "tga_change": tga.get("change"),
                "rrp_change": rrp.get("change"),
            },
        }

    async def m2_money_supply(self) -> dict:
        """Get M2 money supply data."""
        data = await self.fred.get_series("M2SL", limit=24)
        return {
            "latest": data[0] if data else None,
            "series": data,
        }

    async def global_liquidity_proxy(self) -> dict:
        """Approximate global liquidity using Fed + ECB + BoJ balance sheets."""
        fed = await self.fred.get_latest("WALCL")
        m2 = await self.fred.get_latest("M2SL")

        return {
            "fed_balance_sheet": fed.get("value"),
            "us_m2": m2.get("value"),
            "description": "Proxy for global liquidity conditions",
        }
