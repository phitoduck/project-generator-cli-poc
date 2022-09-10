from pathlib import Path
from textwrap import dedent
from typing import Any, Iterable, List, Optional, Tuple
from proj.file import File
from proj.project import Project

from ruamel.yaml.main import round_trip_load, round_trip_dump, YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from proj.types import TScope


class YamlFile(File):
    """
    Base construct for generating YAML files.

    A YAML file can almost be represented as a dictionary, but metadata
    about fields in the YAML such as comments are difficult to represent.

    This class lets you add/update/remove sections of a YAML file
    represented as dictonaries. It also exposes helper methods
    to add comments at the end of lines or before keys.

    The present implementation of this class was inspired by this blog post:
    https://towardsdatascience.com/writing-yaml-files-with-python-a6a7fc6ed6c3
    """

    def __init__(
        self,
        scope: TScope,
        construct_id: str,
        path: Path,
        antitamper: bool = False,
        executable: bool = False,
        initial_contents: dict | str | None = None,
        indent: Optional[int] = 2,
        list_item_indent=0,
    ):
        super().__init__(
            scope=scope,
            construct_id=construct_id,
            path=path,
            antitamper=antitamper,
            executable=executable,
        )

        initial_contents = initial_contents or {}
        self.indent = indent
        self.list_item_indent = list_item_indent
        self.__doc: CommentedMap = round_trip_load(
            round_trip_dump(initial_contents), preserve_quotes=True
        )

    def set_header_comment(self, comment: str):
        self.__doc.yaml_set_start_comment(comment=comment, indent=0)

    def set_comment_before_key_at_path(self, path: str, comment: str):
        comment_indentation = calc_indentation_of_path(
            path,
            indent=self.indent,
            list_item_indent=self.list_item_indent,
        )
        final_key: str | int = get_final_key_in_path(path)

        sub_doc: CommentedMap | CommentedSeq = get_reference_container_by_path(
            path, self.__doc
        )
        sub_doc.yaml_set_comment_before_after_key(
            key=final_key,
            indent=comment_indentation,
            before=comment,
        )

    def set_eol_comment_at_path(self, path: str, comment: str):
        final_key: int | str = get_final_key_in_path(path=path)
        sub_doc: CommentedMap | CommentedSeq = get_reference_container_by_path(
            path, self.__doc
        )
        if not is_array_idx(path.split(".")[-1]) or True:
            sub_doc.yaml_add_eol_comment(
                key=final_key,
                comment=comment,
            )

    def synth_contents(self) -> str:
        return round_trip_dump(
            self.__doc, indent=self.indent, block_seq_indent=self.list_item_indent
        )


def get_reference_by_path(path: str, dictlike: dict) -> Any:
    """
    Get a reference to a value in a ``dictlike`` object using a dot-notation string.

    :param path: a string supporting dot-notation and array indices (like the ``jq`` CLI)
    :param dictlike: object with an interface like a dict

    .. code-block:: python

        obj = {
            "friends": [
                {"name": "murphy"},
                {"name": "jobillydoo"},
                {"name": "barrpiddles"},
            ]
        }
        val = get_reference_by_path("friends.[1].name", obj)
        print(val)

    Should return a reference to ``jobillydoo``.
    """

    parts = path.split(".")
    value = get_value(parts[0], dictlike)

    if len(parts) > 1:
        for part in parts[1:]:
            value = get_value(key=part, obj=value)

    return value


def calc_indentation_of_path(path: str, indent: int, list_item_indent: int) -> int:
    parts: List[str] = path.split(".")

    parts_that_are_array_indices = [part for part in parts if is_array_idx(part)]
    parts_that_are_not_array_indices = set(parts) - set(parts_that_are_array_indices)

    total_indentation_from_list_items = (
        len(parts_that_are_array_indices)
    ) * list_item_indent
    total_indentation_from_non_list_items = (
        len(parts_that_are_not_array_indices) - 1
    ) * indent

    return total_indentation_from_list_items + total_indentation_from_non_list_items


def get_reference_container_by_path(path: str, obj: dict) -> Any:
    parts = path.split(".")
    if len(parts) == 1:
        return obj

    parts = path.split(".")
    path_ = ".".join(parts[:-1])
    return get_reference_by_path(path_, obj)


def get_final_key_in_path(path: str):
    last_part: str = path.split(".")[-1]
    return get_scalar_key(last_part)


def is_array_idx(part: str) -> bool:
    return part.startswith("[") and part.endswith("]")


def is_slice(part: str) -> bool:
    return part.count(":") == 1


def get_array_idx(part: str) -> int:
    idx_as_string = part.strip("[").strip("]")
    return int(idx_as_string)


def get_slice_bounds(part: str) -> Tuple[int, int]:
    lower, upper = part.strip("[").strip("]").split(":")
    return int(lower), int(upper)


def get_scalar_key(part: str) -> int | str:
    if is_array_idx(part):
        return get_array_idx(part)
    return part


def get_value(key: str, obj: Any) -> Any:
    if not is_array_idx(key):
        return obj[key]

    if is_slice(key):
        lower, upper = get_slice_bounds(key)
        return obj[lower:upper]

    array_idx: int = get_array_idx(key)
    return obj[array_idx]


if __name__ == "__main__":
    from proj.consts import CONFIG_DIR_NAME, FILE_REGISTRY_FNAME

    THIS_DIR = Path(__file__).parent
    project = Project(directory=THIS_DIR)
    yaml_file = YamlFile(
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
        # initial_contents={
        #     "Shopping List": {
        #         "eggs": {"type": "free range", "brand": "Mr Tweedy", "amount": 12},
        #         "milk": {
        #             "type": "pasteurised",
        #             "litres": 1.5,
        #             "brands": ["FarmFresh", "FarmHouse gold", "Daisy The Cow"],
        #         },
        #     }
        # },
        path=project.directory / CONFIG_DIR_NAME / FILE_REGISTRY_FNAME,
        antitamper=True,
        executable=False,
        indent=5,
        list_item_indent=3,
    )

    # yaml_file.set_comment_before_key("unsure.reasons.[1]", "This key is tubular :D")
    # yaml_file.set_comment_before_key("Shopping List", "Don't forget the eggs!")
    # yaml_file.set_comment_before_key("Shopping List.eggs", "Don't forget the eggs!")
    # yaml_file.set_comment_before_key(
    #     "Shopping List.milk.brands.[2]", "Don't forget the eggs!"
    # )

    yaml_file.set_comment_before_key_at_path("enemies.[2]", "YOLO!")
    yaml_file.set_comment_before_key_at_path("enemies.[1].name", "YOLO!")
    yaml_file.set_eol_comment_at_path("unsure.motivations", "How's it going?")
    yaml_file.set_eol_comment_at_path("friends.[0].name", "How's it going?")
    yaml_file.set_eol_comment_at_path("friends.[1].name", "How's it going?")
    yaml_file.set_eol_comment_at_path("friends.[1].name", "Have I been replaced?")

    print(yaml_file.synth_contents())
    yaml_file.synth()
