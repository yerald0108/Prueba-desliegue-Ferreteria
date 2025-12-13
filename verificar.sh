#!/bin/bash

echo "🔍 Verificando implementación de prioridades urgentes..."
echo ""

# 1. Variables de entorno
echo "1️⃣ Variables de entorno:"
if [ -f .env ]; then
    echo "✅ Archivo .env existe"
else
    echo "❌ Archivo .env NO existe"
fi

if grep -q "^.env$" .gitignore; then
    echo "✅ .env en .gitignore"
else
    echo "❌ .env NO está en .gitignore"
fi

# 2. Archivos de error
echo ""
echo "2️⃣ Templates de error:"
for file in 404.html 500.html 429.html; do
    if [ -f "shop/templates/shop/errors/$file" ]; then
        echo "✅ $file existe"
    else
        echo "❌ $file NO existe"
    fi
done

# 3. Logging
echo ""
echo "3️⃣ Sistema de logging:"
if [ -d logs ]; then
    echo "✅ Carpeta logs/ existe"
else
    echo "❌ Carpeta logs/ NO existe"
fi

# 4. Rate limiting
echo ""
echo "4️⃣ Rate limiting:"
if pip show django-ratelimit > /dev/null 2>&1; then
    echo "✅ django-ratelimit instalado"
else
    echo "❌ django-ratelimit NO instalado"
fi

echo ""
echo "✅ Verificación completa"