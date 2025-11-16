#!/bin/bash

# Script de instalación para File Search RAG Application

echo "📦 Setting up File Search RAG Application..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed!"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed!"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✅ Found Node.js $NODE_VERSION"

# Setup Backend
echo ""
echo "🔧 Setting up backend..."
cd backend

# Crear entorno virtual
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env and add your GOOGLE_API_KEY"
fi

echo "✅ Backend setup complete"

# Setup Frontend
echo ""
echo "🎨 Setting up frontend..."
cd ../frontend

# Instalar dependencias
echo "Installing Node.js dependencies..."
npm install

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
fi

echo "✅ Frontend setup complete"

# Volver al directorio raíz
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit backend/.env and add your Google API key"
echo "   Get your API key from: https://aistudio.google.com/app/apikey"
echo ""
echo "2. Start the application:"
echo "   ./start.sh"
echo ""
echo "   Or manually:"
echo "   Terminal 1: cd backend && source venv/bin/activate && python -m app.main"
echo "   Terminal 2: cd frontend && npm run dev"
echo ""
echo "3. Open your browser at: http://localhost:5173"
echo ""
echo "📚 Read the README.md for more information"
