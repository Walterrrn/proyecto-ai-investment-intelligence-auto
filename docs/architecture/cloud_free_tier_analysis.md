# ESTUDIO TÉCNICO: PROVEEDORES CLOUD EN CAPA GRATUITA (FREE TIER)
## AI Investment Intelligence Platform — Operativa Continua 24/7 a Coste Cero (0,00 €)

---

## 1. OBJETIVO DEL ANÁLISIS

Determinar la viabilidad técnica y operativa de alojar el backend, el motor de riesgo, la base de datos PostgreSQL/TimescaleDB y la caché de la plataforma en las capas gratuitas (*Free Tier*) de los principales proveedores cloud (**AWS, Google Cloud Platform, Microsoft Azure** y el caso especial de **Oracle Cloud Infrastructure**), con los siguientes requisitos:

1. **Coste recurrente estricto de 0,00 €/mes**.
2. **Operativa continua 24/7** (sin suspensiones por inactividad).
3. **Capacidad de cómputo y memoria suficiente** para ejecutar FastAPI, PostgreSQL y Redis sin caídas por *Out of Memory* (OOM).
4. **Prevención de costes ocultos o sobrecostes accidentales** por tráfico de red o fin de promociones temporales.

---

## 2. COMPARATIVA DETALLADA POR PROVEEDOR

### 2.1 Amazon Web Services (AWS)

```
[AWS Free Tier] ──► 12 Meses Gratis Únicamente (Caduca al año)
                ──► EC2: t2.micro / t3.micro (1 vCPU, 1 GB RAM)
                ──► EBS: 30 GB SSD
```

* **Recursos Disponibles**:
  * 750 horas/mes de instancia EC2 `t2.micro` (o `t3.micro` en regiones más recientes): 1 vCPU, 1 GB RAM.
  * 30 GB de almacenamiento EBS (disco SSD gp2/gp3).
  * 100 GB/mes de salida de datos a Internet (Always Free).
* **Limitación Crítica — No es "Always Free"**:
  * La instancia EC2 y el disco EBS gratuito **expiran a los 12 meses** desde la creación de la cuenta. A partir del mes 13, AWS comenzará a facturar automáticamente entre 8 € y 12 € al mes salvo que se destruya la instancia.
* **Limitación Técnica de Memoria (1 GB RAM)**:
  * Ejecutar Docker Compose con FastAPI + PostgreSQL + Redis en 1 GB de RAM físico provoca que el kernel de Linux dispare el *OOM Killer*, cerrando aleatoriamente la base de datos o el backend salvo que se configure un archivo swap de 2 a 4 GB en disco.
* **Veredicto para AWS**: **Aceptable como entorno temporal de 12 meses**, pero requiere migración al finalizar el año y optimización agresiva de memoria.

---

### 2.2 Google Cloud Platform (GCP)

```
[GCP Always Free] ──► Permanente (Sin fecha de caducidad)
                  ──► Compute Engine: e2-micro (0.25 vCPU base / 2 vCPU burst, 1 GB RAM)
                  ──► Persistent Disk: 30 GB HDD estándar
                  ──► Ubicación obligatoria: us-central1, us-west1 o us-east1
```

* **Recursos Disponibles**:
  * 1 instancia `e2-micro` mensual (Always Free).
  * 30 GB de disco persistente estándar mensual.
  * 5 GB de Cloud Storage (backups).
  * 1 GB de tráfico de salida fuera de Norteamérica (tráfico a España).
* **Ventajas**:
  * **Es 100% permanente (*Always Free*)**: No caduca a los 12 meses.
  * Procesadores modernos (Intel/AMD con tecnología de ráfagas hasta 2 vCPU).
* **Riesgos y Limitaciones Técnicas**:
  1. **1 GB de RAM física**: Requiere crear obligatoriamente un archivo `swap` de 2 a 3 GB en el disco de 30 GB y ajustar los límites de memoria de PostgreSQL (`shared_buffers = 128MB`) y Redis (`maxmemory 64mb`).
  2. **Tráfico de Red Egress**: El límite gratuito a destinos internacionales es de 1 GB/mes. Si el dashboard web consulta la API con excesiva frecuencia desde España sin caché local, el exceso de tráfico podría generar micro-cobros de pocos céntimos (aprox. 0,12 $/GB extra).
  3. **Latencia**: La instancia Always Free debe ubicarse en EE.UU. (`us-central1` Iowa, etc.). La latencia de respuesta hacia España será de ~100-120 ms (perfectamente aceptable para trading cuantitativo EOD y swing, no para microsegundos).
* **Veredicto para GCP**: **Candidato viable Always Free**, siempre que se configure memoria swap y se limite el tráfico saliente.

---

### 2.3 Microsoft Azure

```
[Azure Free Tier] ──► VM B1s (1 vCPU, 1 GB RAM) solo durante 12 meses
                  ──► App Service F1 (Always Free) se apaga tras 20 min de inactividad
```

* **Recursos Disponibles**:
  * 750 horas/mes de máquina virtual `B1s` (1 vCPU, 1 GB RAM, 12 meses gratis).
  * 64 GB de almacenamiento (2 discos de 32 GB P6 SSD) durante 12 meses.
  * 15 GB de ancho de banda saliente al mes.
  * *Servicios Always Free*: Azure App Service (F1 Free) y Azure Functions (1M invocaciones/mes).
* **Incompatibilidad de Azure App Service F1 para 24/7**:
  * El plan gratuito de App Service (F1) suspende y apaga la aplicación tras 20 minutos de inactividad de peticiones HTTP (*idle timeout*). Esto **impide la recolección programada de datos y la monitorización 24/7 en segundo plano**.
