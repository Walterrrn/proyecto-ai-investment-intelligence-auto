# GUÍA DE INSTALACIÓN Y EJECUCIÓN EN WINDOWS 11
## PC Principal (AMD Ryzen 9 3950X / NVIDIA RTX 3090)

Esta guía explica paso a paso cómo clonar, configurar y ejecutar la plataforma **AI Investment Intelligence** en tu equipo local con Windows 11.

---

## 1. Requisitos Previos en Windows 11

Asegúrate de tener instalados en tu PC:
1. **Git para Windows**: [git-scm.com](https://git-scm.com/)
2. **Python 3.12+** (marca la casilla *"Add python.exe to PATH"* durante la instalación): [python.org](https://www.python.org/)
3. **Docker Desktop para Windows** (con el motor WSL 2 habilitado): [docker.com](https://www.docker.com/products/docker-desktop/)
   * *Opcional*: Si prefieres ejecutar en modo ligero sin Docker en la Fase 1, el backend soporta SQLite local (`aiosqlite`) sin necesidad de levantar contenedores.

---

## 2. Opción A: Ejecución Rápida con Docker Compose (Recomendada)

Esta opción levanta automáticamente la base de datos **TimescaleDB (PostgreSQL 16)**, la caché **Redis 7** y el backend **FastAPI** en contenedores aislados.

1. Abre **PowerShell** o **Windows Terminal**.
2. Clona el repositorio si no lo has hecho:
   ```powershell
   git clone https://github.com/Walterrrn/proyecto-ai-investment-intelligence-auto.git
   cd proyecto-ai-investment-intelligence-auto
   ```
3. Copia el archivo de configuración de entorno:
   ```powershell
   Copy-Item .env.example .env
   ```
4. Inicia los servicios con Docker Compose:
   ```powershell
   docker compose up --build
   ```
5. Accede desde tu navegador:
   * **Documentación interactiva de la API**: [http://localhost:8000/docs](http://localhost:8000/docs)
   * **Healthcheck del sistema**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
   * **Desglose de asignación de cartera**: [http://localhost:8000/api/v1/portfolio/allocation](http://localhost:8000/api/v1/portfolio/allocation)

Para detener los contenedores en cualquier momento:
```powershell
docker compose down
```

---

## 3. Opción B: Ejecución Nativa con Entorno Virtual de Python (Desarrollo Ligero)

Si deseas depurar código o ejecutar tests rápidamente sin encender Docker:

1. Abre **PowerShell** en la carpeta del proyecto.
2. Crea un entorno virtual con Python 3.12:
   ```powershell
   python -m venv .venv
   ```
3. Activa el entorno virtual:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   *(Si PowerShell bloquea la ejecución de scripts, ejecuta una sola vez: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*.
4. Actualiza pip e instala las dependencias:
   ```powershell
   pip install --upgrade pip
   pip install -r requirements-dev.txt
   ```
5. Copia la plantilla de entorno:
   ```powershell
   Copy-Item .env.example .env
   ```
6. Ejecuta la suite completa de tests para verificar que todo funciona:
   ```powershell
   pytest -v
   ```
   *(Verás los 14 tests pasando en verde).*
7. Inicia el servidor FastAPI en modo desarrollo con recarga en caliente:
   ```powershell
   uvicorn src.api.main:app --reload --port 8000
   ```
8. Abre en tu navegador [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 4. Verificación de Seguridad en la Fase 1

Cuando consultes el endpoint de salud en [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health), comprobarás los siguientes parámetros de seguridad:
```json
{
  "status": "online",
  "project": "AI Investment Intelligence",
  "version": "0.1.0",
  "environment": "development",
  "autonomy_mode": "ANALYST_ONLY",
  "database_connected": true,
  "live_trading_enabled": false
}
```

* El sistema arranca de forma predeterminada en modo **`ANALYST_ONLY`**.
* La ejecución real de órdenes está deshabilitada por diseño a nivel de código (`live_trading_enabled: false`).
