# CHANGELOG
Todas las modificaciones notables de este proyecto serán documentadas en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/), y este proyecto se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [0.2.0] - 2026-11-09
### Añadido (Sprint 002 - Market Intelligence & Entorno Local)
* **Entorno de Desarrollo Local Operativo en PC Principal (Ryzen 9 3950X / RTX 3090)**:
  * Instalación de Python 3.12.10 vía `winget` en Windows 11.
  * Creación del entorno virtual `.venv` dentro de la carpeta del proyecto.
  * Instalación de todas las dependencias de producción y desarrollo.
  * Generación de `.env` a partir de `.env.example`.
  * Claves SSH generadas y protegidas para futura conexión a servidores Cloud.
* **Módulo de Inteligencia de Mercado (`src/services/market_data/`)**:
  * **Interfaz abstracta `BaseMarketDataCollector`**: Contrato canónico para todos los conectores de datos de mercado (`base.py`).
  * **DTOs y Schemas Pydantic**: `OHLCVBarDTO`, `QuoteDTO`, `MacroObservationDTO` para normalización de datos entre fuentes (`schemas.py`).
  * **Yahoo Finance Collector** (`yahoo_collector.py`): Conector asíncrono para acciones, ETFs e índices globales vía `yfinance`. Soporta velas diarias, horarias y semanales con validación de datos y conversión de zonas horarias a UTC.
  * **Crypto Data Collector** (`crypto_collector.py`): Conector asíncrono para criptomonedas Spot (BTC/EUR, ETH/EUR) vía `ccxt` con Kraken como exchange principal. Incluye fallback automático a pares USDT si EUR no está disponible.
  * **FRED Macro Collector** (`fred_collector.py`): Conector para indicadores macroeconómicos de la Reserva Federal (St. Louis FRED API). Series monitorizadas: FEDFUNDS (tipos de interés), T10Y2Y (curva de rendimientos), CPIAUCSL (inflación CPI), UNRATE (desempleo). Incluye valores de referencia baseline si no se dispone de API key.
  * **MarketDataService** (`market_data_service.py`): Orquestador central que coordina los 3 conectores, gestiona el registro automático de activos en la base de datos, persiste velas OHLCV sin duplicados y genera un resumen consolidado del entorno de mercado multiactivo (4 compartimentos + macro).
* **Modelo de Datos `MacroIndicator`** (`src/models/macro.py`):
  * Nueva tabla relacional para series temporales macroeconómicas con índice compuesto único `(series_id, period_date)`.
  * Registrado en `src/models/__init__.py`.
* **Nuevos Endpoints REST FastAPI** (`src/api/v1/endpoints/market_data.py`):
  * `GET /api/v1/market-data/overview`: Visión consolidada de cotizaciones de referencia de los 4 compartimentos (Core/URTH, Táctico/QQQ, Cripto/BTC, Liquidez/XEON.DE) y snapshot macroeconómico.
  * `GET /api/v1/market-data/quote/{symbol}`: Cotización en tiempo real o EOD de cualquier activo.
  * `GET /api/v1/market-data/history/{symbol}`: Consulta de velas OHLCV históricas almacenadas en base de datos.
  * `POST /api/v1/market-data/sync`: Sincronización bajo demanda de datos históricos de un activo y/o indicadores macro.
* **Dependencias de Datos de Mercado** (`requirements.txt`):
  * `yfinance>=1.8.0`: Yahoo Finance para renta variable y ETFs.
  * `ccxt>=4.5.64`: Librería unificada de exchanges de criptomonedas.
  * `pandas>=2.2.0` y `numpy>=2.0.0`: Análisis cuantitativo y manipulación de series temporales.
* **Tests Automatizados** (`tests/test_market_data.py`):
  * `test_yahoo_collector_mocked`: Verificación de parseo de datos de Yahoo Finance con ticker simulado.
  * `test_crypto_collector_mocked`: Verificación de parseo de velas CCXT con candles simulados.
  * `test_fred_collector_fallback`: Verificación de valores baseline macroeconómicos sin API key.
  * `test_market_data_service_db_sync`: Test de integración de persistencia en BD (inserción, actualización sin duplicados y sincronización macro).
  * `test_api_market_data_endpoints`: Test de integración de los endpoints REST de Market Data.
  * **Total: 19/19 tests pasando exitosamente** (14 originales + 5 nuevos).

### Notas sobre Oracle Cloud Infrastructure (OCI)
* Se intentó crear una instancia Always Free en la región de Madrid (`eu-madrid-1`):
  * **VM.Standard.A1.Flex (ARM Ampere)**: Error `Out of capacity` en 4 OCPUs/24 GB y también en 2 OCPUs/12 GB.
  * **VM.Standard.E2.1.Micro (AMD x86)**: Error `Out of capacity` igualmente.
  * **Conclusión**: La región de Madrid tiene el cupo de máquinas gratuitas agotado. Se evaluará reintentar en otro momento o utilizar Google Cloud Platform (GCP) Always Free como alternativa.
  * Se documentó el proceso completo de creación de cuenta y configuración de VM como referencia futura.

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
