from generator.creator import ProjectCreator
from generator.templates.typescript.agent_files import get_agent_templates
from generator.templates.typescript.config_files import get_config_templates
from generator.templates.typescript.core_files import get_core_templates
from generator.templates.typescript.database_files import get_database_templates


class TypeScriptProjectCreator(ProjectCreator):
    """
    Creator específico para proyectos NestJS (TypeScript).
    Implementa la lógica para generar una arquitectura de Agentes de IA.
    """

    def _collect_templates(self) -> None:
        """
        Information Expert (GRASP): Sabe qué templates necesita un proyecto TypeScript.
        """
        # 1. Core Files (NestJS setup, Config, Env)
        self._templates.extend(get_core_templates(self._project_name))

        # 2. AI Agents Module (LLM Agnostic Architecture)
        self._templates.extend(
            get_agent_templates(
                default_model=self._options.get("default_llm", "gpt-5.1"),
                include_rag=self._options.get("include_rag", False),
            )
        )

        # 3. Database Module (Drizzle + PostgreSQL)
        self._templates.extend(
            get_database_templates(include_pgvector=self._options.get("include_rag", False))
        )

        # 4. Configuration & Infrastructure (Docker, CI/CD, package.json)
        self._templates.extend(
            get_config_templates(
                project_name=self._project_name,
                package_manager=self._options.get("package_manager", "pnpm"),
                include_docker=self._options.get("include_docker", True),
                include_tests=self._options.get("include_tests", True),
                include_cicd=self._options.get("include_cicd", True),
                include_queue=self._options.get("include_queue", False),
            )
        )

    def _install_dependencies(self) -> None:
        """
        Hook para instalar dependencias de Node.js si se desea.
        Por ahora lo dejamos vacío o podríamos imprimir instrucciones.
        El usuario suele preferir hacerlo manualmente o via script separado.
        """
        pass
