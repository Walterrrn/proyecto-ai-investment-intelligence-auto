# POLÍTICA DE SEGURIDAD Y PROTECCIÓN DE ACTIVOS (SECURITY.MD)
## AI Investment Intelligence Platform

---

## 1. Principio Fundamental de Seguridad

La integridad y protección del patrimonio prevalecen sobre cualquier consideración de velocidad o sofisticación algorítmica.

El sistema está diseñado bajo el principio de **Privilegios Mínimos** (*Principle of Least Privilege*) y **Defensa en Profundidad**.

---

## 2. Gestión de Secretos y Credenciales de Brokers

1. **Prohibición Total de Secretos en el Repositorio**:
   * Ningún archivo `.env`, clave privada, certificado SSL ni API Key debe ser commiteado al repositorio Git.
   * El archivo `.gitignore` excluye activamente todos los patrones de credenciales (`.env`, `*.key`, `*.pem`, `secrets/`).
2. **Claves de API con Permisos Restringidos**:
   * Las claves generadas en brokers (Interactive Brokers, Kraken, Coinbase) **JAMÁS** tendrán activados permisos de retirada (*withdrawals*), transferencias ni depósitos.
   * Separación estricta entre **claves de solo lectura** (utilizadas por los colectores de telemetría y saldos) y **claves de trading** (utilizadas exclusivamente por el OMS).
3. **Cifrado en Reposo**:
   * Las credenciales que deban almacenarse en base de datos o en memoria se cifran mediante algoritmos simétricos robustos (AES-256-GCM / Fernet) utilizando una clave maestra derivada de una variable de entorno inyectada en tiempo de ejecución.
4. **Restricción de Acceso por IP (IP Whitelisting)**:
   * Toda clave de API habilitada para trading debe estar restringida exclusivamente a la dirección IP estática del servidor de ejecución (Cloud VPS o IP fija local).

---

## 3. Conmutador de Emergencia (Kill Switch) y Circuit Breakers

* **Kill Switch Lógico y Remoto**:
  * Implementado en memoria Redis y base de datos con flag atómico.
  * Al activarse:
    1. Cancela inmediatamente todas las órdenes pendientes en el OMS y en los brokers.
    2. Bloquea el envío de cualquier orden nueva.
    3. Emite alertas críticas inmediatas por canal seguro (Telegram / Webhook cifrado).
* **Circuit Breakers Automáticos**:
  * Si la pérdida diaria alcanza el **1,00 %**, se suspenden nuevas operaciones automáticamente por el resto de la sesión.
  * Si la pérdida semanal alcanza el **2,00 %**, se suspenden nuevas operaciones por el resto de la semana.
  * Si el *drawdown* acumulado alcanza el **10,00 %**, se congela de inmediato toda la operativa táctica hasta auditoría humana explícita.
* **Comportamiento ante Pérdida de Conexión o Datos Obsoletos**:
  * Si un feed de precios no se actualiza dentro de su ventana temporal de tolerancia, se marca como `STALE_DATA` y el Risk Engine bloquea cualquier operación sobre ese activo.
  * Si se pierde la conexión con el broker por más de 60 segundos, el sistema entra en modo de salvaguarda defensiva (*safe mode*).

---

## 4. Aislamiento de la Inteligencia Artificial (LLM)

* Los modelos de lenguaje y agentes de IA actúan **exclusivamente como analistas cualitativos y asistentes de investigación**.
* **El LLM no tiene acceso a endpoints de envío de órdenes**.
* La salida de los modelos LLM siempre es parseada a esquemas fuertemente tipados con Pydantic. Cualquier salida que no cumpla el esquema es descartada.
* El Risk Engine matemático no puede ser configurado, relajado ni modificado por prompts ni por inferencias de IA.

---

## 5. Reporte de Vulnerabilidades

Si detectas cualquier fallo de seguridad, bug en la validación de riesgos o exposición indebida de credenciales, abre un issue privado o comunícalo inmediatamente al responsable del proyecto antes de ejecutar cualquier operación en entornos de producción.
