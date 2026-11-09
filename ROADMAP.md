# ROADMAP DE DESARROLLO
## AI Investment Intelligence Platform

---

## 🗺️ Visión General de Fases

| Fase | Título | Objetivo Principal | Estado |
| :---: | :--- | :--- | :---: |
| **Fase 1** | **Foundation & Design** | Arquitectura, backend FastAPI, PostgreSQL, Docker Compose, Risk Engine base, tests y estrategia Cloud Free Tier | ✅ **COMPLETADO** |
| **Fase 2** | **Market Intelligence** | Conectores oficiales (FRED, Yahoo, CCXT), normalizadores, DTOs, servicio central y endpoints REST | ✅ **COMPLETADO** |
| **Fase 3** | **Investment Engine** | Screener fundamental de Calidad (ROIC, Deuda, Moat), asignación de ETFs y DCA dinámico | 🔜 Siguiente |
| **Fase 4** | **Trading Engine** | Estrategias cuantitativas (Donchian, Momentum, Swing), trailing stops ATR y backtesting | Pendiente |
| **Fase 5** | **Crypto Engine** | Métricas on-chain BTC/ETH (MVRV, Mayer Multiple, Halving cycles) y monitoreo 24/7 | Pendiente |
| **Fase 6** | **Risk Engine Hardening** | Circuit breakers avanzados, stress testing, control de correlaciones y VaR | Pendiente |
| **Fase 7** | **Paper Trading** | Simulador de órdenes con comisiones y slippage real, carteras virtuales y validación | Pendiente |
| **Fase 8** | **Broker Integration** | Conexión en modo lectura y conciliación con Interactive Brokers y Kraken | Pendiente |
| **Fase 9** | **Cloud Production (Free Tier)** | Despliegue en Cloud Always Free 24/7 (OCI / GCP), backups hacia el NAS Synology | Pendiente |
| **Fase 10** | **Autonomía Limitada** | Nivel 4 de autonomía activa con límites de riesgo blindados y kill switch | Pendiente |

---

## 📋 Detalle de Sprints

### SPRINT 001 — Foundation Setup & Core Architecture ✅
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
* **Estado**: ✅ Completado. 14/14 tests pasando.

---

### SPRINT 002 — Market Intelligence & Entorno Local ✅
* **Objetivo**: Implementar los conectores oficiales de datos de mercado multiactivo (renta variable, cripto y macroeconomía), crear el servicio central de orquestación con persistencia en BD y exponer endpoints REST de inteligencia de mercado. Configurar el entorno de desarrollo local en el PC principal.
* **Entregables en Repositorio**:
  1. Instalación y configuración del entorno Python 3.12 local en Windows 11 con `.venv` autocontenido.
  2. Interfaz abstracta `BaseMarketDataCollector` con contrato canónico (`src/services/market_data/base.py`).
  3. DTOs normalizados: `OHLCVBarDTO`, `QuoteDTO`, `MacroObservationDTO` (`src/services/market_data/schemas.py`).
  4. Yahoo Finance Collector para acciones, ETFs e índices globales (`src/services/market_data/yahoo_collector.py`).
  5. Crypto Data Collector vía CCXT/Kraken para BTC y ETH en EUR (`src/services/market_data/crypto_collector.py`).
  6. FRED Macro Collector para indicadores de la Reserva Federal: FEDFUNDS, T10Y2Y, CPI y desempleo (`src/services/market_data/fred_collector.py`).
  7. Servicio orquestador `MarketDataService` con registro automático de activos, persistencia sin duplicados y generación de resumen de mercado consolidado (`src/services/market_data/market_data_service.py`).
  8. Modelo de datos `MacroIndicator` para series temporales macroeconómicas (`src/models/macro.py`).
  9. Nuevos endpoints REST: `/market-data/overview`, `/market-data/quote/{symbol}`, `/market-data/history/{symbol}`, `/market-data/sync`.
  10. 5 tests nuevos de Market Intelligence (`tests/test_market_data.py`): conectores mockeados, fallback macro, integración con BD y endpoints REST.
* **Estado**: ✅ Completado. 19/19 tests pasando (14 originales + 5 nuevos).

---

### SPRINT 003 — Investment Engine (Planificado)
* **Objetivo**: Implementar el motor de inversión a largo plazo (Compartimento Core 50%) con screener fundamental de calidad, scoring 0-100, monitorización de ETFs globales UCITS y lógica de DCA dinámico adaptativo.
* **Entregables Previstos**:
  1. Screener de calidad fundamental: ROIC > 15%, Deuda/EBITDA < 2.5, Free Cash Flow positivo, Moat cualitativo.
  2. Scoring cuantitativo 0-100 para cada activo candidato.
  3. Monitorización de ETFs Core: URTH (MSCI World), SWRD (MSCI World EUR Acc), EIMI (Emergentes), AGG (Bonos globales).
  4. Lógica de DCA dinámico: ajuste de aportación periódica según nivel de valoración relativa del mercado.
  5. Integración con el Risk Engine para validación de cualquier propuesta de compra.
  6. Tests automatizados del screener y del DCA.
* **Estado**: 🔜 Siguiente sprint.
