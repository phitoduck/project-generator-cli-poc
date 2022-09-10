from abc import ABC, abstractmethod
from dataclasses import dataclass
from multiprocessing.sharedctypes import Value
from pathlib import Path
import stat
from typing import List
from proj.project import Project
from proj.construct import Construct
from proj.types import TScope


class File(Construct, ABC):
    """
    Primitive type to manage file creation in a consistent way.

    Constructs can use descendants of this class to create files.
    But note that two or more files can make changes to the same file.
    """

    def __init__(
        self,
        scope: TScope,
        construct_id: str,
        path: Path,
        antitamper: bool = False,
        executable: bool = False,
        **kwargs,
    ):
        super().__init__(scope=scope, construct_id=construct_id, **kwargs)
        self.path = path
        self.antitamper = antitamper
        self.executable = executable
        self.register_with_project(self.node.root)

    @abstractmethod
    def synth_contents(self) -> str | bytes:
        """Produce the contents of the file."""
        ...

    def synth(self):
        self.make_parent_dir()

        contents: str | bytes = self.synth_contents()
        if isinstance(contents, str):
            self.path.write_text(contents)
        elif isinstance(contents, bytes):
            self.path.write_bytes(contents)
        else:
            raise ValueError(
                f"File.synth_contents() must return bytes or str. Got: type={type(contents)} value={contents[:100]}..."
            )

        if self.executable:
            self.make_executable()

    def make_parent_dir(self):
        self.path.parent.mkdir(exist_ok=True)

    def make_executable(self):
        """Perform the equivalent of ``chmod +x <file>``."""
        stat_result = self.path.stat()
        self.path.chmod(stat_result.st_mode | stat.S_IEXEC)

    def register_with_project(self, root: Project):
        root.files.add(self)

    def __str__(self) -> str:
        print(self.__dict__)
        return repr(self)

    def __repr__(self) -> str:
        cls: str = self.__class__.__name__
        key_vals: List[str] = ", ".join(
            [f"{key}={repr(val)}" for key, val in self.__dict__.items()]
        )
        return f"{cls}({key_vals})"
