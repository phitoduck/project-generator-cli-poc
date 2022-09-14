from pathlib import Path
from proj.construct import Construct
from proj.types import TScope


class FileRegistry(Construct):
    def __init__(self, scope: TScope, construct_id: str, directory: Path, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
