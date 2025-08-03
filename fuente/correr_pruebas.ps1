$salida = "sobrecargar/pruebas/reportes"
if (-not (Test-Path $salida)) {
    New-Item -ItemType Directory -Path $salida | Out-Null
}

$rcfile = "sobrecargar/pruebas/.coveragerc"
$modulo_base = "sobrecargar.pruebas.__main__"

if ($args.Count -gt 0) {
    # Si los argumentos no contienen punto, se asume que es una clase de test (como "PruebasExtendidas")
    # y se completa con el nombre del módulo
    $targets = $args | ForEach-Object {
        if ($_ -notmatch "\.") {
            "$modulo_base.$_"
        } else {
            $_
        }
    }

    $tests = $targets -join " "
    coverage run --rcfile=$rcfile -m unittest $tests
} else {
    coverage run --rcfile=$rcfile -m sobrecargar.pruebas
}

coverage report --rcfile=$rcfile
coverage html --rcfile=$rcfile
coverage xml --rcfile=$rcfile

Write-Host "`nReporte guardado en $salida" -ForegroundColor Green
