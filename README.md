# AI Investment Intelligence & Autonomous Trading System

Plataforma integral e institucional para la gestión, análisis cuantitativo multiactivo, monitorización de riesgos y ejecución algorítmica de carteras de inversión personales.

---

## 🎯 Objetivo del Sistema

Construir un ecosistema autónomo y seguro capaz de:
1. **Analizar múltiples mercados** de forma continua (Bolsa, ETFs, Criptomonedas, Renta Fija, Materias Primas).
2. **Generar scoring cuantitativo (0 a 100)** combinando análisis técnico, fundamental, macroeconómico y de sentimiento.
3. **Validar estrategias rigurosamente** mediante backtesting multianual con Walk-Forward y simulaciones Monte Carlo, evitando el sobreajuste y sesgos retrospectivos.
4. **Gestionar el riesgo de forma soberana** con límites estrictos de drawdown, tamaño de posición y conmutador de emergencia (*kill switch*).
5. **Operar con tres niveles de autonomía** (Nivel 1: Analista | Nivel 2: Operador Supervisado | Nivel 3: Gestor Autónomo Limitado).
6. **Cumplir la normativa fiscal española** (criterio FIFO, regla de los dos meses, seguimiento para IRPF y Modelos 720/721).

---

## 🏗️ Arquitectura y Tecnologías Principales

* **Backend & Quant Engine**: Python 3.12+, FastAPI, Pydantic v2, Polars, VectorBT, TA-Lib.
* **Persistencia y Caché**: PostgreSQL 16 + TimescaleDB (Hypertables para series temporales de alta velocidad) y Redis 7+.
* **Conectores de Datos**: FRED API (Macro), CCXT (Cripto), Yahoo Finance / FMP (Renta Variable / Fundamentales), RSS & LLM (Sentimiento).
* **Conectores de Brokers**: Interactive Brokers (vía `ib_async` y `IB Gateway`), Kraken API, Binance API.
* **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Shadcn/UI y TradingView Lightweight Charts.
* **Contenedores**: Docker & Docker Compose con proxy inverso seguro (Caddy con HTTPS automático).

---

## 📚 Documentación

* **[Documento Maestro de Arquitectura y Especificación Técnica](docs/architecture/system_design.md)**: Análisis detallado de diseño, comparativa de brokers, motores analíticos y fiscalidad española.

---

## 🗺️ Roadmap de Desarrollo

- [x] **Fase 1: Diseño Funcional y Arquitectura Maestra**
- [ ] **Fase 2: Pipeline de Ingesta de Datos y Persistencia TimescaleDB**
- [ ] **Fase 3: Motor Cuantitativo y Scoring 0-100 + Dashboard Inicial (MVP)**
- [ ] **Fase 4: Motor de Backtesting y Validación Libre de Sesgos**
- [ ] **Fase 5: Conexión de Cuentas en Modo Lectura (Nivel 1: Analista)**
- [ ] **Fase 6: Paper Trading Simulator y Gestión de Órdenes**
- [ ] **Fase 7: Ejecución Real Supervisada (Nivel 2: Operador Supervisado)**
- [ ] **Fase 8: Autonomía Limitada y Monitoreo Continuo (Nivel 3)**
