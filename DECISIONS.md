# REGISTRO DE DECISIONES DE ARQUITECTURA (ADR)
## AI Investment Intelligence Platform

---

### ADR-001: Adopción de Monolito Modular Asíncrono frente a Microservicios Distribuidos
* **Fecha**: 2026-11-09
* **Estado**: Aceptado
* **Contexto**: Se requiere una plataforma de gestión patrimonial personal robusta, auditable y mantenible. Los microservicios introducen sobrecostes operativos (gestión de redes, serialización gRPC/JSON redundante, orquestación compleja y mayores requisitos de RAM).
* **Decisión**: Implementar un monolito modular en Python 3.12 con FastAPI y arquitectura hexagonal (Ports & Adapters). Cada dominio (`data_engine`, `investment_engine`, `trading_engine`, `crypto_module`, `risk_engine`, `execution_engine`) está estrictamente desacoplado mediante interfaces canónicas.
* **Consecuencias**: Despliegue simplificado en un solo host Docker Compose, latencia de comunicación prácticamente nula en memoria, transacciones locales ACID y reducción de costes de infraestructura a menos de 15-20 €/mes.

---

### ADR-002: Soberanía e Independencia del Motor de Riesgo (Risk Engine)
* **Fecha**: 2026-11-09
* **Estado**: Aceptado
* **Contexto**: Los modelos analíticos, cuantitativos y de lenguaje natural (LLM) operan sobre probabilidades y pueden producir alucinaciones o sobreajuste (*overfitting*). Si un motor de inversión tuviera permisos directos de ejecución, un fallo lógico podría arriesgar el capital.
* **Decisión**: El Risk Engine es completamente independiente y jerárquicamente superior. Los motores analíticos solo pueden proponer operaciones. El Risk Engine valida de forma matemática e inmutable que se cumplan las reglas: riesgo máximo por trade (0,25-0,50%), riesgo agregado (< 1,5%), pérdida diaria (< 1,0%) y drawdown (< 10%). Si alguna regla falla, la orden es vetada de inmediato.
* **Consecuencias**: Seguridad garantizada por diseño (*safety-by-design*). Ningún LLM ni modelo predictivo puede comprometer la solvencia de la cartera.

---

### ADR-003: Persistencia Híbrida con PostgreSQL 16 y Extensión TimescaleDB
* **Fecha**: 2026-11-09
* **Estado**: Aceptado
* **Contexto**: El sistema maneja simultáneamente datos relacionales complejos (activos, cuentas, lotes FIFO fiscales, auditoría) y series temporales de alta frecuencia (velas OHLCV, ticks, snapshots de riesgo de cartera).
* **Decisión**: Utilizar PostgreSQL 16 con la extensión **TimescaleDB**.
* **Consecuencias**: Una sola instancia de base de datos gestiona tanto las tablas relacionales como las *Hypertables* de series temporales con compresión columnar automática (> 85% de ahorro de disco), simplificando copias de seguridad y manteniendo transacciones ACID estándar.

---

### ADR-004: Topología Hardware Asimétrica (PC Principal + NAS + Cloud VPS)
* **Fecha**: 2026-11-09
* **Estado**: Aceptado
* **Contexto**: Se dispone de un PC potente (AMD Ryzen 9 3950X, GPU RTX 3090, Windows 11), un NAS Synology DS218j (512 MB RAM) y un futuro entorno Cloud VPS.
* **Decisión**:
  1. **PC Principal**: Dedicado a desarrollo, backtesting masivo con VectorBT, simulaciones de Monte Carlo y ejecución de modelos de IA locales con aceleración CUDA.
  2. **NAS Auxiliar**: Exclusivamente almacenamiento pasivo de copias de seguridad (dumps de DB) y exportación de históricos. No ejecuta bases de datos activas ni trading.
  3. **Cloud VPS**: Nodo de ejecución continua 24/7 para el backend, telemetría y conexiones oficiales a brokers.
* **Consecuencias**: Se aprovecha la potencia de cálculo del PC sin crear una dependencia crítica de que deba estar encendido para mantener la seguridad de las posiciones abiertas.

---

### ADR-005: Autonomía Progresiva por Etapas Obligatorias
* **Fecha**: 2026-11-09
* **Estado**: Aceptado
* **Contexto**: Nunca se debe arriesgar capital real sin validación empírica suficiente.
* **Decisión**: La plataforma arranca obligatoriamente en **Nivel 1: Analista (Solo Lectura)**. Las transiciones a Paper Trading (Nivel 2), Ejecución Supervisada (Nivel 3) y Autonomía Limitada (Nivel 4) requieren superar umbrales cuantitativos estrictos (Sharpe > 1.0, Profit Factor > 1.5 en out-of-sample) y aprobación humana explícita.
* **Consecuencias**: Se elimina el riesgo de pérdidas accidentales durante las fases de diseño y desarrollo.
