from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Dict, List, Union
from proj import Construct

from tomlkit import comment, document, nl, table, TOMLDocument
from tomlkit.items import Table
from tomlkit import dumps

if TYPE_CHECKING:
    from proj import Project


class SetupCfgFile(Construct):
    def __init__(
        self,
        scope: Union["Project", Construct],
        construct_id: str,
        path: Path,
        install_requires: List[str],
        extras_require: Dict[str, List[str]] = None,
        **kwargs,
    ):
        super().__init__(scope, construct_id)

        self.extras_require = extras_require

        self.path = path
        self.__doc: TOMLDocument = document()

    def __add__extras_require__section(
        self, extras: Dict[str, List[str]], toml_doc: TOMLDocument
    ):
        extras_require: Table = table()

        for extra in extras.keys():
            extras_require.add(extra, extras[extra])

        extras_require_comment = _make_comment(
            """\
        You can define optional dependencies that can be 
        # installed by running: pip install .[some-extra]\
        """
        )

        toml_doc.add(comment(extras_require_comment))
        toml_doc["extras_require"] = extras_require

        toml_doc.add(comment(extras_require_comment))
        toml_doc["next"] = extras_require

    def synth(self):
        self.__add__extras_require__section(
            extras=self.extras_require, toml_doc=self.__doc
        )

        self.path.parent.mkdir(exist_ok=True)

        contents_: str = dumps(self.__doc)
        contents: str = _post_process_toml_string(contents_)

        self.path.write_text(contents)


def _post_process_toml_string(toml: str) -> str:
    lines = toml.splitlines()
    stripped_toml = "\n".join(line.strip() for line in lines)
    return (
        stripped_toml.replace("<end-comment>\n", "")
        .replace("# <start-comment>", "\n# ")
        .strip()
    )


def _make_comment(text: str) -> str:
    return f"<start-comment>{dedent(text)}<end-comment>"
