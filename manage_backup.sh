#!/bin/bash

# Archivos a respaldar
FILES=("backend/app.db" "backend/token.json" "backend/credentials.json")
BACKUP_DIR="backups"
BACKUP_NAME="${BACKUP_DIR}/backup_filesearch_$(date +%Y%m%d_%H%M%S).tar.gz"

function do_backup() {
    echo "Iniciando backup..."
    
    # Crear directorio de backups si no existe
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        echo "Creado directorio: $BACKUP_DIR"
    fi
    
    # Verificar que existen los archivos
    FILES_TO_TAR=""
    for file in "${FILES[@]}"; do
        if [ -f "$file" ]; then
            FILES_TO_TAR="$FILES_TO_TAR $file"
            echo "Incluyendo: $file"
        else
            echo "Aviso: $file no encontrado (se omitirá)"
        fi
    done

    if [ -z "$FILES_TO_TAR" ]; then
        echo "Error: No se encontraron archivos para respaldar."
        exit 1
    fi

    # Crear el tar en el directorio de backups
    tar -czf "$BACKUP_NAME" $FILES_TO_TAR
    
    if [ $? -eq 0 ]; then
        echo "Backup creado exitosamente: $BACKUP_NAME"
    else
        echo "Error al crear el backup."
        exit 1
    fi
}

function do_restore() {
    if [ -z "$1" ]; then
        echo "Uso: $0 restore <archivo_backup.tar.gz> [-f|--force]"
        echo "Ejemplo: $0 restore backups/backup_filesearch_20241128_120000.tar.gz"
        exit 1
    fi

    BACKUP_FILE="$1"
    FORCE="$2"

    if [ ! -f "$BACKUP_FILE" ]; then
        echo "Error: El archivo $BACKUP_FILE no existe."
        exit 1
    fi

    if [[ "$FORCE" != "-f" && "$FORCE" != "--force" ]]; then
        echo "ADVERTENCIA: Esto sobrescribirá la base de datos y credenciales actuales en backend/."
        read -p "¿Estás seguro de continuar? (s/n): " confirm
        if [[ "$confirm" != "s" && "$confirm" != "S" ]]; then
            echo "Operación cancelada."
            exit 0
        fi
    else
        echo "Modo forzado: Saltando confirmación."
    fi

    echo "Restaurando desde $BACKUP_FILE..."
    # Extraer manteniendo la estructura de directorios (backend/...)
    tar -xzf "$BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        echo "Restauración completada."
    else
        echo "Error al restaurar."
        exit 1
    fi
}

case "$1" in
    backup)
        do_backup
        ;;
    restore)
        do_restore "$2"
        ;;
    *)
        echo "Uso: $0 {backup|restore <archivo>}"
        exit 1
        ;;
esac
