# Uso: .\scripts\build.ps1 "Intervenciones" [vueltas] [espera]
param([string]$Dominio, [int]$Vueltas = 6, [int]$Espera = 900)
Set-Location (Split-Path $PSScriptRoot)
python -m forge build $Dominio --laps $Vueltas --wait $Espera
