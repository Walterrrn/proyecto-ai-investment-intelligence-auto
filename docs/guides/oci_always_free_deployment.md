# GUÍA DE DESPLIEGUE EN ORACLE CLOUD (OCI) ALWAYS FREE
## Despliegue 24/7 a Coste Cero (0,00 €) en la Región de Madrid (España)

Esta guía detalla paso a paso cómo crear y configurar una máquina virtual en **Oracle Cloud Infrastructure (OCI) Always Free** para alojar el sistema completo (Backend FastAPI, PostgreSQL 16 con TimescaleDB y Redis) sin pagar nada.

---

## 1. RECURSOS GRATUITOS QUE UTILIZAREMOS

Oracle Cloud asigna de por vida a cada cuenta gratuita (*Always Free Eligible*):
* **Cómputo ARM Ampere A1**: Hasta **4 OCPUs** y **24 GB de memoria RAM** (se puede asignar a 1 sola máquina virtual o dividirla en varias).
* **Almacenamiento**: **200 GB** de disco SSD en bloque.
* **Red**: **10 TB/mes** de transferencia de salida a Internet y **1 IP pública IPv4 estática**.
* **Ubicación recomendada**: Datacenter de **Madrid (España)** (`eu-madrid-1`).

---

## 2. PASO 1: REGISTRO DE CUENTA EN ORACLE CLOUD

