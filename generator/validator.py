"""
Chain of Responsibility (GoF): Cadena de validadores.
Open/Closed (SOLID): Extendible sin modificar código existente.
Template Method (GoF): validate() define estructura fija.
"""

import os
import re
from abc import ABC, abstractmethod
from pathlib import Path


class ValidationError(Exception):
    """
    Custom exception para errores de validación.
    
    Dependency Inversion (SOLID): No depende de excepciones estándar,
    permite identificar errores de validación específicamente.
    """
    pass


class Validator(ABC):
    """
    Chain of Responsibility (GoF): Clase base para cadena de validadores.
    Open/Closed (SOLID): Extendible por herencia, cerrado para modificación.
    Template Method (GoF): validate() define estructura, _do_validate() es hook.
    
    Cada validador puede tener un siguiente validador en la cadena.
    Si la validación pasa, delega al siguiente; si falla, lanza excepción.
    """
    
    def __init__(self, next_validator: 'Validator | None' = None):
        """
        Args:
            next_validator: Siguiente validador en la cadena (opcional).
        """
        self._next = next_validator
    
    def validate(self, project_name: str, target_path: Path) -> None:
        """
        Template Method (GoF): Define estructura fija del algoritmo.
        
        Ejecuta la validación de esta instancia y luego delega al siguiente
        si existe.
        
        Args:
            project_name: Nombre del proyecto a validar.
            target_path: Ruta completa donde se creará el proyecto.
            
        Raises:
            ValidationError: Si la validación falla.
        """
        self._do_validate(project_name, target_path)
        if self._next:
            self._next.validate(project_name, target_path)
    
    @abstractmethod
    def _do_validate(self, project_name: str, target_path: Path) -> None:
        """
        Hook para subclases (Liskov Substitution).
        
        Cada validador concreto implementa su lógica específica aquí.
        
        Args:
            project_name: Nombre del proyecto a validar.
            target_path: Ruta completa donde se creará el proyecto.
            
        Raises:
            ValidationError: Si la validación falla.
        """
        pass


class ProjectNameValidator(Validator):
    """
    Single Responsibility (SOLID): Solo valida formato del nombre.
    
    Verifica que el nombre del proyecto:
    - Comience con alfanumérico
    - Solo contenga letras, números, guiones y guiones bajos
    - Tenga al menos 2 caracteres
    """
    
    def _do_validate(self, project_name: str, target_path: Path) -> None:
        """
        Valida formato del nombre del proyecto.
        
        Raises:
            ValidationError: Si el nombre no cumple con el formato.
        """
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_-]*$', project_name):
            raise ValidationError(
                "Nombre debe comenzar con alfanumérico y solo contener a-z, 0-9, -, _"
            )
        if len(project_name) < 2:
            raise ValidationError("Nombre debe tener al menos 2 caracteres")


class DirectoryExistsValidator(Validator):
    """
    Single Responsibility (SOLID): Solo valida si directorio existe.
    
    Verifica que el directorio de destino no exista o esté vacío.
    """
    
    def _do_validate(self, project_name: str, target_path: Path) -> None:
        """
        Valida que el directorio no exista o esté vacío.
        
        Raises:
            ValidationError: Si el directorio existe y no está vacío.
        """
        if target_path.exists() and any(target_path.iterdir()):
            raise ValidationError(
                f"Directorio {target_path} existe y no está vacío. "
                "Use --overwrite para sobrescribir."
            )


class WritablePathValidator(Validator):
    """
    Single Responsibility (SOLID): Solo valida permisos de escritura.
    
    Verifica que el directorio padre exista y tenga permisos de escritura.
    """
    
    def _do_validate(self, project_name: str, target_path: Path) -> None:
        """
        Valida permisos de escritura en directorio padre.
        
        Raises:
            ValidationError: Si no hay permisos o el padre no existe.
        """
        parent = target_path.parent
        if not parent.exists():
            raise ValidationError(f"Directorio padre {parent} no existe")
        if not os.access(parent, os.W_OK):
            raise ValidationError(f"Sin permisos de escritura en {parent}")


def create_validator_chain() -> Validator:
    """
    Factory Method (GoF): Encapsula creación de la cadena de validadores.
    Creator (GRASP): Responsable de crear y configurar validadores.
    
    Crea la cadena en orden específico:
    1. Valida nombre del proyecto
    2. Valida que directorio no exista
    3. Valida permisos de escritura
    
    Returns:
        Primer validador de la cadena configurada.
    """
    return ProjectNameValidator(
        DirectoryExistsValidator(
            WritablePathValidator()
        )
    )

