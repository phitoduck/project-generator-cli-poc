from typing import Optional
from proj import Construct
from pathlib import Path


class TextFile(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        path: Path,
        contents: Optional[str] = None,
        **kwargs,
    ):
        """Base class for a file.

        :param scope: parent construct
        :param id: identifier for the construct
        :param path: absolute file path for the file that should be created
        """
        super().__init__(scope=scope, construct_id=construct_id, **kwargs)
        self.fpath = path
        self.contents: str = contents or ""

    def synth(self):
        self.fpath.parent.mkdir(exist_ok=True)
        self.fpath.write_text(self.contents)
