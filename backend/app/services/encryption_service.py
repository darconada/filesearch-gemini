"""Servicio de encriptación para API keys y datos sensibles"""
from cryptography.fernet import Fernet
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class EncryptionService:
    """Servicio para encriptar/desencriptar datos sensibles usando Fernet (AES-128)"""

    def __init__(self):
        self._cipher = None
        self._key_file = Path(__file__).parent.parent.parent / ".encryption_key"
        self._load_or_create_key()

    def _load_or_create_key(self):
        """Cargar la key de encriptación o crear una nueva si no existe"""
        try:
            if self._key_file.exists():
                # Cargar key existente
                with open(self._key_file, "rb") as f:
                    key = f.read()
                logger.info("Encryption key loaded from file")
            else:
                # Generar nueva key
                key = Fernet.generate_key()

                # Guardar la key de forma segura
                # En producción, considerar usar un KMS o variables de entorno
                with open(self._key_file, "wb") as f:
                    f.write(key)

                # Establecer permisos restrictivos (solo owner puede leer)
                os.chmod(self._key_file, 0o600)

                logger.warning(
                    f"NEW encryption key generated and saved to {self._key_file}. "
                    "BACKUP THIS FILE - if lost, encrypted data cannot be recovered!"
                )

            self._cipher = Fernet(key)

        except Exception as e:
            logger.error(f"Error loading/creating encryption key: {e}")
            raise

    def encrypt(self, plaintext: str) -> str:
        """
        Encriptar un string

        Args:
            plaintext: Texto a encriptar

        Returns:
            String encriptado (base64)
        """
        if not plaintext:
            return plaintext

        try:
            encrypted_bytes = self._cipher.encrypt(plaintext.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise

    def decrypt(self, encrypted_text: str) -> str:
        """
        Desencriptar un string

        Args:
            encrypted_text: Texto encriptado (base64) o texto plano

        Returns:
            Texto original

        Note:
            Si el texto NO está encriptado (backward compatibility),
            lo devuelve tal cual sin intentar desencriptar.
        """
        if not encrypted_text:
            return encrypted_text

        # Verificar si ya está encriptado
        # Si NO está encriptado, devolverlo tal cual (backward compatibility)
        if not self.is_encrypted(encrypted_text):
            logger.warning(f"Attempting to decrypt non-encrypted data (plain text API key). Consider encrypting it.")
            return encrypted_text

        try:
            decrypted_bytes = self._cipher.decrypt(encrypted_text.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise

    def is_encrypted(self, text: str) -> bool:
        """
        Verificar si un texto está encriptado (heurística básica)

        Los datos encriptados por Fernet empiezan con 'gAAAAA'
        """
        if not text:
            return False

        # Fernet tokens empiezan con version byte (0x80) seguido de timestamp
        # En base64, esto típicamente empieza con 'g'
        return text.startswith('gAAAAA')


# Instancia global del servicio
encryption_service = EncryptionService()
