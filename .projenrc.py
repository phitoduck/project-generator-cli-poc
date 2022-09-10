from projen.python import PythonProject

project = PythonProject(
    author_email="eric.riddoch@gmail.com",
    author_name="Eric Riddoch",
    module_name="project_generator_cli_poc",
    name="project-generator-cli-poc",
    version="0.1.0",
)

project.synth()