1. Entra en [oracle.com/cloud/free](https://www.oracle.com/cloud/free/).
2. Haz clic en **Start for free**.
3. Selecciona tu país (**Spain**) e introduce tus datos reales.
4. **Home Region**: Selecciona obligatoriamente **Spain Central (Madrid)** (`eu-madrid-1`).
   > *Nota*: La Home Region no se puede cambiar después y es donde tendrás los recursos Always Free con mínima latencia hacia brokers europeos.
5. **Verificación de tarjeta**: Oracle solicita una tarjeta de débito/crédito para verificar la identidad (realiza una retención temporal de ~1 € que se reembolsa de inmediato). **No cobrarán nada**.

---

## 3. PASO 2: CREACIÓN DE LA MÁQUINA VIRTUAL ALWAYS FREE

Una vez dentro de la consola de Oracle Cloud:

1. Ve al menú hamburguesa (arriba a la izquierda) ➔ **Compute** ➔ **Instances** (Instancias).
2. Haz clic en **Create instance** (Crear instancia).
3. **Nombre**: `aii-cloud-node-01`
4. **Compartment**: Deja el que viene por defecto.
5. **Placement (Ubicación)**: Availability Domain por defecto (AD-1).
6. **Image and Shape (Imagen y Forma)**:
   * Haz clic en **Edit**:
   * **Image**: Haz clic en *Change Image* y selecciona **Canonical Ubuntu 24.04** (o 22.04 LTS) versión **aarch64 (ARM)**.
   * **Shape**: Haz clic en *Change Shape*, selecciona **Ampere (ARM Processor)** ➔ `VM.Standard.A1.Flex`.
   * **Asignación de recursos recomendada**:
     * **OCPUs**: `2` (equivalente a 4 vCPUs estándar).
     * **Memoria (RAM)**: `12 GB` (suficiente para todo el stack y futuros modelos, dejando otros 2 OCPUs y 12 GB libres por si queremos crear otra VM en el futuro).
   * Verás la etiqueta verde: **Always Free Eligible**.
7. **Networking (Red)**:
   * Selecciona *Create new virtual cloud network (VCN)* y *Create new public subnet*.
   * Marca la casilla: **Assign a public IPv4 address** (Asignar una dirección IPv4 pública).
8. **Add SSH Keys (Claves SSH)**:
   * Selecciona *Generate a key pair for me* y descarga tanto la clave privada (`.key`) como la pública.
   * *(O sube tu clave pública existente si ya usas `id_ed25519.pub` / `id_rsa.pub`)*.
9. **Boot Volume (Disco)**:
   * Marca *Specify a custom boot volume size* y asígnale **80 GB** o **100 GB** (de los 200 GB gratuitos totales).
10. Haz clic en **Create** (Crear). En 1-2 minutos la máquina estará en estado verde **Running**.

---

## 4. PASO 3: ABRIR PUERTOS EN LA RED DE ORACLE (SECURITY LIST)

Por defecto, Oracle bloquea todo el tráfico entrante salvo el puerto SSH (22). Para permitir tráfico web:

1. En la página de detalles de tu instancia, haz clic en tu **Subnet** (debajo de *Primary VNIC*).
2. Haz clic en **Default Security List for vcn-...**.
3. En *Ingress Rules* (Reglas de entrada), haz clic en **Add Ingress Rules**:
   * **Source CIDR**: `0.0.0.0/0`
   * **IP Protocol**: `TCP`
   * **Destination Port Range**: `80,443,8000`
   * **Description**: `Allow HTTP, HTTPS and API Gateway`
4. Haz clic en **Add Ingress Rules**.

---

## 5. PASO 4: CONEXIÓN POR SSH Y CONFIGURACIÓN INICIAL DEL SERVIDOR

1. Abre **PowerShell** en tu PC local donde descargaste la clave SSH:
   ```powershell
   ssh -i .\ssh-key-*.key ubuntu@TU_IP_PUBLICA_DE_ORACLE
   ```
2. Actualiza el sistema operativo en la máquina:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
3. **Desbloquear el cortafuegos interno de Ubuntu (iptables de Oracle)**:
   Las imágenes de Ubuntu en Oracle Cloud traen reglas de `iptables` estrictas que bloquean puertos aunque los abras en la consola web:
   ```bash
   sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
   sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
   sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
   sudo netfilter-persistent save
   ```
4. **Instalar Docker y Docker Compose en Ubuntu**:
   ```bash
   sudo apt install -y docker.io docker-compose-v2 git
   sudo usermod -aG docker ubuntu
   # Reinicia la sesión para aplicar permisos
   exit
   ```

---

## 6. PASO 5: DESPLIEGUE DEL REPOSITORIO CON DOCKER COMPOSE

1. Conéctate de nuevo por SSH:
   ```bash
   ssh -i .\ssh-key-*.key ubuntu@TU_IP_PUBLICA_DE_ORACLE
   ```
2. Clona tu repositorio de GitHub:
   ```bash
   git clone https://github.com/Walterrrn/proyecto-ai-investment-intelligence-auto.git
   cd proyecto-ai-investment-intelligence-auto
   ```
3. Crea tu archivo `.env` a partir de la plantilla:
   ```bash
   cp .env.example .env
   ```
4. Levanta el stack completo con Docker Compose:
   ```bash
   docker compose up -d --build
   ```
5. Comprueba que todos los contenedores están sanos y en ejecución:
   ```bash
   docker ps
   ```
   Verás en ejecución:
   * `aii_timescaledb` (PostgreSQL 16 + TimescaleDB)
   * `aii_redis` (Redis 7)
   * `aii_backend` (FastAPI en Python 3.12)

6. Prueba que la API responde:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```
   O entra desde el navegador de tu PC a:
   `http://TU_IP_PUBLICA_DE_ORACLE:8000/docs`

---

## 7. POLÍTICA DE "MÁQUINA OCIOSA" DE ORACLE Y CÓMO EVITARLA

> [!TIP]
> Oracle Cloud tiene una cláusula en su programa gratuito: si una máquina pasa más de 7 días consecutivos con un uso de CPU inferior al 15-20% y sin uso de red, puede ser clasificada como "ociosa" (*Idle Instance*) y detenida automáticamente.

En nuestro sistema, **esto queda resuelto de forma natural**:
* Las tareas programadas de ingesta de datos de mercado (descarga de velas EOD, tipos de la FRED, balances e indicadores on-chain cada hora) generan actividad real periódica de CPU y red.
* Opcionalmente, se configura un cron en Linux que ejecute un heartbeat cada 10 minutos, garantizando que Oracle reconozca la instancia como un servicio productivo activo 24/7.
