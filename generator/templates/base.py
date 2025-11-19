"""
Pure Fabrication (GRASP): Clases artificiales para representar templates.
Single Responsibility (SOLID): Solo contiene estructuras de datos y helpers.
"""

from dataclasses import dataclass
from typing import Callable
import textwrap


@dataclass(frozen=True)
class FileTemplate:
    """
    Pure Fabrication (GRASP): Clase artificial para representar archivos.
    Single Responsibility (SOLID): Solo contiene datos de template.
    Open/Closed (SOLID): Inmutable, no se puede modificar después de crear.
    
    Strategy (GoF): El content puede ser string o callable, permitiendo
    generación dinámica de contenido.
    
    Attributes:
        relative_path: Ruta relativa del archivo dentro del proyecto.
        content: Contenido del archivo (string o función que retorna string).
    """
    relative_path: str
    content: str | Callable[[], str]
    
    def get_content(self) -> str:
        """
        Polymorphism (GRASP): Maneja ambos tipos de content uniformemente.
        
        Returns:
            Contenido del archivo como string.
        """
        return self.content() if callable(self.content) else self.content


def dedent(text: str) -> str:
    """
    Helper: Normaliza indentación de strings multi-línea.
    
    Elimina indentación común, quita línea vacía inicial y asegura
    salto de línea final.
    
    Args:
        text: Texto con posible indentación.
        
    Returns:
        Texto sin indentación común y normalizado.
    """
    return textwrap.dedent(text).lstrip("\n").rstrip() + "\n"

