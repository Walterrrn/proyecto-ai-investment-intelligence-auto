#!/usr/bin/env bash
# ==============================================================================
# Script de despliegue automatizado hacia Oracle Cloud (OCI Always Free)
# ==============================================================================

set -euo pipefail

if [ "$#" -ne 2 ]; then
    echo "Uso: $0 <OCI_IP> <RUTA_CLAVE_SSH>"
    echo "Ejemplo: $0 123.45.67.89 ~/.ssh/oci_key.key"
    exit 1
fi

OCI_IP="$1"
KEY_PATH="$2"

echo "=========================================================="
echo " AI INVESTMENT INTELLIGENCE - DESPLIEGUE A OCI ALWAYS FREE"
echo "=========================================================="

ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no "ubuntu@$OCI_IP" << 'EOF'
set -e
echo "--- 1. Actualizando repositorio ---"
cd ~/proyecto-ai-investment-intelligence-auto
git pull origin main

echo "--- 2. Reconstruyendo contenedores Docker Compose ---"
docker compose up -d --build

echo "--- 3. Verificando estado de los servicios ---"
docker compose ps
EOF

echo ""
echo "[EXITO] Despliegue completado satisfactoriamente."
echo "API en: http://${OCI_IP}:8000/docs"
