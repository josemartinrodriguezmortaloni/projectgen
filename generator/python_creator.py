from generator.creator import ProjectCreator
from generator.templates.python.app_files import get_app_templates
from generator.templates.python.config_files import get_config_templates
from generator.templates.python.test_files import get_test_templates


class PythonProjectCreator(ProjectCreator):
    """
    Creator específico para proyectos FastAPI (Python).
    Extiende ProjectCreator (Template Method) para definir templates específicos.
    """

    def _collect_templates(self) -> None:
        """
        Information Expert (GRASP): Sabe qué templates necesita un proyecto Python.
        Strategy (GoF): Implementación específica para Python.
        """
        # App templates (FastAPI core)
        self._templates.extend(
            get_app_templates(project_name=self._project_name, hash_algo=self._options["hash_algo"])
        )

        # Config templates (Docker, CI/CD, etc)
        self._templates.extend(
            get_config_templates(
                project_name=self._project_name,
                include_docker=self._options["include_docker"],
                include_cicd=self._options.get("include_cicd", True),
            )
        )

        # Tests templates (Conditional)
        if self._options["include_tests"]:
            self._templates.extend(get_test_templates())
