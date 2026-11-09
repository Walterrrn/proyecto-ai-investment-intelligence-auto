# Esquema de Base de Datos y Modelo de Datos
## PostgreSQL 16 + TimescaleDB

Este documento contiene la definición completa de tipos y DDL para el almacenamiento de datos relacionales y de series temporales de la plataforma.

---

```sql
-- Habilitar extensión TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 1. Catálogo Maestro de Activos
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    isin VARCHAR(12) UNIQUE,
    name VARCHAR(100) NOT NULL,
    asset_class VARCHAR(20) NOT NULL, -- 'EQUITY', 'ETF', 'CRYPTO', 'FIXED_INCOME', 'CASH'
    allocation_bucket VARCHAR(20) NOT NULL, -- 'LONG_TERM', 'TACTICAL', 'CRYPTO', 'LIQUIDITY'
    currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
    exchange VARCHAR(30) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Cotizaciones y Velas OHLCV (TimescaleDB Hypertable)
CREATE TABLE market_data_ohlcv (
    timestamp TIMESTAMPTZ NOT NULL,
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    timeframe VARCHAR(5) NOT NULL, -- '1m', '1h', '1d', '1w'
    open NUMERIC(16, 6) NOT NULL,
    high NUMERIC(16, 6) NOT NULL,
    low NUMERIC(16, 6) NOT NULL,
    close NUMERIC(16, 6) NOT NULL,
    volume NUMERIC(24, 6) NOT NULL,
    vwap NUMERIC(16, 6),
    PRIMARY KEY (timestamp, asset_id, timeframe)
);
SELECT create_hypertable('market_data_ohlcv', 'timestamp', if_not_exists => TRUE);
ALTER TABLE market_data_ohlcv SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'asset_id, timeframe'
);
SELECT add_compression_policy('market_data_ohlcv', INTERVAL '30 days');

-- 3. Indicadores Macroeconómicos (TimescaleDB Hypertable)
CREATE TABLE macro_indicators (
    timestamp TIMESTAMPTZ NOT NULL,
    indicator_code VARCHAR(30) NOT NULL, -- 'FEDFUNDS', 'T10Y2Y', 'CPIAUCSL', 'EURIBOR_12M'
    value NUMERIC(12, 4) NOT NULL,
    source VARCHAR(20) NOT NULL,
    PRIMARY KEY (timestamp, indicator_code)
);
SELECT create_hypertable('macro_indicators', 'timestamp', if_not_exists => TRUE);

-- 4. Métricas On-Chain Cripto (TimescaleDB Hypertable)
CREATE TABLE crypto_metrics (
    timestamp TIMESTAMPTZ NOT NULL,
    asset_id INTEGER NOT NULL REFERENCES assets(id),
    mvrv_zscore NUMERIC(8, 4),
    mayer_multiple NUMERIC(8, 4),
    exchange_netflow NUMERIC(18, 6),
    PRIMARY KEY (timestamp, asset_id)
);
SELECT create_hypertable('crypto_metrics', 'timestamp', if_not_exists => TRUE);

-- 5. Posiciones de Cartera Consolidadas
CREATE TABLE portfolio_positions (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id),
    broker VARCHAR(30) NOT NULL, -- 'IBKR', 'KRAKEN'
    allocation_bucket VARCHAR(20) NOT NULL, -- 'LONG_TERM', 'TACTICAL', 'CRYPTO', 'LIQUIDITY'
    quantity NUMERIC(18, 8) NOT NULL,
    avg_buy_price_eur NUMERIC(16, 4) NOT NULL,
    current_price_eur NUMERIC(16, 4) NOT NULL,
    market_value_eur NUMERIC(16, 4) GENERATED ALWAYS AS (quantity * current_price_eur) STORED,
    unrealized_pnl_eur NUMERIC(16, 4) GENERATED ALWAYS AS (quantity * (current_price_eur - avg_buy_price_eur)) STORED,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. Órdenes y Lifecycle OMS
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id INTEGER NOT NULL REFERENCES assets(id),
    engine_source VARCHAR(20) NOT NULL, -- 'INVESTMENT', 'TRADING', 'CRYPTO'
    broker VARCHAR(30) NOT NULL, -- 'IBKR', 'KRAKEN', 'PAPER'
    side VARCHAR(4) NOT NULL, -- 'BUY', 'SELL'
    order_type VARCHAR(10) NOT NULL, -- 'MARKET', 'LIMIT', 'STOP_LOSS'
    quantity NUMERIC(18, 8) NOT NULL,
    limit_price_eur NUMERIC(16, 4),
    stop_loss_price_eur NUMERIC(16, 4),
    risk_amount_eur NUMERIC(10, 2) NOT NULL,
    risk_pct_portfolio NUMERIC(5, 4) NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'PENDING_APPROVAL', 'APPROVED', 'SUBMITTED', 'FILLED', 'REJECTED', 'CANCELLED'
    rejection_reason TEXT,
    human_approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. Telemetría de Riesgo de Cartera (TimescaleDB Hypertable)
CREATE TABLE risk_snapshots (
    timestamp TIMESTAMPTZ NOT NULL PRIMARY KEY,
    total_wealth_eur NUMERIC(14, 2) NOT NULL,
    invested_equity_eur NUMERIC(14, 2) NOT NULL,
    liquidity_eur NUMERIC(14, 2) NOT NULL,
    daily_pnl_pct NUMERIC(6, 4) NOT NULL,
    weekly_pnl_pct NUMERIC(6, 4) NOT NULL,
    current_drawdown_pct NUMERIC(6, 4) NOT NULL,
    open_risk_pct NUMERIC(6, 4) NOT NULL,
    circuit_breaker_active BOOLEAN NOT NULL DEFAULT FALSE
);
SELECT create_hypertable('risk_snapshots', 'timestamp', if_not_exists => TRUE);

-- 8. Lotes Fiscales FIFO (IRPF España)
CREATE TABLE tax_fifo_lots (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id),
    buy_order_id UUID REFERENCES orders(id),
    acquisition_date DATE NOT NULL,
    initial_quantity NUMERIC(18, 8) NOT NULL,
    remaining_quantity NUMERIC(18, 8) NOT NULL,
    unit_cost_basis_eur NUMERIC(16, 4) NOT NULL,
    total_cost_eur NUMERIC(14, 2) NOT NULL,
    is_exhausted BOOLEAN NOT NULL DEFAULT FALSE
);

-- 9. Explicabilidad y Auditoría de Decisiones Cuantitativas
CREATE TABLE decision_audit_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    engine VARCHAR(20) NOT NULL,
    asset_symbol VARCHAR(20) NOT NULL,
    action_proposed VARCHAR(20) NOT NULL,
    quantitative_score NUMERIC(5, 2) NOT NULL,
    macro_regime VARCHAR(30) NOT NULL,
    risk_check_passed BOOLEAN NOT NULL,
    decision_rationale JSONB NOT NULL,
    execution_result VARCHAR(30)
);
```
