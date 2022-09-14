from __future__ import annotations
from dataclasses import dataclass

from pathlib import Path
from typing import TYPE_CHECKING, Generic, List, Type, TypeVar

from proj.construct import Construct
from proj.project import Project

# a node can contain either a construct or a project
TNodeValue = TypeVar("TNodeValue", Construct, Project)


@dataclass(frozen=True, eq=True)
class Node(Generic[TNodeValue]):
    """
    .. code-block:: text

                    (root)
                    /    \\
            (construct)    (construct)
                            /       \\
                      (construct)    (construct)
    """

    # the tree has a single root node; all nodes should have a reference to root
    root: Project
    # value can be Root if it is the root node; otherwise it is a construct
    value: TNodeValue
    # the root node has no parent
    parent: Node[Construct | Project] | None

    children: List[Node[Construct | Project]]

    @property
    def path(self):
        c = self.value
        is_root = not self.parent
        return f"/{c.id}" if is_root else str(Path(c.id) / id)

    def add_child(self, child: Construct):
        self.children.append(child.node)
        self.root.constructs.add(child)

    @classmethod
    def from_scope(
        cls: Type[Node], scope: Construct | Project | None, value: Construct | Project
    ) -> Node:

        from proj import Construct, Project

        # determine root
        if isinstance(scope, Project):
            root: Project = scope
        elif isinstance(scope, Construct):
            root: Project = scope.node.root
        elif scope is None:
            root = value

        node: Node = cls(
            root=root,
            value=value,
            parent=None if isinstance(value, Project) else scope.node,
            children=[],
        )

        return node
