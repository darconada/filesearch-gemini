#!/bin/bash

# Script para iniciar backend y frontend simultáneamente

echo "🚀 Starting File Search RAG Application..."

# Verificar que exista el entorno virtual del backend
if [ ! -d "backend/venv" ]; then
    echo "❌ Backend virtual environment not found!"
    echo "Please run: cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Verificar que existan las dependencias del frontend
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Frontend dependencies not installed!"
    echo "Please run: cd frontend && npm install"
    exit 1
fi

# Iniciar backend en background
echo "🔧 Starting backend server..."
cd backend
source venv/bin/activate
python -m app.main &
BACKEND_PID=$!
cd ..

# Esperar un momento para que el backend inicie
sleep 3

# Verificar que el backend está corriendo
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "❌ Backend failed to start!"
    exit 1
fi

echo "✅ Backend started (PID: $BACKEND_PID)"
echo "📚 API Documentation: http://localhost:8000/docs"

# Iniciar frontend
echo "🎨 Starting frontend server..."
cd frontend
npm run dev

# Cleanup: cuando se cierra el frontend, matar el backend
echo ""
echo "🛑 Stopping servers..."
kill $BACKEND_PID 2>/dev/null
echo "✅ Application stopped"
