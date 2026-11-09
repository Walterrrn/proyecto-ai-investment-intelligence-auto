<#
.SYNOPSIS
    Script de despliegue automatizado desde Windows 11 hacia la máquina virtual en Oracle Cloud (OCI).
.DESCRIPTION
    Conecta por SSH a la instancia Always Free de OCI, descarga la última versión desde GitHub
    y actualiza los contenedores Docker Compose sin interrumpir los datos persistentes.
.EXAMPLE
    .\scripts\deploy_oci.ps1 -OciIp "123.45.67.89" -KeyPath "C:\Users\Walter\.ssh\oci_key.key"
#>

param (
    [Parameter(Mandatory = $true, HelpMessage = "Dirección IP pública de tu instancia en Oracle Cloud")]
    [string]$OciIp,

    [Parameter(Mandatory = $true, HelpMessage = "Ruta completa a tu clave privada SSH (.key o .pem)")]
    [string]$KeyPath
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " AI INVESTMENT INTELLIGENCE - DESPLIEGUE A OCI ALWAYS FREE" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

if (-not (Test-Path $KeyPath)) {
    Write-Host "[ERROR] No se encuentra la clave privada SSH en: $KeyPath" -ForegroundColor Red
    exit 1
}

Write-Host "[1/3] Conectando por SSH a $OciIp..." -ForegroundColor Yellow
$remoteCommand = @"
set -e
echo '--- Actualizando repositorio desde GitHub ---'
cd ~/proyecto-ai-investment-intelligence-auto
git pull origin main

echo '--- Reconstruyendo contenedores Docker Compose ---'
docker compose up -d --build

echo '--- Verificando estado de los servicios ---'
docker compose ps
"@

ssh -i $KeyPath -o StrictHostKeyChecking=no ubuntu@$OciIp $remoteCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[EXITO] Despliegue completado satisfactoriamente en OCI." -ForegroundColor Green
    Write-Host "Documentación activa en: http://${OciIp}:8000/docs" -ForegroundColor Cyan
} else {
    Write-Host "`n[ERROR] El despliegue ha fallado. Revisa los logs de SSH." -ForegroundColor Red
}
