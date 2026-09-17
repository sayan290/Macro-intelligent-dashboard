"""Initial schema

Revision ID: 001
Create Date: 2024-01-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Market Data
    op.create_table(
        'market_data',
        sa.Column('id', sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column('symbol', sa.String(50), nullable=False),
        sa.Column('asset_class', sa.String(30), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('open', sa.Float()),
        sa.Column('high', sa.Float()),
        sa.Column('low', sa.Float()),
        sa.Column('close', sa.Float(), nullable=False),
        sa.Column('volume', sa.Float()),
        sa.Column('metadata_json', JSONB, server_default='{}'),
    )
    op.create_index('idx_market_data_symbol_ts', 'market_data', ['symbol', 'timestamp'])

    # Market Data Daily
    op.create_table(
        'market_data_daily',
        sa.Column('id', sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column('symbol', sa.String(50), nullable=False),
        sa.Column('asset_class', sa.String(30), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('open', sa.Float()),
        sa.Column('high', sa.Float()),
        sa.Column('low', sa.Float()),
        sa.Column('close', sa.Float(), nullable=False),
        sa.Column('adj_close', sa.Float()),
        sa.Column('volume', sa.BigInteger()),
        sa.Column('change_pct', sa.Float()),
    )
    op.create_index('idx_daily_symbol_date', 'market_data_daily', ['symbol', 'date'], unique=True)

    # Macro Series
    op.create_table(
        'macro_series',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('series_id', sa.String(100), unique=True, nullable=False),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('category', sa.String(100)),
        sa.Column('frequency', sa.String(20)),
        sa.Column('units', sa.String(200)),
        sa.Column('description', sa.Text()),
        sa.Column('last_updated', sa.DateTime()),
        sa.Column('metadata_json', JSONB, server_default='{}'),
    )

    # Macro Data Points
    op.create_table(
        'macro_data_points',
        sa.Column('id', sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column('series_id', sa.String(100), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('previous_value', sa.Float()),
        sa.Column('change', sa.Float()),
        sa.Column('change_pct', sa.Float()),
    )
    op.create_index('idx_macro_series_date', 'macro_data_points', ['series_id', 'date'], unique=True)

    # Economic Events
    op.create_table(
        'economic_events',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('event_name', sa.String(300), nullable=False),
        sa.Column('country', sa.String(5), nullable=False),
        sa.Column('datetime_utc', sa.DateTime(), nullable=False),
        sa.Column('impact', sa.String(10)),
        sa.Column('category', sa.String(100)),
        sa.Column('actual', sa.String(50)),
        sa.Column('forecast', sa.String(50)),
        sa.Column('previous', sa.String(50)),
        sa.Column('source', sa.String(50)),
        sa.Column('is_processed', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime()),
    )
    op.create_index('idx_events_datetime', 'economic_events', ['datetime_utc'])

    # Event Impacts
    op.create_table(
        'event_impacts',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(50), nullable=False),
        sa.Column('pre_event_price', sa.Float()),
        sa.Column('post_event_price_5m', sa.Float()),
        sa.Column('post_event_price_1h', sa.Float()),
        sa.Column('post_event_price_1d', sa.Float()),
        sa.Column('volatility_impact', sa.Float()),
        sa.Column('direction', sa.String(10)),
    )

    # Alerts
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('alert_type', sa.String(50), nullable=False),
        sa.Column('condition', JSONB, nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('channels', JSONB, server_default='["telegram"]'),
        sa.Column('cooldown_minutes', sa.Integer(), server_default='60'),
        sa.Column('last_triggered', sa.DateTime()),
        sa.Column('created_at', sa.DateTime()),
    )

    # Alert Triggers
    op.create_table(
        'alert_triggers',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('alert_id', sa.Integer(), nullable=False),
        sa.Column('triggered_at', sa.DateTime()),
        sa.Column('message', sa.Text()),
        sa.Column('data', JSONB),
        sa.Column('delivered', sa.Boolean(), server_default='false'),
    )

    # Regime States
    op.create_table(
        'regime_states',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('regime', sa.String(50), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('sub_regimes', JSONB, server_default='{}'),
        sa.Column('indicators', JSONB, server_default='{}'),
        sa.Column('description', sa.Text()),
    )
    op.create_index('idx_regime_ts', 'regime_states', ['timestamp'])

    # Regime Transitions
    op.create_table(
        'regime_transitions',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('from_regime', sa.String(50), nullable=False),
        sa.Column('to_regime', sa.String(50), nullable=False),
        sa.Column('transition_date', sa.DateTime(), nullable=False),
        sa.Column('confidence', sa.Float()),
        sa.Column('trigger_factors', JSONB, server_default='{}'),
    )


def downgrade():
    op.drop_table('regime_transitions')
    op.drop_table('regime_states')
    op.drop_table('alert_triggers')
    op.drop_table('alerts')
    op.drop_table('event_impacts')
    op.drop_table('economic_events')
    op.drop_table('macro_data_points')
    op.drop_table('macro_series')
    op.drop_table('market_data_daily')
    op.drop_table('market_data')