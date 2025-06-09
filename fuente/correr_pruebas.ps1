
$salida = "sobrecargar/pruebas/reportes"
if (-not (Test-Path $salida)) {
    New-Item -ItemType Directory -Path $salida | Out-Null
}

$rcfile = "sobrecargar/pruebas/.coveragerc"

coverage run --rcfile=$rcfile -m sobrecargar.pruebas
coverage report --rcfile=$rcfile
coverage html --rcfile=$rcfile
coverage xml --rcfile=$rcfile

Write-Host "`nReporte guardado en $salida" -ForegroundColor Green