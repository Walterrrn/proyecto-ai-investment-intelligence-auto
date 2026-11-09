# ROADMAP DE DESARROLLO
## AI Investment Intelligence Platform

---

## 🗺️ Visión General de Fases

| Fase | Título | Objetivo Principal | Estado |
| :---: | :--- | :--- | :---: |
| **Fase 1** | **Foundation & Design** | Arquitectura, backend FastAPI, PostgreSQL, Docker Compose, Risk Engine base, tests y estrategia Cloud Free Tier | **COMPLETADO A NIVEL DE DISEÑO Y REPOSITORIO** |
| **Fase 2** | **Market Intelligence** | Conectores oficiales (FRED, Yahoo, FMP, CCXT), normalizadores y pipeline EOD | En espera de activación |
| **Fase 3** | **Investment Engine** | Screener fundamental de Calidad (ROIC, Deuda, Moat), asignación de ETFs y DCA dinámico | Pendiente |
| **Fase 4** | **Trading Engine** | Estrategias cuantitativas (Donchian, Momentum, Swing), trailing stops ATR y backtesting | Pendiente |
| **Fase 5** | **Crypto Engine** | Métricas on-chain BTC/ETH (MVRV, Mayer Multiple, Halving cycles) y monitoreo 24/7 | Pendiente |
| **Fase 6** | **Risk Engine Hardening** | Circuit breakers avanzados, stress testing, control de correlaciones y VaR | Pendiente |
| **Fase 7** | **Paper Trading** | Simulador de órdenes con comisiones y slippage real, carteras virtuales y validación | Pendiente |
| **Fase 8** | **Broker Integration** | Conexión en modo lectura y conciliación con Interactive Brokers y Kraken | Pendiente |
| **Fase 9** | **Cloud Production (Free Tier)** | Despliegue en Cloud Always Free 24/7 (OCI / GCP), backups hacia el NAS Synology | Pendiente |
| **Fase 10** | **Autonomía Limitada** | Nivel 4 de autonomía activa con límites de riesgo blindados y kill switch | Pendiente |

---

## 📋 Detalle de Sprints

### SPRINT 001 — Foundation Setup & Core Architecture (Completado en Repositorio)
* **Objetivo**: Establecer los cimientos del backend en Python 3.12 con FastAPI, el modelo de datos relacional/series temporales, Docker Compose, la configuración de entornos protegida, el motor soberano de riesgo paramétrico en modo solo lectura (`ANALYST_ONLY`) y el estudio técnico de viabilidad en capas gratuitas Cloud (AWS, GCP, Azure, Oracle Cloud).
* **Entregables en Repositorio**:
  1. Definición y configuración de `Settings` con validación estricta en Pydantic (`src/core/config.py`).
  2. Implementación de conexión asíncrona a base de datos (`src/core/database.py`).
  3. Creación de modelos de datos principales: `Asset`, `PortfolioPosition`, `MarketDataOHLCV`, `Signal`, `RiskSnapshot`, `DecisionAuditLog`.
  4. Implementación del servicio de asignación de capital y distribución por compartimentos (`src/services/portfolio_service.py`).
  5. Implementación del motor matemático soberano de dimensionamiento de posición y circuit breakers (`src/services/risk_service.py`).
  6. Exposición de endpoints REST documentados (`/health`, `/assets`, `/portfolio/allocation`, `/signals`, `/risk/limits`, `/risk/calculate-sizing`).
  7. Suite de 14 tests automatizados con Pytest (`tests/`) pasando al 100%.
  8. Configuración de contenedor Docker Compose con PostgreSQL 16 + TimescaleDB y Redis 7+.
  9. Estudio técnico de capas gratuitas Cloud 24/7 (`docs/architecture/cloud_free_tier_analysis.md`).
  10. Guía de instalación y puesta en marcha en Windows 11 (`docs/guides/windows11_setup.md`).
* **Estado Actual**:
  * Código congelado y documentado en GitHub.
  * Sin ejecuciones activas programadas para conservar créditos.
  * Preparado para que el usuario clone y ejecute en su PC cuando lo desee.
