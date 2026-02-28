"""
Módulo de controladores - Capa de lógica de negocio de la aplicación MVC

Este paquete contiene todos los controladores que manejan las rutas,
procesan las peticiones HTTP y coordinan entre modelos y vistas.
"""

# En versiones futuras, aquí importaremos todos los controladores
from .task_controller import *
from .auth_controller import *

__all__ = ['task_controller', 'auth_controller']

