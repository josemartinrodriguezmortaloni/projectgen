"""
Template Method (GoF): Define algoritmo de creación de proyectos.
Creator (GRASP): Responsable de crear estructura física del proyecto.
"""

import contextlib
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from rich.progress import Progress

from generator.templates.base import FileTemplate


class ProjectCreator(ABC):
    """
    Creator (GRASP): Responsable de crear estructura del proyecto.
    Template Method (GoF): Define algoritmo de creación en create().
    Single Responsibility (SOLID): Solo crea archivos/directorios.
    Protected Variations (GRASP): Protege contra cambios en I/O.
    """

    def __init__(self, project_name: str, target_path: Path, options: dict[str, Any]):
        """
        Args:
            project_name: Nombre del proyecto.
            target_path: Ruta completa donde crear el proyecto.
            options: Diccionario con opciones de creación.
        """
        self._project_name = project_name
        self._target_path = target_path
        self._options = options
        self._templates: list[FileTemplate] = []

    def create(self, progress: Progress, task_id: int) -> None:
        """
        Template Method (GoF): Define pasos de creación.
        Information Expert (GRASP): Conoce orden de pasos.

        Args:
            progress: Objeto Progress de Rich para mostrar progreso.
            task_id: ID de la tarea de progreso.
        """
        total_steps = 7  # Added dependency installation as potential step
        current_step = 0

        # Paso 1: Recolectar templates
        progress.update(
            task_id,
            description="[cyan]Recolectando templates...",
            completed=(current_step / total_steps) * 100,
        )
        self._collect_templates()
        current_step += 1

        # Paso 2: Crear directorios
        progress.update(
            task_id,
            description="[cyan]Creando estructura de directorios...",
            completed=(current_step / total_steps) * 100,
        )
        self._create_directories()
        current_step += 1

        # Paso 3: Crear archivos
        progress.update(
            task_id,
            description="[cyan]Generando archivos...",
            completed=(current_step / total_steps) * 100,
        )
        self._create_files()
        current_step += 1

        # Paso 4: Inicializar git
        progress.update(
            task_id,
            description="[cyan]Inicializando repositorio Git...",
            completed=(current_step / total_steps) * 100,
        )
        self._initialize_git()
        current_step += 1

        # Paso 5: Instalar dependencias (Hook opcional)
        progress.update(
            task_id,
            description="[cyan]Instalando dependencias...",
            completed=(current_step / total_steps) * 100,
        )
        self._install_dependencies()
        current_step += 1

        # Paso 6: Instalar pre-commit
        progress.update(
            task_id,
            description="[cyan]Configurando pre-commit hooks...",
            completed=(current_step / total_steps) * 100,
        )
        self._install_pre_commit()
        current_step += 1

        # Paso 7: Finalizar
        progress.update(task_id, description="[green]✓ Proyecto creado", completed=100)

    @abstractmethod
    def _collect_templates(self) -> None:
        """
        Hook: cada creator define sus templates específicos.
        """
        pass

    def _install_dependencies(self) -> None:
        """
        Hook opcional para instalar dependencias después de crear archivos.
        Por defecto no hace nada (útil para npm/pnpm install en TS).
        """
        pass

    def _create_directories(self) -> None:
        """
        Pure Fabrication (GRASP): Lógica técnica, no de dominio.
        Crea todos los directorios necesarios para los archivos.
        """
        dirs = self._extract_directories()
        for directory in sorted(dirs):
            full_path = self._target_path / directory
            full_path.mkdir(parents=True, exist_ok=True)

    def _extract_directories(self) -> set[Path]:
        """
        Helper: Extrae directorios únicos de templates.
        """
        dirs: set[Path] = {Path(".")}  # Raíz siempre

        for template in self._templates:
            path = Path(template.relative_path)
            current = path.parent

            # Agregar directorio y todos sus padres
            while current != Path("."):
                dirs.add(current)
                current = current.parent

        return dirs

    def _create_files(self) -> None:
        """
        Protected Variations (GRASP): Protege contra cambios en I/O.
        Crea todos los archivos a partir de los templates.
        """
        for template in self._templates:
            file_path = self._target_path / template.relative_path

            # Skip si ya existe y no se quiere sobrescribir
            if file_path.exists() and not self._options.get("overwrite", False):
                continue

            # Asegurar que el directorio padre existe
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Obtener contenido y escribir archivo
            content = template.get_content()
            file_path.write_text(content, encoding="utf-8")

    def _initialize_git(self) -> None:
        """
        Inicializa repositorio git si no existe.
        """
        git_dir = self._target_path / ".git"
        if git_dir.exists():
            return  # Ya está inicializado

        try:
            # git init
            subprocess.run(
                ["git", "init"], cwd=self._target_path, check=True, capture_output=True, timeout=10
            )

            # git add .gitignore
            # Solo si existe .gitignore
            if (self._target_path / ".gitignore").exists():
                subprocess.run(
                    ["git", "add", ".gitignore"],
                    cwd=self._target_path,
                    check=True,
                    capture_output=True,
                    timeout=10,
                )
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            # Git es opcional, no bloquea si falla
            pass

    def _install_pre_commit(self) -> None:
        """
        Instala hooks de pre-commit si está disponible y hay configuración.
        """
        if not (self._target_path / ".pre-commit-config.yaml").exists():
            return

        with contextlib.suppress(
            subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired
        ):
            subprocess.run(
                ["pre-commit", "install"],
                cwd=self._target_path,
                check=True,
                capture_output=True,
                timeout=30,
            )
