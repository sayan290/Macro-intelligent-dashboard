"""
Pre-defined backtesting strategy configurations.
"""

STRATEGY_PRESETS = {
    "regime_rotation": {
        "name": "Regime-Based Rotation",
        "description": "Rotates between asset classes based on macro regime detection",
        "default_params": {
            "lookback": 63,
            "rebalance_frequency": 21,
        },
        "default_symbols": ["SPY", "TLT", "GLD", "USO"],
    },
    "momentum": {
        "name": "Cross-Asset Momentum",
        "description": "Buys top-performing assets over lookback period",
        "default_params": {
            "lookback_period": 63,
            "top_n": 2,
            "rebalance_frequency": 21,
        },
        "default_symbols": ["SPY", "QQQ", "TLT", "GLD", "EEM"],
    },
    "mean_reversion": {
        "name": "Pairs Mean Reversion",
        "description": "Trades mean reversion of ratio between two assets",
        "default_params": {
            "z_score_entry": 2.0,
            "z_score_exit": 0.5,
            "window": 30,
        },
        "default_symbols": ["SPY", "IWM"],
    },
}
