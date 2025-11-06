#!/bin/bash

echo "🚀 Iniciando entorno para Domain Finder..."
echo "=================================================="

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no encontrado. Instalando..."
    sudo apt update && sudo apt install -y python3 python3-pip
else
    echo "✅ Python3 encontrado: $(python3 --version)"
fi

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 no encontrado. Instalando..."
    sudo apt install -y python3-pip
else
    echo "✅ pip3 encontrado: $(pip3 --version)"
fi

# Instalar dependencias
echo ""
echo "📦 Instalando dependencias..."
pip3 install -r requirements.txt

# Verificar whois (para backup)
if ! command -v whois &> /dev/null; then
    echo "📦 Instalando whois (backup method)..."
    sudo apt install -y whois
else
    echo "✅ whois encontrado"
fi

# Verificar curl
if ! command -v curl &> /dev/null; then
    echo "📦 Instalando curl..."
    sudo apt install -y curl
else
    echo "✅ curl encontrado"
fi

echo ""
echo "🎯 Entorno listo!"
echo "=================================================="
echo ""
echo ""
echo "🚀 Iniciando Domain Finder..."
python3 domain_finder.py

echo ""
echo "📁 Los resultados se guardan con formato: dominios_disponibles_{letras}_{tlds}.txt"
echo "🔍 Para ver resultados: ls dominios_disponibles_*.txt"
echo ""
echo "✅ Proceso completado!"