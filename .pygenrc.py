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

        TextFile(self, "text-file", path=directory / "file.txt", contents="soup bubba")

        TextFile(
            self,
            "text-file-2",
            path=directory / "file2.txt",
            contents="soup bubba",
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


project = Project(directory=THIS_DIR / "sample-pygen-proj")
pkg1 = PythonPackage(
    project, "python-package-1", directory=project.directory / "python-package-1"
)
PythonPackage(
    project, "python-package-2", directory=project.directory / "python-package-2"
)
YamlFile(
    project,
    "file-registry.yml",
    initial_contents={
        "friends": [
            {"name": "murphy"},
            {"name": "jobillydoo"},
            {"name": "barrpiddles"},
        ],
        "enemies": [
            {"name": "zurg"},
            {"name": "smurf"},
            {"name": "larry"},
        ],
        "unsure": {"reasons": ["blegh", "blagh"], "motivations": "none, really"},
    },
    path=project.directory / CONFIG_DIR_NAME / FILE_REGISTRY_FNAME,
    antitamper=True,
    executable=False,
    indent=5,
    list_item_indent=3,
)

project.synth()
