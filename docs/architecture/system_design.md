# AI Investment Intelligence & Autonomous Trading System
## Documento de Diseño Técnico de Arquitectura (Configuración Particular)

---

### 1. Resumen Ejecutivo y Perfil del Inversor
* **Residencia Fiscal**: España (sujeto a normativa IRPF, Ley 35/2006, criterio FIFO, regla de los 2 meses y control de Modelos 720/721).
* **Capital Inicial**: 10.000 € – 25.000 € (base de cálculo: 20.000 €).
* **Perfil**: Equilibrado (crecimiento patrimonial con control estricto de riesgos).
* **Horizonte**: Combinación de inversión a largo plazo y trading táctico.
* **Autonomía**: Progresiva (1. Análisis → 2. Simulación → 3. Paper Trading → 4. Operativa Real Autorizada → 5. Autonomía Limitada).
* **Restricciones V1**: Sin apalancamiento, sin derivados, sin futuros, sin cortos, sin intradía de alta frecuencia.

---

### 2. Distribución Inicial de Referencia (Simulación de Capital)
* **50 % Inversión a Largo Plazo (Core)**: ETFs diversificados globales (UCITS) y acciones Quality/Moat (10.000 € base).
* **15 % Trading Táctico (Satélite)**: Swing trading, momentum y trend following sobre acciones y ETFs sectoriales líquidos (3.000 € base).
* **10 % Criptoactivos**: 70% Bitcoin (BTC) y 30% Ethereum (ETH) en mercado Spot (2.000 € base).
* **25 % Liquidez Activa Defensiva**: Saldo remunerado EUR o ETFs monetarios (XEON / Letras) para amortiguar volatilidad y aprovechar correcciones (5.000 € base).

---

### 3. Arquitectura de Motores Desacoplados
El sistema se compone de dos motores analíticos independientes y un módulo cripto especializado, gobernados por un motor central de riesgo soberano:
1. **Investment Engine (A)**: Centrado en asignación estratégica, rebalanceo por bandas ($\pm 5\%$), screener de calidad (ROIC $> 15\%$, Deuda/EBITDA $< 2.5$) y DCA dinámico.
2. **Trading Engine (B)**: Swing trading y momentum, rupturas de Donchian de 20 periodos, filtros de medias (EMA 200) y trailing stops basados en ATR ($2 \times \text{ATR}$).
3. **Crypto Module (C)**: MVRV Z-Score, múltiplos de Mayer, seguimiento de ciclos halving y flujos en exchanges para BTC y ETH.
4. **Motor Central e Independiente de Riesgo**: Jerárquicamente superior con poder de veto inmutable.

```
       [Fuentes de Datos: Yahoo, FRED, FMP, CCXT]
                           │
                           ▼
              [TimescaleDB + Redis 7+]
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
[Investment Engine] [Trading Engine]   [Crypto Module]
  (Largo Plazo)     (Swing/Momentum)      (BTC / ETH)
        │                  │                  │
        └──────────────────┬──────────────────┘
                           ▼
           [MOTOR CENTRAL DE RIESGO SOBERANO]
          (0,25-0,5% riesgo/trade | Max 1,5% agreg.)
          (Max 1% diario | Max 2% sem | Stop DD 10%)
                           │
                           ▼
              [OMS & Autonomy Gate]
        (1: Analista | 2: Supervisado | 3: Autónomo)
                           │
          ┌────────────────┴────────────────┐
          ▼                                 ▼
[Interactive Brokers (IBKR)]       [Kraken Exchange]
   (Bolsa, ETFs, Liquidez)            (BTC / ETH Spot)
```

---

### 4. Modelo de Riesgo Matemático y Parámetros vinculantes
* **Riesgo por Operación**: 0,25 % – 0,50 % del patrimonio total (50 € a 100 € sobre 20.000 €).
* **Riesgo Agregado Abierto**: Máximo 1,5 % (máx 300 € en riesgo simultáneo).
* **Pérdida Máxima Diaria**: 1,0 % (200 €). Si se alcanza, parada de nuevas órdenes por el resto de la sesión.
* **Pérdida Máxima Semanal**: 2,0 % (400 €). Si se alcanza, parada de nuevas operaciones durante la semana.
* **Drawdown de Revisión (8 %)**: Alerta crítica en el dashboard y reducción automática del tamaño de posición al 50%.
* **Drawdown de Parada / Circuit Breaker (10 %)**: Congelación total inmediata de nuevas operaciones y cancelación de órdenes abiertas.
* **Dimensionamiento Paramétrico**:
  $$N = \left\lfloor \frac{\text{Capital} \times R_{\%}}{P_e - SL} \right\rfloor$$
  *Nunca se ajusta el Stop Loss para ampliar el tamaño nominal de una orden.*

---

### 5. Comparativa y Selección de Brokers (Residencia Fiscal España)
1. **Interactive Brokers (IBKR)** (*Recomendado para Bolsa y ETFs*):
   * Entidad europea en Irlanda (`IBIE`), supervisada por el Banco Central de Irlanda, garantía ICF (20.000 €).
   * Tarifa *Tiered* con costes desde 1,25 € por operación en Europa y 0,35 $ en EE.UU.
   * Conexión oficial y automatizable mediante `ib_async` sobre `IB Gateway` headless en contenedor Docker.
   * Gestión fiscal manual en IRPF (criterio FIFO) y seguimiento del umbral de 50.000 € para el **Modelo 720**.
2. **Kraken** (*Recomendado para Criptomonedas*):
   * Registrado formalmente como `DASP` en el **Banco de España**.
   * Comisiones de 0,16 % Maker / 0,26 % Taker en Kraken Pro (un 60% más económico que Coinbase).
   * API REST y WebSockets v2 de latencia ultra-baja, con gestión estricta de permisos (Trade habilitado, Retiradas/Transferencias bloqueadas por diseño).
   * Registro FIFO en IRPF y seguimiento del umbral de 50.000 € para el **Modelo 721**.
3. **Coinbase Advanced** (*Alternativa de Respaldo*):
   * Registrado en Banco de España, pero con comisiones sensiblemente más elevadas (0,40 % / 0,60 %). Queda como canal secundario de redundancia.

---

### 6. Roadmap por Etapas de Autonomía
1. **Etapa 1: Análisis**: Solo lectura, normalización de datos, cálculo de scoring 0-100 y radar de oportunidades.
2. **Etapa 2: Simulación**: Backtesting multianual con Walk-Forward, Monte Carlo y comisiones reales modeladas.
3. **Etapa 3: Paper Trading**: Entorno virtual con cotizaciones en vivo y ejecución simulada con slippage.
4. **Etapa 4: Operativa Real Autorizada**: Ejecución en brokers reales con confirmación humana expresa previa (2FA / Telegram).
5. **Etapa 5: Autonomía Limitada**: Ejecución automática de estrategias validadas bajo presupuesto fijo y conmutador de emergencia (*kill switch*).
