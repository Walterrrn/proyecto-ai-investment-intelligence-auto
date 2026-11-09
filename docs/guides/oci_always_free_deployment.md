# GUÍA DE DESPLIEGUE EN ORACLE CLOUD (OCI) ALWAYS FREE
## Despliegue 24/7 a Coste Cero (0,00 €) en la Región de Madrid (España)

Esta guía detalla paso a paso cómo crear y configurar una máquina virtual en **Oracle Cloud Infrastructure (OCI) Always Free** para alojar el sistema completo (Backend FastAPI, PostgreSQL 16 con TimescaleDB y Redis) sin pagar nada, garantizando **cero costes ocultos**.

---

## 1. RECURSOS GRATUITOS QUE UTILIZAREMOS

Oracle Cloud asigna de por vida a cada cuenta gratuita (*Always Free Eligible*):
* **Cómputo ARM Ampere A1**: Hasta **4 OCPUs** y **24 GB de memoria RAM** (se puede asignar a 1 sola máquina virtual o dividirla en varias).
* **Almacenamiento**: **200 GB** de disco SSD en bloque.
* **Red**: **10 TB/mes** de transferencia de salida a Internet y **1 IP pública IPv4 estática**.
* **Ubicación recomendada**: Datacenter de **Madrid (España)** (`eu-madrid-1`).

---

## 2. TIPS CRÍTICOS PARA EL REGISTRO DE CUENTA (EVITAR RECHAZOS Y SUSTOS)

El sistema de validación de Oracle es conocido por ser muy estricto para evitar abusos. Sigue estas recomendaciones al darte de alta:

1. **Datos de Registro 100% Coincidentes**:
   * Tu nombre, apellidos, dirección postal y código postal deben coincidir **exactamente** con los que figuran en el extracto bancario de la tarjeta que vayas a introducir.
2. **Tipo de Tarjeta**:
   * Utiliza preferiblemente una tarjeta de débito o crédito bancaria tradicional (Santander, BBVA, CaixaBank, ING, Openbank, etc.).
   * *Precaución*: Las tarjetas virtuales temporales o desechables (como algunas de Revolut no verificadas) a veces son rechazadas por el filtro antifraude de Oracle.
3. **Sin VPNs ni Proxies**:
   * Regístrate desde tu conexión a Internet residencial habitual (fibra de casa), sin VPNs ni extensiones que modifiquen tu IP.
4. **Retención de Verificación**:
   * Oracle realiza una retención temporal de verificación de aproximadamente **0,93 € / 1 $**, que se libera y reembolsa automáticamente a los pocos minutos. **No es un cobro**.
5. **Elección de la "Home Region"**:
   * Selecciona obligatoriamente **Spain Central (Madrid)** (`eu-madrid-1`).
   * *Atención*: La Home Region **no se puede cambiar nunca**. Al elegir Madrid, tus recursos Always Free se crearán en España, con una latencia mínima (< 10 ms) hacia brokers europeos como Interactive Brokers o Kraken.

---

## 3. CÓMO BLINDARTE CONTRA SUSTOS: ALERTA DE PRESUPUESTO A 0,01 €

Para tener la tranquilidad absoluta de que nunca te cobrarán nada:

1. En la consola de Oracle Cloud, ve al menú superior izquierdo ➔ **Billing & Cost Management** ➔ **Budgets** (Presupuestos).
2. Haz clic en **Create Budget**:
   * **Budget Scope**: Compartment raíz.
   * **Monthly Budget Amount**: `1` (o `0.01` €).
   * **Threshold Metric**: *Forecasted Spend* (Gasto proyectado) o *Actual Spend*.
   * **Threshold Percentage**: `100%`.
   * **Email Recipients**: Tu correo electrónico personal.
3. Si cualquier servicio de pago llegase a encenderse por error, recibirás un aviso inmediato por email mucho antes de que suponga ningún importe significativo.

---

## 4. ¿HACEN FALTA BASES DE DATOS EXTERNAS O PLANIFICADORES EN OCI?

**Respuesta Técnica: NO**. 

Todo el sistema está diseñado para funcionar de forma **autónoma y autocontenida dentro de la propia máquina virtual**:

