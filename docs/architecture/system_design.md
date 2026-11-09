# AI Investment Intelligence & Autonomous Trading System
## Documento de Diseño de Arquitectura y Especificación Técnica

Este documento contiene la arquitectura técnica, modelo de datos, estrategia de conectividad y análisis regulatorio para la plataforma personal de inversión inteligente.

---

### Índice
1. [Visión General y Principios de Diseño](#1-visión-general-y-principios-de-diseño)
2. [Arquitectura del Sistema y Diagramas](#2-arquitectura-del-sistema-y-diagramas)
3. [Fuentes de Datos Financieros](#3-fuentes-de-datos-financieros)
4. [Análisis de Brokers y Exchanges (Enfoque España)](#4-análisis-de-brokers-y-exchanges-enfoque-españa)
5. [Stack Tecnológico Justificado](#5-stack-tecnológico-justificado)
6. [Estructura Modular y Flujo de Datos](#6-estructura-modular-y-flujo-de-datos)
7. [Motor de Puntuación Multifactor (0-100)](#7-motor-de-puntuación-multifactor-0-100)
8. [Niveles de Autonomía y Mecanismos de Seguridad](#8-niveles-de-autonomía-y-mecanismos-de-seguridad)
9. [Fiscalidad y Cumplimiento Normativo (España)](#9-fiscalidad-y-cumplimiento-normativo-españa)
10. [Estimación de Costes de Infraestructura](#10-estimación-de-costes-de-infraestructura)
11. [Matriz de Riesgos y Mitigación](#11-matriz-de-riesgos-y-mitigación)
12. [Especificación del MVP y Roadmap](#12-especificación-del-mvp-y-roadmap)

---

### 1. Visión General y Principios de Diseño
El sistema está concebido como una infraestructura institucional de inversión cuantitativa para patrimonio personal:
* **Soberanía del Motor de Riesgo**: Las decisiones del módulo de riesgo son inviolables. Ningún modelo probabilístico o de IA puede saltarse los límites de pérdida o exposición.
* **Seguridad Absoluta**: Aislamiento criptográfico de credenciales. Claves de API con permisos estrictos de trading sin posibilidad de retiradas o transferencias.
* **Neutralidad de Mercado**: Capacidad de rotar y asignar capital entre Renta Variable, Criptoactivos, Renta Fija y Materias Primas según el régimen macroeconómico. Mantener liquidez (Cash en EUR) es una posición activa prioritaria en regímenes desfavorables.

---

### 2. Arquitectura del Sistema y Diagramas

El sistema se estructura bajo una **Arquitectura Hexagonal Asíncrona (Ports & Adapters)** desplegada como un **Monolito Modular** en Docker Compose:

```
[Fuentes de Datos: Yahoo, FRED, FMP, CCXT]
              │
              ▼
   [Ingestion & Pipeline]
              │
              ▼
[TimescaleDB + PostgreSQL 16] ◄──► [Redis 7+ Caché & Kill-Switch]
              │
              ▼
   [Motor Cuantitativo & Scoring (0-100)]
              │
              ▼
    [Motor de Estrategias]
              │
              ▼
     [MOTOR DE RIESGO] (Soberano: Stop Loss, Sizing, Límites)
              │
              ▼
 [OMS / EMS: Niveles 1, 2, 3] ──► [Brokers: IBKR, Kraken, Binance]
              │
              ▼
 [FastAPI Gateway & Next.js 14 Dashboard]
```

---

### 3. Fuentes de Datos Financieros
* **Macroeconomía**: **FRED API** (Reserva Federal) + **BCE Data Portal** (100% oficiales y gratuitos para inflación, tipos de interés, M2, curvas de tipos).
* **Criptomonedas**: **CCXT** (biblioteca open source conectada en tiempo real a endpoints públicos de Kraken, Binance, Coinbase) + **DeFiLlama** (métricas on-chain, TVL, stablecoins gratuitas).
* **Renta Variable / ETFs**: **Yahoo Finance (`yfinance`)** para datos históricos y fin de día en fase inicial; complementado con **Financial Modeling Prep (FMP)** para estados financieros auditados, balances y ratios de valoración.
* **Noticias y Sentimiento**: Ingesta de feeds RSS financieros + análisis de sentimiento cualitativo mediante modelos LLM (ej. Gemini 1.5 Flash / GPT-4o-mini) con salida estructurada en JSON.

---

### 4. Análisis de Brokers y Exchanges (Enfoque España)
1. **Interactive Brokers (IBKR)** (*Recomendado*):
   * Dispone de API oficial probada (`ib_async` conectada a `IB Gateway`).
   * Sede europea en Irlanda (`IBIE`) regulada por el Banco Central de Irlanda y MiFID II.
   * Comisiones extremadamente bajas en acciones y ETFs europeos/americanos.
   * Requiere gestión fiscal manual en España (IRPF y eventual Modelo 720 si el saldo > 50.000 €).
2. **DEGIRO**: **Descartado para ejecución algorítmica**. No cuenta con API pública oficial para clientes minoristas; los métodos no oficiales se basan en scraping que violan sus condiciones de servicio y conllevan riesgo de bloqueo de cuenta.
3. **Trade Republic**: **Descartado para operativa automatizada**. No ofrece interfaz de programación de aplicaciones para trading sistemático.
4. **Kraken y Binance** (*Recomendados para Criptoactivos*):
   * Ambos registrados en el Banco de España para servicios de cambio y custodia.
   * APIs completas vía REST y WebSockets con soporte para claves API sin permisos de retirada.

---

### 5. Stack Tecnológico Justificado
* **Backend**: Python 3.12, FastAPI, Pydantic v2, Polars (procesamiento de datos a alta velocidad), VectorBT (backtesting multivariable) y Celery/ARQ con Redis para tareas en segundo plano.
* **Bases de Datos**: PostgreSQL 16 con extensión TimescaleDB (almacenamiento de series temporales de alta compresión y datos relacionales en una única instancia) + Redis 7 para estado en tiempo real.
* **Frontend**: Next.js 14 (React 19), TypeScript, Tailwind CSS, Shadcn/UI y gráficos financieros interactivos con TradingView Lightweight Charts.
* **Infraestructura**: Docker Compose, Caddy (Reverse Proxy con SSL automático), compatible con despliegue en servidor privado VPS (ej. Hetzner Cloud) o Mini-PC local.

---

### 6. Estructura de Directorios del Proyecto
```
proyecto-ai-investment-intelligence-auto/
├── docs/                      # Documentación de diseño, arquitectura y guías
│   └── architecture/
├── src/
│   ├── core/                  # Configuración global, seguridad, criptografía
│   ├── data_engine/           # Ingesta multifuente, normalizadores, pipelines
│   ├── quant_engine/          # Análisis técnico, fundamental, macro y scoring 0-100
│   ├── strategy_engine/       # Catálogo de estrategias de inversión cuantitativa
│   ├── backtest_engine/       # Simulación histórica, Walk-forward y Monte Carlo
│   ├── risk_engine/           # Validación pre-trade, dimensionamiento de posición, kill switch
│   ├── execution_engine/      # OMS/EMS, adaptadores IBKR/Kraken/Binance, paper trading
│   ├── portfolio_engine/      # Seguimiento consolidado de posiciones y NAV
│   ├── tax_engine/            # FIFO español, regla de 2 meses, reporte IRPF y 720/721
│   └── api/                   # API REST y WebSockets con FastAPI
├── ui/                        # Dashboard web profesional con Next.js y Tailwind CSS
├── tests/                     # Tests unitarios, integración y validación cuantitativa
├── docker-compose.yml         # Orquestación de servicios (API, DB, Redis, Gateway)
└── README.md
```

---

### 7. Fiscalidad y Cumplimiento Normativo (España)
* **Criterio FIFO**: Aplicación estricta de las directrices de la AEAT y consultas vinculantes de la DGT para la transmisión sucesiva de acciones y criptomonedas.
* **Regla de los Dos Meses**: Monitorización algorítmica para evitar la aplicación indebida de minusvalías cuando existan recompras de valores homogéneos en los dos meses previos o posteriores.
* **Modelos 720 y 721**: Alertas automáticas cuando el saldo custodiado en entidades en el extranjero (como IBKR en Irlanda o exchanges cripto foráneos) supere el umbral de 50.000 € a 31 de diciembre o en saldo medio trimestral.
* **Patrimonio Propio**: Exclusivamente enfocado a la gestión privada sin prestación de servicios a terceros ni captación de capital ajeno.

---

### 8. Fases de Desarrollo del Proyecto
* **Fase 1**: Diseño de arquitectura, esquemas relacionales/timescale y setup de proyecto.
* **Fase 2**: Pipeline de ingesta de datos financieros (FRED, Yahoo, CCXT) y persistencia.
* **Fase 3**: Motor analítico multifactor, cálculo de Score 0-100 y primer dashboard visual.
* **Fase 4**: Motor de Backtesting con Walk-Forward, Monte Carlo y filtros anti-sesgo.
* **Fase 5**: Conexión de brokers en modo sólo lectura (Nivel 1: Analista).
* **Fase 6**: Simulador de Paper Trading con slippage y comisiones reales.
* **Fase 7**: Nivel 2: Operador Supervisado con aprobación manual expresa.
* **Fase 8**: Nivel 3: Gestor Autónomo con límites estrictos de capital y parada de emergencia.
