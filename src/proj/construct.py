"""
Requirements:
- files need to be marked as tamper-proof
- does the framework need to commit files? That seems like a wierd responsibility.
  Until we have a reason not to, I think we should avoid doing anything but
  generating text files.
"""

from __future__ import annotations
from abc import ABC

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from proj import Project


class Construct(ABC):
    """Node in the graph that can perform operations on files."""

    def __init__(self, scope: "Project" | Construct, construct_id: str, **kwargs):
        from .node import Node

        self.scope = Construct
        self.id = construct_id
        self.node = Node.from_scope(scope, value=self)

        # register the node with it's parent
        scope.node.add_child(self)

    def synth(self):
        """Generate file changes associated with this construct."""
