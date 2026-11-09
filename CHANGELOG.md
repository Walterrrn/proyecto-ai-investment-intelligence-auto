# CHANGELOG
Todas las modificaciones notables de este proyecto serán documentadas en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/), y este proyecto se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [0.1.0] - 2026-11-09
### Añadido (Sprint 001 - Foundation Setup)
* **Arquitectura Base**:
  * Estructura modular y limpia del proyecto bajo `src/` y `tests/`.
  * Configuración centralizada con Pydantic Settings y validaciones estrictas (`src/core/config.py`).
  * Conexión asíncrona a base de datos con SQLAlchemy 2.0 y soporte para PostgreSQL/TimescaleDB y SQLite (`src/core/database.py`).
  * Configuración de logging estructurado (`src/core/telemetry.py`).
  * Utilidades de enmascaramiento seguro de credenciales (`src/core/security.py`).
* **Modelos de Datos Relacionales y Series Temporales**:
  * `Asset`: Catálogo maestro de activos (acciones, ETFs, cripto, bonos, liquidez) y clasificación por compartimentos de asignación (`src/models/asset.py`).
  * `MarketDataOHLCV`: Esquema de velas históricas e intradía (`src/models/market_data.py`).
  * `PortfolioPosition` y `PortfolioSnapshot`: Seguimiento de cartera, precio medio de compra, valoración de mercado y PnL (`src/models/portfolio.py`).
  * `Signal`: Entidad de hipótesis cuantitativas de inversión con precios de entrada, stop loss y horizonte temporal (`src/models/signal.py`).
  * `RiskSnapshot`: Telemetría de riesgo, pérdida diaria/semanal y estado de los circuit breakers (`src/models/risk.py`).
  * `DecisionAuditLog`: Registro inmutable de justificación de decisiones y validaciones de riesgo (`src/models/audit.py`).
* **Servicios de Negocio y Riesgo**:
  * `PortfolioService`: Cálculo de distribución de capital en los 4 compartimentos de referencia (50% Core, 15% Táctico, 10% Cripto, 25% Liquidez) y detección de bandas de rebalanceo (`src/services/portfolio_service.py`).
  * `RiskService`: Motor soberano con validación pre-trade, dimensionamiento matemático de posición ($N = \lfloor \frac{\text{Capital} \times R_{\%}}{P_e - SL} \rfloor$) y circuit breakers duros por drawdown del 10% y pérdida diaria del 1.0% (`src/services/risk_service.py`).
* **API REST FastAPI**:
  * `/api/v1/health`: Estado del sistema, conectividad de base de datos y confirmación del modo `ANALYST_ONLY`.
  * `/api/v1/assets`: Listado y filtrado de activos.
  * `/api/v1/portfolio/allocation`: Desglose consolidado de capital y reservas.
  * `/api/v1/signals`: Consulta de señales generadas por los motores analíticos.
  * `/api/v1/risk/limits`: Parámetros soberanos de riesgo inmutables.
  * `/api/v1/risk/calculate-sizing`: Endpoint de cálculo paramétrico de tamaño de orden.
* **Infraestructura**:
  * `docker-compose.yml`: Orquestación de backend FastAPI, PostgreSQL 16 con extensión TimescaleDB y Redis 7+.
  * `Dockerfile`: Imagen base de backend en Python 3.12-slim.
  * `.env.example`: Plantilla de variables de entorno con valores seguros por defecto.
  * `pyproject.toml` y `requirements.txt`: Dependencias bloqueadas y configuración de Pytest.
* **Tests Automatizados**:
  * 14 tests unitarios y de integración pasando con éxito (`tests/test_health.py`, `tests/test_config.py`, `tests/test_portfolio_allocations.py`, `tests/test_risk_engine.py`).
* **Documentación**:
  * `ARCHITECTURE.md`: Documento maestro de arquitectura y topología hardware (PC Ryzen 9 3950X / RTX 3090, NAS DS218j, Cloud VPS).
  * `ROADMAP.md`: Hoja de ruta de 10 fases y detalle del Sprint 001.
  * `DECISIONS.md`: Registro de decisiones de arquitectura (ADR).
  * `SECURITY.md`: Política de seguridad, aislamiento de secretos y reglas de no-ejecución.
  * `docs/guides/windows11_setup.md`: Guía de puesta en marcha paso a paso en Windows 11.