* **Base de Datos**: PostgreSQL 16 con TimescaleDB se ejecuta en un contenedor Docker con volumen persistente en los 80-100 GB SSD de la máquina virtual. Disponer de **12 GB de RAM** en la VM elimina por completo la necesidad de contratar bases de datos gestionadas de pago.
* **Planificador de Tareas**: La ejecución de ingestas y tareas periódicas corre a través de un scheduler interno en Python (AsyncIO / Celery Beat) y cron jobs del propio Linux. No se necesita contratar EventBridge ni servicios de orquestación en la nube.
* **Ventajas**:
  1. **Coste estrictamente cero (0,00 €)**.
  2. **Copias de seguridad fáciles**: Puedes programar un script diario que haga `pg_dump` y envíe la copia cifrada directamente a tu NAS Synology en casa vía SFTP/rsync.
  3. **Portabilidad total**: Si un día quieres mover el sistema a otro servidor o a tu PC, basta con llevarte la carpeta con el `docker-compose.yml`.

---

## 5. CREACIÓN DE LA INSTANCIA ALWAYS FREE (PASO A PASO)

1. Ve a **Compute** ➔ **Instances** ➔ **Create instance**.
2. **Nombre**: `aii-cloud-node-01`
3. **Image and Shape**:
   * Imagen: **Canonical Ubuntu 24.04** (o 22.04 LTS) versión **aarch64 (ARM)**.
   * Forma (*Shape*): **Ampere (ARM Processor)** ➔ `VM.Standard.A1.Flex`.
   * OCPUs: `2`.
   * RAM: `12 GB`.
   * *(Asegúrate de que aparece la etiqueta verde: **Always Free Eligible**)*.
4. **Networking**:
   * *Create new VCN* y *Create new public subnet*.
   * Marca: **Assign a public IPv4 address**.
5. **Claves SSH**:
   * Descarga la clave privada `.key` en tu PC (guárdala en un lugar seguro como `C:\Users\tu_usuario\.ssh\oci_key.key`).
6. **Disco de Arranque**:
   * Tamaño: **80 GB** o **100 GB** (dentro del cupo de 200 GB gratuitos).
7. Haz clic en **Create**. En 1 minuto estará en verde (*Running*).

---

## 6. ABRIR PUERTOS EN LA RED DE ORACLE (SECURITY LIST)

1. En la página de tu instancia, haz clic en tu **Subnet** (debajo de *Primary VNIC*).
2. Haz clic en **Default Security List for vcn-...**.
3. En *Ingress Rules*, haz clic en **Add Ingress Rules**:
   * **Source CIDR**: `0.0.0.0/0`
   * **IP Protocol**: `TCP`
   * **Destination Port Range**: `80,443,8000`
   * **Description**: `HTTP, HTTPS, API Gateway`
4. Haz clic en **Add Ingress Rules**.

---

## 7. CONFIGURACIÓN INICIAL DEL SERVIDOR POR SSH

Conéctate desde PowerShell en tu PC:
```powershell
ssh -i C:\ruta\a\tu\oci_key.key ubuntu@TU_IP_PUBLICA
```

Ejecuta dentro del servidor:
```bash
# 1. Actualizar paquetes
sudo apt update && sudo apt upgrade -y

# 2. Desbloquear iptables interno de Oracle para permitir puertos web
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
sudo netfilter-persistent save

# 3. Instalar Docker y Docker Compose
sudo apt install -y docker.io docker-compose-v2 git
sudo usermod -aG docker ubuntu
exit
```

---

## 8. FLUJO DE TRABAJO Y DESPLIEGUE AUTOMATIZADO DESDE TU PC

El flujo de trabajo es muy sencillo y te permite controlar todo desde tu ordenador:

```
[Tu PC (Ryzen 9 / Win 11)] ──► Desarrollas / Pruebas / git commit
           │
           ▼ (git push a GitHub)
       [GitHub]
           │
           ▼ (Ejecutas scripts\deploy_oci.ps1 desde tu PC)
[Servidor OCI Always Free 24/7] ──► Hace git pull y levanta contenedores automáticamente
```

### Despliegue en 1 clic con el Script de PowerShell:
Cada vez que quieras actualizar lo que corre en OCI con lo que tienes en GitHub, abres PowerShell en tu PC y ejecutas:

```powershell
.\scripts\deploy_oci.ps1 -OciIp "TU_IP_PUBLICA_DE_ORACLE" -KeyPath "C:\ruta\a\tu\oci_key.key"
```

El script se conecta por SSH a OCI, descarga la última versión y reconstruye los contenedores en segundo plano sin interrumpir los datos persistentes de la base de datos.
