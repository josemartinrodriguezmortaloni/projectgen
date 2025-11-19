"""
Controller (GRASP): Coordina flujo del CLI sin hacer trabajo pesado.
Facade (GoF): Simplifica acceso a validator y creator.
"""

import argparse
from pathlib import Path

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.tree import Tree

from generator.creator import ProjectCreator
from generator.validator import ValidationError, create_validator_chain


console = Console()


class CLI:
    """
    Controller (GRASP): Coordina flujo sin hacer trabajo pesado.
    Facade (GoF): Simplifica acceso a subsistemas (validator, creator).
    Single Responsibility (SOLID): Solo maneja interfaz CLI.
    
    Responsabilidades:
    - Parsear argumentos
    - Mostrar UI con Rich
    - Validar entrada
    - Delegar creación a ProjectCreator
    """
    
    def __init__(self):
        """
        Inicializa CLI con cadena de validadores y parser.
        """
        self._validator_chain = create_validator_chain()
        self._parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """
        Information Expert (GRASP): Conoce estructura de args.
        
        Returns:
            ArgumentParser configurado.
        """
        parser = argparse.ArgumentParser(
            description="🚀 Generador de proyectos FastAPI con arquitectura limpia",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="Ejemplo: python -m template-proyects mi-api --hash-algo argon2\n"
                   "         python -m template-proyects  # Modo interactivo completo"
        )
        
        parser.add_argument(
            "project_name",
            nargs="?",  # Make optional
            help="Nombre del proyecto (ej: mi-api, backend-service). Si no se provee, se preguntará interactivamente"
        )
        
        parser.add_argument(
            "--output-dir",
            type=Path,
            default=Path.cwd(),
            help="Directorio donde crear el proyecto (default: directorio actual)"
        )
        
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Sobrescribir proyecto existente"
        )
        
        parser.add_argument(
            "--no-docker",
            action="store_true",
            help="No generar Dockerfile ni docker-compose.yml"
        )
        
        parser.add_argument(
            "--no-tests",
            action="store_true",
            help="No generar directorio tests/"
        )
        
        parser.add_argument(
            "--hash-algo",
            choices=["bcrypt", "argon2"],
            default="argon2",
            help="Algoritmo de hash de passwords (default: argon2)"
        )
        
        return parser
    
    def run(self, args: list[str] | None = None) -> int:
        """
        Template Method (GoF): Flujo fijo del CLI.
        
        Args:
            args: Argumentos de línea de comandos (None = sys.argv).
            
        Returns:
            Exit code (0 = success, 1 = error, 130 = cancelled).
        """
        parsed = self._parser.parse_args(args)
        
        try:
            self._show_header()
            
            # Interactive configuration (always, but uses CLI args as defaults)
            parsed = self._get_interactive_config(parsed)
            
            # Validate after getting all config
            self._validate(parsed)
            
            # Confirm (with reconfiguration option)
            parsed = self._confirm_creation(parsed)
            
            self._create_project(parsed)
            self._show_success(parsed)
            return 0
        except ValidationError as exc:
            console.print(f"\n[red]✗ Error de validación:[/red] {exc}")
            return 1
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠ Cancelado por usuario[/yellow]")
            return 130
        except Exception as exc:
            console.print(f"\n[red]✗ Error inesperado:[/red] {exc}")
            console.print_exception()
            return 1
    
    def _show_header(self) -> None:
        """
        Rich UI: Header con panel.
        """
        console.print()
        console.print(Panel.fit(
            "[bold cyan]FastAPI Template Generator[/bold cyan]\n"
            "[dim]Arquitectura limpia con SOLID + GoF + GRASP[/dim]\n"
            "[dim]FastAPI 0.115+ | PostgreSQL 16 | SQLAlchemy 2.0 async[/dim]",
            border_style="cyan",
            box=box.DOUBLE
        ))
        console.print()
    
    def _validate(self, args: argparse.Namespace) -> None:
        """
        Delega validación a cadena de validadores.
        
        Args:
            args: Argumentos parseados.
            
        Raises:
            ValidationError: Si alguna validación falla.
        """
        target_path = args.output_dir / args.project_name
        
        # Solo validar si no se quiere sobrescribir
        if not args.overwrite:
            self._validator_chain.validate(args.project_name, target_path)
    
    def _get_interactive_config(self, args: argparse.Namespace) -> argparse.Namespace:
        """
        Prompts user for all configuration options interactively.
        Pattern: Template Method - defines fixed sequence of prompts
        
        Args:
            args: Initial arguments (may have some values pre-filled from CLI)
            
        Returns:
            Updated namespace with user's choices
        """
        console.print("[bold cyan]📋 Configuración del proyecto[/bold cyan]\n")
        
        # Project name (if not provided via CLI)
        if not args.project_name:
            args.project_name = Prompt.ask(
                "  [cyan]Nombre del proyecto[/cyan]",
                default="my-api"
            )
        
        # Output directory (always prompt unless explicitly set via CLI)
        if args.output_dir == Path.cwd():  # Default value, not explicitly set
            output_dir_str = Prompt.ask(
                "  [cyan]Directorio donde crear el proyecto[/cyan]",
                default=str(Path.cwd())
            )
            args.output_dir = Path(output_dir_str).expanduser().resolve()
        
        # Docker
        include_docker = Confirm.ask(
            "  [cyan]¿Incluir Docker y docker-compose?[/cyan]",
            default=not args.no_docker
        )
        args.no_docker = not include_docker
        
        # Tests
        include_tests = Confirm.ask(
            "  [cyan]¿Incluir directorio de tests?[/cyan]",
            default=not args.no_tests
        )
        args.no_tests = not include_tests
        
        # Hash algorithm
        args.hash_algo = Prompt.ask(
            "  [cyan]Algoritmo de hash para passwords[/cyan]",
            choices=["argon2", "bcrypt"],
            default=args.hash_algo
        )
        
        console.print()
        return args
    
    def _confirm_creation(self, args: argparse.Namespace) -> argparse.Namespace:
        """
        Rich UI: Muestra resumen y permite reconfigurar.
        Pattern: Template Method with loop for reconfiguration
        
        Args:
            args: Argumentos parseados.
            
        Returns:
            Confirmed (possibly modified) arguments.
            
        Raises:
            KeyboardInterrupt: Si usuario cancela definitivamente.
        """
        while True:
            # Tabla de configuración
            table = Table(
                title="⚙️  Configuración del proyecto",
                show_header=False,
                box=box.ROUNDED,
                border_style="blue"
            )
            table.add_column("Opción", style="cyan bold", width=20)
            table.add_column("Valor", style="green")
            
            table.add_row("📛 Nombre", args.project_name)
            table.add_row("📁 Directorio", str(args.output_dir / args.project_name))
            table.add_row("🐳 Docker", "❌ No" if args.no_docker else "✅ Sí")
            table.add_row("🧪 Tests", "❌ No" if args.no_tests else "✅ Sí")
            table.add_row("🔐 Hash", f"✅ {args.hash_algo.upper()}")
            
            console.print(table)
            console.print()
            
            # Confirmar
            if Confirm.ask("¿Crear proyecto con esta configuración?", default=True):
                console.print()
                return args
            
            # Si rechaza, preguntar si quiere reconfigurar
            console.print()
            if Confirm.ask(
                "[yellow]¿Deseas modificar la configuración?[/yellow]",
                default=True
            ):
                console.print()
                # Preserve project_name but allow re-prompting for everything
                args = self._get_interactive_config(args)
            else:
                raise KeyboardInterrupt()
    
    def _create_project(self, args: argparse.Namespace) -> None:
        """
        Delega creación a ProjectCreator con Rich progress.
        
        Args:
            args: Argumentos parseados.
        """
        target_path = args.output_dir / args.project_name
        
        # Preparar opciones
        options = {
            "include_docker": not args.no_docker,
            "include_tests": not args.no_tests,
            "hash_algo": args.hash_algo,
            "overwrite": args.overwrite,
        }
        
        # Crear instancia de ProjectCreator
        creator = ProjectCreator(args.project_name, target_path, options)
        
        # Mostrar progreso con Rich
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
            transient=False,
        ) as progress:
            task_id = progress.add_task(
                "[cyan]Generando proyecto...",
                total=100
            )
            creator.create(progress, task_id)
    
    def _show_success(self, args: argparse.Namespace) -> None:
        """
        Rich UI: Árbol de estructura + comandos siguientes.
        
        Args:
            args: Argumentos parseados.
        """
        console.print()
        console.print("[bold green]✓ ¡Proyecto creado exitosamente![/bold green]\n")
        
        # Árbol de estructura
        tree = Tree(
            f"📁 [bold cyan]{args.project_name}[/bold cyan]",
            guide_style="bright_blue"
        )
        
        app_node = tree.add("📁 [bold]app[/bold] - Código de la aplicación")
        app_node.add("📄 main.py - Entry point FastAPI")
        
        api_node = app_node.add("📁 api - Capa de presentación (HTTP)")
        api_node.add("📁 v1/endpoints - CRUD endpoints (users, products, orders)")
        
        app_node.add("📁 core - Config, security, events")
        app_node.add("📁 services - Lógica de negocio (Service Layer)")
        app_node.add("📁 repositories - Acceso a datos (Repository pattern)")
        app_node.add("📁 models - Modelos SQLAlchemy")
        app_node.add("📁 schemas - Schemas Pydantic")
        
        if not args.no_tests:
            tree.add("📁 [bold]tests[/bold] - Tests unitarios e integración")
        
        if not args.no_docker:
            tree.add("🐳 docker-compose.yml - Postgres + Redis + API")
            tree.add("🐳 Dockerfile - Imagen de la app")
        
        tree.add("📄 pyproject.toml - Deps + ruff config")
        tree.add("📄 .pre-commit-config.yaml - Git hooks")
        tree.add("📄 alembic.ini - Configuración migrations")
        
        console.print(tree)
        console.print()
        
        # Panel con comandos siguientes
        console.print(Panel(
            f"[bold white]Siguientes pasos:[/bold white]\n\n"
            f"[cyan]1.[/cyan] cd {args.project_name}\n"
            f"[cyan]2.[/cyan] uv sync                    [dim]# Instalar dependencias[/dim]\n"
            f"[cyan]3.[/cyan] docker-compose up -d       [dim]# Levantar Postgres + Redis[/dim]\n"
            f"[cyan]4.[/cyan] alembic upgrade head        [dim]# Ejecutar migraciones[/dim]\n"
            f"[cyan]5.[/cyan] uv run uvicorn app.main:app --reload\n\n"
            f"[bold green]API disponible en:[/bold green] "
            f"[link=http://localhost:8000]http://localhost:8000[/link]\n"
            f"[bold green]Docs interactivos:[/bold green] "
            f"[link=http://localhost:8000/docs]http://localhost:8000/docs[/link]\n"
            f"[bold green]ReDoc:[/bold green] "
            f"[link=http://localhost:8000/redoc]http://localhost:8000/redoc[/link]",
            title="🚀 [bold]¡Listo para desarrollar![/bold]",
            border_style="green",
            box=box.DOUBLE
        ))


def main() -> None:
    """
    Entry point del CLI.
    """
    cli = CLI()
    exit(cli.run())

