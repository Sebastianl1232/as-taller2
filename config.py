"""
Configuración de la aplicación Flask
"""
import os
from pathlib import Path

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Configuración base de la aplicación"""
    
    # Clave secreta para sesiones y formularios
    # En producción, esto debe venir de una variable de entorno
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Configuración de base de datos
    # Si no se define DATABASE_URL, se usa una BD en memoria (no crea archivo .db)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///:memory:'
    
    # Desactivar el seguimiento de modificaciones de SQLAlchemy para mejorar el rendimiento
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de Flask
    DEBUG = True  # Cambiar a False en producción
    
    # Configuración para formularios
    WTF_CSRF_ENABLED = True


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Mostrar consultas SQL en la consola


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # En producción, se debe definir DATABASE_URL (PostgreSQL/MySQL/SQLite administrado)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Diccionario de configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