* **Veredicto para Azure**: **Descartado para operativa 24/7 permanente**, ya que la VM vence a los 12 meses y los servicios Always Free no soportan demonios en segundo plano continuo.

---

### 2.4 La Alternativa Especial: Oracle Cloud Infrastructure (OCI) Always Free

> [!IMPORTANT]
> Oracle Cloud ofrece el programa *Always Free* más generoso de la industria para computación y contenedores, sin fecha de caducidad.

```
[Oracle Cloud Always Free] ──► Permanente (Sin caducidad de 12 meses)
                           ──► Arquitectura ARM Ampere A1: Hasta 4 núcleos OCPU y 24 GB de RAM
                           ──► Almacenamiento: 200 GB de disco en bloque NVMe
                           ──► Ancho de banda: 10 TB/mes gratuitos
                           ──► Región disponible: Madrid (España)
```

* **Recursos Gratuitos de por Vida**:
  * **Hasta 4 OCPUs y 24 GB de memoria RAM** en instancias basadas en ARM (Ampere A1). Puedes crear 1 sola máquina virtual con **2 vCPUs y 12 GB de RAM** (o 4 vCPUs y 24 GB RAM) completamente gratis.
  * **200 GB de disco** SSD de alto rendimiento.
  * **10 TB de transferencia de red saliente al mes**.
  * **Sede física en España**: Región `eu-madrid-1` disponible, ofreciendo latencias mínimas (< 10 ms).
* **Compatibilidad con Nuestro Stack**:
  * Al disponer de 12 a 24 GB de RAM real, el stack completo de Docker Compose (`FastAPI` + `TimescaleDB` + `Redis` + `Worker`) se ejecuta con holgura total, sin necesidad de trucos de memoria swap ni riesgo de caídas OOM.
  * Las imágenes Docker oficiales de Python 3.12, PostgreSQL 16 y Redis disponen de soporte nativo para arquitecturas `linux/arm64` (multi-arch out-of-the-box).
* **Precaución en OCI**:
  * Política de máquinas ociosas (*Idle VM Policy*): Oracle puede reclamar instancias gratuitas si el uso de CPU durante 7 días consecutivos es inferior al 15-20%. Se soluciona programando los colectores de mercado periódicos y telemetría activa del sistema.
* **Veredicto para OCI**: **El mejor entorno para 24/7 a coste cero**.

---

## 3. TABLA COMPARATIVA RESUMIDA

| Proveedor | Modelo de Instancia | CPU / RAM | Almacenamiento | Duración Gratuita | Tráfico Saliente | Adecuación para 24/7 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **AWS** | `t2.micro` / `t3.micro` | 1 vCPU / 1 GB | 30 GB SSD | **Solo 12 Meses** | 100 GB/mes | Regular (Caduca al año) |
| **GCP** | `e2-micro` | 0.25 vCPU / 1 GB | 30 GB HDD | **Always Free** | 1 GB/mes a UE | Buena (Requiere Swap) |
| **Azure** | `B1s` / App Service F1 | 1 vCPU / 1 GB | 64 GB SSD | **Solo 12 Meses** | 15 GB/mes | Mala (App Service se duerme) |
| **Oracle Cloud** | `Ampere A1` (ARM) | **4 OCPU / 24 GB** | **200 GB SSD** | **Always Free** | **10.000 GB/mes** | **Excelente (Recomendada)** |

---

## 4. GUÍA DE OPTIMIZACIÓN PARA ENTORNOS DE 1 GB DE RAM (GCP / AWS)

Si decides utilizar la instancia `e2-micro` de Google Cloud Platform (GCP) o `t3.micro` de AWS, es imprescindible aplicar esta configuración para evitar que el sistema se quede sin memoria:

### 1. Creación de Memoria Virtual Swap (2 GB en Disco)
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 2. Ajuste de Parámetros de PostgreSQL para Bajo Consumo
En la configuración de PostgreSQL (`postgresql.conf` o variables en Docker):
* `shared_buffers = 128MB` (en lugar del valor por defecto de 256MB+).
* `work_mem = 4MB`.
* `max_connections = 25` (suficiente para un solo usuario).

### 3. Ajuste de Parámetros de Redis
En el archivo `redis.conf`:
* `maxmemory 64mb`
* `maxmemory-policy allkeys-lru`

### 4. Ajuste del Worker de FastAPI (Uvicorn)
* Ejecutar con un único worker (`--workers 1`), lo cual consume aproximadamente 65-80 MB de RAM.

---

## 5. ESTRATEGIA RECOMENDADA PARA NUESTRO ROADMAP

1. **Fase Actual (Diseño y Validación Local en PC)**:
   * Todo el desarrollo y validación se mantiene en el PC con Docker Desktop / SQLite / venv. **Coste: 0,00 €**.
2. **Fase de Despliegue 24/7 a Coste Cero**:
   * **Opción Principal (Recomendada)**: Abrir cuenta en **Oracle Cloud (Always Free)** en la región de Madrid y aprovisionar una instancia Ampere A1 (2 vCPU, 12 GB RAM, Ubuntu 24.04 ARM). Ejecutará el Docker Compose completo sin restricciones de memoria y con IP fija gratuita.
   * **Opción Secundaria**: Si no se dispone de cuenta OCI, utilizar la máquina `e2-micro` de **GCP (Always Free)** con los ajustes de 2 GB Swap detallados en este documento.
3. **Seguridad contra Sobrecostes**:
   * Configurar siempre en la consola cloud una **Alerta de Facturación (*Budget Alert*) al límite de 0,01 €** para recibir un aviso de inmediato si cualquier recurso no gratuito se activase accidentalmente.
