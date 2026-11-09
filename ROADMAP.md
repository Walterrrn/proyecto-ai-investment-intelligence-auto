# ROADMAP DE DESARROLLO
## AI Investment Intelligence Platform

---

## 🗺️ Visión General de Fases

| Fase | Título | Objetivo Principal | Estado |
| :---: | :--- | :--- | :---: |
| **Fase 1** | **Foundation** | Arquitectura, backend FastAPI, PostgreSQL, Docker Compose, Risk Engine base y tests | **EN PROGRESO (Sprint 001 Completado)** |
| **Fase 2** | **Market Intelligence** | Conectores oficiales (FRED, Yahoo, FMP, CCXT), normalizadores y pipeline EOD | Pendiente |
| **Fase 3** | **Investment Engine** | Screener fundamental de Calidad (ROIC, Deuda, Moat), asignación de ETFs y DCA dinámico | Pendiente |
| **Fase 4** | **Trading Engine** | Estrategias cuantitativas (Donchian, Momentum, Swing), trailing stops ATR y backtesting | Pendiente |
| **Fase 5** | **Crypto Engine** | Métricas on-chain BTC/ETH (MVRV, Mayer Multiple, Halving cycles) y monitoreo 24/7 | Pendiente |
| **Fase 6** | **Risk Engine Hardening** | Circuit breakers avanzados, stress testing, control de correlaciones y VaR | Pendiente |
| **Fase 7** | **Paper Trading** | Simulador de órdenes con comisiones y slippage real, carteras virtuales y validación | Pendiente |
| **Fase 8** | **Broker Integration** | Conexión en modo lectura y conciliación con Interactive Brokers y Kraken | Pendiente |
| **Fase 9** | **Cloud Production** | Despliegue en VPS cloud 24/7, Prometheus/Grafana, backups hacia el NAS Synology | Pendiente |
| **Fase 10** | **Autonomía Limitada** | Nivel 4 de autonomía activa con límites de riesgo blindados y kill switch | Pendiente |

---

## 📋 Detalle de Sprints (Fase 1: Foundation)

### SPRINT 001 — Foundation Setup & Core Architecture (Completado)
* **Objetivo**: Establecer los cimientos del backend en Python 3.12 con FastAPI, el modelo de datos relacional/series temporales, Docker Compose, la configuración de entornos protegida y el motor soberano de riesgo paramétrico en modo solo lectura (`ANALYST_ONLY`).
* **Tareas Realizadas**:
  1. Definición y configuración de `Settings` con validación estricta en Pydantic (`src/core/config.py`).
  2. Implementación de conexión asíncrona a base de datos (`src/core/database.py`).
  3. Creación de modelos de datos principales: `Asset`, `PortfolioPosition`, `MarketDataOHLCV`, `Signal`, `RiskSnapshot`, `DecisionAuditLog`.
  4. Implementación del servicio de asignación de capital y distribución por compartimentos (`src/services/portfolio_service.py`).
  5. Implementación del motor matemático soberano de dimensionamiento de posición y circuit breakers (`src/services/risk_service.py`).
  6. Exposición de endpoints REST documentados (`/health`, `/assets`, `/portfolio/allocation`, `/signals`, `/risk/limits`, `/risk/calculate-sizing`).
  7. Suite de 14 tests automatizados con Pytest (`tests/`).
  8. Configuración de contenedor Docker Compose con PostgreSQL 16 + TimescaleDB y Redis 7+.
* **Archivos Afectados**:
  * `src/core/config.py`, `src/core/database.py`, `src/core/security.py`, `src/core/telemetry.py`
  * `src/models/base.py`, `src/models/asset.py`, `src/models/market_data.py`, `src/models/portfolio.py`, `src/models/signal.py`, `src/models/risk.py`, `src/models/audit.py`
  * `src/services/portfolio_service.py`, `src/services/risk_service.py`
  * `src/api/main.py`, `src/api/v1/api.py`, `src/api/v1/endpoints/*.py`
  * `docker-compose.yml`, `Dockerfile`, `.env.example`, `requirements.txt`, `pyproject.toml`
  * `tests/conftest.py`, `tests/test_health.py`, `tests/test_config.py`, `tests/test_portfolio_allocations.py`, `tests/test_risk_engine.py`
* **Criterios de Aceptación**:
  * [x] Endpoint `/health` operativo y reportando modo `ANALYST_ONLY` con ejecución real deshabilitada.
  * [x] Modelos de datos creados y validados.
  * [x] Cálculo matemático de position sizing probado y verificado.
  * [x] 100% de la suite de tests pasando (14/14 tests OK).
* **Resultado**: Base de código robusta, modular, tipada y testeada con éxito.
* **Riesgos Pendientes**:
  * Migraciones formales de base de datos con Alembic para entornos de producción.
* **Próximo Sprint (Sprint 002)**:
  * Ingesta de datos de mercado oficiales (Fase 2): Conectores para FRED API (Macro) y Yahoo Finance (Históricos EOD de Acciones y ETFs) con persistencia en la base de datos.
