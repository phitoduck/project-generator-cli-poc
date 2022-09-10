from pathlib import Path

from proj import Construct, Project, TScope
from proj.files.text_file import TextFile
from proj.files.yaml_file import YamlFile
from proj.python import SetupCfgFile
from proj.consts import CONFIG_DIR_NAME, FILE_REGISTRY_FNAME

THIS_DIR = Path(__file__).parent


class PythonPackage(Construct):
    def __init__(self, scope: TScope, construct_id: str, directory: Path, **kwargs):
        super().__init__(scope=scope, construct_id=construct_id, **kwargs)

        TextFile(
            self, "text-file", path=directory / "file.txt", contents="awesome text file"
        )

        TextFile(
            self,
            "text-file-2",
            path=directory / "file2.txt",
            contents="*ANOTHER* awesome text file :D",
        )

        self.setup_cfg = SetupCfgFile(
            self,
            "setup.cfg",
            install_requires=["a", "b", "c"],
            extras_require={
                "test": ["pytest", "pytest-cov>=0.0.0"],
                "dev": ["pandas"],
            },
            path=directory / "setup.cfg",
        )

        self.pre_commit_config_yaml = YamlFile(
            self,
            "file-registry.yml",
            initial_contents={
                "repos": [
                    {
                        "repo": "https://github.com/pre-commit/pre-commit-hooks",
                        "rev": "v4.1.0",
                        "hooks": [
                            {"id": "trailing-whitespace"},
                            {"id": "check-added-large-files"},
                            {"id": "check-ast"},
                            {"id": "check-json"},
                            {"id": "check-merge-conflict"},
                            {"id": "check-xml"},
                            {"id": "check-yaml"},
                            {"id": "debug-statements"},
                            {"id": "end-of-file-fixer"},
                            {"id": "requirements-txt-fixer"},
                            {"id": "mixed-line-ending", "args": ["--fix=auto"]},
                        ],
                    }
                ]
            },
            path=directory / ".pre-commit-config.yaml",
            antitamper=True,
            executable=False,
            indent=4,
            list_item_indent=0,
        )
        self.pre_commit_config_yaml.set_header_comment(
            "This file let's you run pre-commit hooks!"
        )
        self.pre_commit_config_yaml.set_comment_before_key_at_path(
            path="repos.[0]",
            comment="This is the official pre-commit repository URL",
        )
        self.pre_commit_config_yaml.set_eol_comment_at_path(
            path="repos.[0].rev",
            comment="Showing off end-of-line comments 🎉",
        )


project = Project(directory=THIS_DIR / "sample-pygen-proj")
pkg1 = PythonPackage(
    project, "python-package-1", directory=project.directory / "python-package-1"
)
PythonPackage(
    project, "python-package-2", directory=project.directory / "python-package-2"
)


project.synth()
