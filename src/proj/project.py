"""
Question: are files the leaf nodes in the tree?
"""

from pathlib import Path
from typing import TYPE_CHECKING, Set
from proj.files.text_file import TextFile
from proj.python import SetupCfgFile

if TYPE_CHECKING:
    from .construct import Construct
    from .file import File


class Project:
    def __init__(self, directory: Path, **kwargs):
        from .node import Node

        self.directory = directory
        self.constructs: Set["Construct"] = set()
        self.files: Set["File"] = set()

        self.node = Node(children=[], value=self, parent=None, root=self)

    def synth(self):
        self.directory.mkdir(exist_ok=True)
        for construct in self.constructs:
            construct.synth()
