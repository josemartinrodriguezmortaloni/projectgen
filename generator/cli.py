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
from generator.python_creator import PythonProjectCreator
from generator.typescript_creator import TypeScriptProjectCreator
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
    - Delegar creación a ProjectCreator adecuado (Factory Method implícito)
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
            description="🚀 Generador de proyectos Multi-lenguaje (Python & TypeScript)",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="Ejemplo: python -m template-proyects my-api --type python\n"
            "         python -m template-proyects  # Modo interactivo completo",
        )

        parser.add_argument(
            "project_name",
            nargs="?",  # Make optional
            help="Nombre del proyecto (ej: mi-api, backend-service). Si no se provee, se preguntará interactivamente",
        )

        parser.add_argument(
            "--type",
            choices=["python", "typescript"],
            help="Tipo de proyecto a generar (python | typescript)",
        )

        parser.add_argument(
            "--output-dir",
            type=Path,
            default=Path.cwd(),
            help="Directorio donde crear el proyecto (default: directorio actual)",
        )

        parser.add_argument(
            "--overwrite", action="store_true", help="Sobrescribir proyecto existente"
        )

        parser.add_argument(
            "--no-docker", action="store_true", help="No generar Dockerfile ni docker-compose.yml"
        )

        parser.add_argument("--no-tests", action="store_true", help="No generar directorio tests/")

        parser.add_argument(
            "--no-cicd",
            action="store_true",
            help="No generar archivos de CI/CD (.github/workflows/)",
        )

        # Opciones Python
        parser.add_argument(
            "--hash-algo",
            choices=["bcrypt", "argon2"],
            default="argon2",
            help="[Python] Algoritmo de hash de passwords (default: argon2)",
        )

        # Opciones TypeScript
        parser.add_argument(
            "--package-manager",
            choices=["pnpm", "npm", "yarn"],
            default="pnpm",
            help="[TypeScript] Gestor de paquetes (default: pnpm)",
        )

        parser.add_argument(
            "--non-interactive",
            action="store_true",
            help="Ejecutar sin preguntas interactivas (usar defaults para opciones no especificadas)",
        )

        # TS Options
        parser.add_argument(
            "--default-llm",
            choices=["gpt-5.1", "claude-sonnet-4.5", "claude-opus-4.1", "gemini-3"],
            default="gpt-5.1",
            help="[TypeScript] Modelo LLM por defecto",
        )

        parser.add_argument(
            "--include-rag",
            action="store_true",
            help="[TypeScript] Incluir sistema RAG",
        )

        parser.add_argument(
            "--include-queue",
            action="store_true",
            help="[TypeScript] Incluir sistema de colas (BullMQ)",
        )

        parser.add_argument(
            "--scaffold-only",
            action="store_true",
            help="[TypeScript] Generar scaffold mínimo (default) - solo estructura básica",
        )

        parser.add_argument(
            "--full",
            action="store_true",
            help="[TypeScript] Generar implementación completa con ejemplos funcionando",
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
            console.print(f"\n[red]! Error de validación:[/red] {exc}")
            return 1
        except KeyboardInterrupt:
            console.print("\n[yellow]! Cancelado por usuario[/yellow]")
            return 130
        except Exception as exc:
            console.print(f"\n[red]! Error inesperado:[/red] {exc}")
            console.print_exception()
            return 1

    def _show_header(self) -> None:
        """
        Rich UI: Header con panel.
        """
        console.print()
        console.print(
            Panel.fit(
                "[bold cyan]Project Generator CLI[/bold cyan]\n"
                "[dim]Arquitectura limpia con SOLID + GoF + GRASP[/dim]\n"
                "[dim]Soporte: Python (FastAPI) & TypeScript (NestJS)[/dim]",
                border_style="cyan",
                box=box.DOUBLE,
            )
        )
        console.print()

    def _validate(self, args: argparse.Namespace) -> None:
        """
        Delega validación a cadena de validadores.
        """
        target_path = args.output_dir / args.project_name

        # Solo validar si no se quiere sobrescribir
        if not args.overwrite:
            self._validator_chain.validate(args.project_name, target_path)

    def _get_interactive_config(self, args: argparse.Namespace) -> argparse.Namespace:
        """
        Prompts user for all configuration options interactively.
        Pattern: Template Method - defines fixed sequence of prompts
        """
        if args.non_interactive:
            if not args.project_name:
                args.project_name = "my-app"
            if not args.type:
                args.type = "typescript"
            return args

        console.print("[bold cyan]Configuration[/bold cyan]\n")

        # 1. Project Type (First Question)
        if not args.type:
            args.type = Prompt.ask(
                "  [cyan]Tipo de proyecto[/cyan]",
                choices=["python", "typescript"],
                default="typescript",
            )

        # 2. Project Name
        if not args.project_name:
            args.project_name = Prompt.ask("  [cyan]Nombre del proyecto[/cyan]", default="my-app")

        # 3. Output Directory
        if args.output_dir == Path.cwd():  # Default value, not explicitly set
            output_dir_str = Prompt.ask(
                "  [cyan]Directorio donde crear el proyecto[/cyan]", default=str(Path.cwd())
            )
            args.output_dir = Path(output_dir_str).expanduser().resolve()

        # Common Options
        include_docker = Confirm.ask(
            "  [cyan]¿Incluir Docker y docker-compose?[/cyan]", default=not args.no_docker
        )
        args.no_docker = not include_docker

        include_tests = Confirm.ask(
            "  [cyan]¿Incluir directorio de tests?[/cyan]", default=not args.no_tests
        )
        args.no_tests = not include_tests

        include_cicd = Confirm.ask(
            "  [cyan]¿Incluir GitHub Actions CI/CD?[/cyan]", default=not args.no_cicd
        )
        args.no_cicd = not include_cicd

        # Language Specific Options
        if args.type == "python":
            self._get_python_config(args)
        else:
            self._get_typescript_config(args)

        console.print()
        return args

    def _get_python_config(self, args: argparse.Namespace) -> None:
        """Prompts específicos para Python."""
        console.print("\n[dim]Configuración Python (FastAPI)[/dim]")
        args.hash_algo = Prompt.ask(
            "  [cyan]Algoritmo de hash para passwords[/cyan]",
            choices=["argon2", "bcrypt"],
            default=args.hash_algo,
        )

    def _get_typescript_config(self, args: argparse.Namespace) -> None:
        """Prompts específicos para TypeScript."""
        console.print("\n[dim]Configuración TypeScript (NestJS)[/dim]")

        args.package_manager = Prompt.ask(
            "  [cyan]Package Manager[/cyan]",
            choices=["pnpm", "npm", "yarn"],
            default="pnpm",
        )

        # Default LLM Model
        args.default_llm = Prompt.ask(
            "  [cyan]Modelo LLM por defecto[/cyan]",
            choices=["gpt-5.1", "claude-sonnet-4.5", "claude-opus-4.1", "gemini-3"],
            default="gpt-5.1",
        )

        # RAG System
        args.include_rag = Confirm.ask(
            "  [cyan]¿Incluir sistema RAG (pgvector + embeddings)?[/cyan]", default=False
        )

        # Queue System
        args.include_queue = Confirm.ask(
            "  [cyan]¿Incluir sistema de colas (BullMQ)?[/cyan]", default=False
        )

        # Generation Level (scaffold vs full)
        if not hasattr(args, "full") or not args.full:
            args.full = False
        if not hasattr(args, "scaffold_only") or not args.scaffold_only:
            args.scaffold_only = False

        # Si no se especificó ningún flag, preguntar
        if not args.full and not args.scaffold_only:
            generation_level = Prompt.ask(
                "  [cyan]Nivel de generación[/cyan]",
                choices=["scaffold", "full"],
                default="scaffold",
                help="scaffold: estructura básica funcional mínima | full: implementación completa",
            )
            args.full = generation_level == "full"
            args.scaffold_only = generation_level == "scaffold"
        elif args.full:
            args.scaffold_only = False
        else:
            args.scaffold_only = True

    def _confirm_creation(self, args: argparse.Namespace) -> argparse.Namespace:
        """
        Rich UI: Muestra resumen y permite reconfigurar.
        """
        if args.non_interactive:
            return args

        while True:
            # Tabla de configuración
            table = Table(
                title=f"Project Configuration ({args.type})",
                show_header=False,
                box=box.ROUNDED,
                border_style="blue",
            )
            table.add_column("Opción", style="cyan bold", width=20)
            table.add_column("Valor", style="green")

            table.add_row("Name", args.project_name)
            table.add_row("Directory", str(args.output_dir / args.project_name))
            table.add_row("Language", args.type.capitalize())
            table.add_row("Docker", "No" if args.no_docker else "Yes")
            table.add_row("Tests", "No" if args.no_tests else "Yes")
            table.add_row("CI/CD", "No" if args.no_cicd else "Yes")

            if args.type == "python":
                table.add_row("Hash", f"{args.hash_algo.upper()}")
            else:
                table.add_row("Pkg Manager", getattr(args, "package_manager", "pnpm"))
                table.add_row("LLM Default", getattr(args, "default_llm", "gpt-5.1"))
                table.add_row("RAG System", "Yes" if getattr(args, "include_rag", False) else "No")
                table.add_row(
                    "Queue System", "Yes" if getattr(args, "include_queue", False) else "No"
                )
                generation_mode = (
                    "Full (completo)" if getattr(args, "full", False) else "Scaffold (mínimo)"
                )
                table.add_row("Generation", generation_mode)

            console.print(table)
            console.print()

            # Confirmar
            if Confirm.ask("¿Crear proyecto con esta configuración?", default=True):
                console.print()
                return args

            # Si rechaza, preguntar si quiere reconfigurar
            console.print()
            if Confirm.ask("[yellow]¿Deseas modificar la configuración?[/yellow]", default=True):
                console.print()
                # Preserve project_name but allow re-prompting for everything
                args = self._get_interactive_config(args)
            else:
                raise KeyboardInterrupt()

    def _create_project(self, args: argparse.Namespace) -> None:
        """
        Delega creación a ProjectCreator con Rich progress.
        Factory Method: Decide qué Creator instanciar.
        """
        target_path = args.output_dir / args.project_name

        # Opciones comunes
        options = {
            "include_docker": not args.no_docker,
            "include_tests": not args.no_tests,
            "include_cicd": not args.no_cicd,
            "overwrite": args.overwrite,
        }

        # Crear instancia de ProjectCreator según tipo
        creator: ProjectCreator

        if args.type == "python":
            options["hash_algo"] = args.hash_algo
            creator = PythonProjectCreator(args.project_name, target_path, options)
        else:
            # Usar getattr() con defaults para evitar AttributeError en modo no interactivo
            options["package_manager"] = getattr(args, "package_manager", "pnpm")
            options["default_llm"] = getattr(args, "default_llm", "gpt-5.1")
            options["include_rag"] = getattr(args, "include_rag", False)
            options["include_queue"] = getattr(args, "include_queue", False)
            options["full"] = getattr(args, "full", False)
            creator = TypeScriptProjectCreator(args.project_name, target_path, options)

        # Mostrar progreso con Rich
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
            transient=False,
        ) as progress:
            task_id = progress.add_task("[cyan]Generando proyecto...", total=100)
            creator.create(progress, task_id)

    def _show_success(self, args: argparse.Namespace) -> None:
        """
        Rich UI: Árbol de estructura + comandos siguientes.
        """
        console.print()
        console.print("[bold green]Project created successfully![/bold green]\n")

        if args.type == "python":
            self._show_python_success(args)
        else:
            self._show_typescript_success(args)

    def _show_python_success(self, args: argparse.Namespace) -> None:
        # Árbol de estructura Python (simplificado)
        tree = Tree(f"[bold cyan]{args.project_name}[/bold cyan]", guide_style="bright_blue")
        tree.add("app/")
        tree.add("tests/")
        tree.add("pyproject.toml")
        console.print(tree)
        console.print()

        console.print(
            Panel(
                f"[bold white]Next steps:[/bold white]\n\n"
                f"[cyan]1.[/cyan] cd {args.project_name}\n"
                f"[cyan]2.[/cyan] uv sync\n"
                f"[cyan]3.[/cyan] docker-compose up -d\n"
                f"[cyan]4.[/cyan] alembic upgrade head\n"
                f"[cyan]5.[/cyan] uv run uvicorn app.main:app --reload",
                title="[bold]Python API Ready[/bold]",
                border_style="green",
                box=box.DOUBLE,
            )
        )

    def _show_typescript_success(self, args: argparse.Namespace) -> None:
        pm = getattr(args, "package_manager", "pnpm")
        run_cmd = "npm run" if pm == "npm" else pm

        # Árbol de estructura TypeScript
        tree = Tree(f"[bold cyan]{args.project_name}[/bold cyan]", guide_style="bright_blue")
        src = tree.add("src/")
        src.add("agents/ (LLM Agnostic Core)")
        src.add("database/ (Drizzle ORM)")
        src.add("config/")
        tree.add("package.json")
        tree.add("docker-compose.yml")
        console.print(tree)
        console.print()

        console.print(
            Panel(
                f"[bold white]Next steps:[/bold white]\n\n"
                f"[cyan]1.[/cyan] cd {args.project_name}\n"
                f"[cyan]2.[/cyan] {pm} install\n"
                f"[cyan]3.[/cyan] docker-compose up -d db redis\n"
                f"[cyan]4.[/cyan] {run_cmd} db:push\n"
                f"[cyan]5.[/cyan] {run_cmd} start:dev\n\n"
                f"[bold green]API Docs:[/bold green] http://localhost:3000/api/docs",
                title="[bold]NestJS AI Agent Ready[/bold]",
                border_style="green",
                box=box.DOUBLE,
            )
        )


def main() -> None:
    """
    Entry point del CLI.
    """
    cli = CLI()
    exit(cli.run())
