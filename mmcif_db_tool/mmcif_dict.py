import logging

from gemmi import cif
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class ItemFilter:
    def __init__(self, include_items: list[str] = [], exclude_items: set[str] = []):
        self.filtered_categories = set()
        self.include_items = set(include_items)
        self.exclude_items = set(exclude_items)
        self._set_filtered_cats()

    def _set_filtered_cats(self):
        for i in self.include_items:
            cat, _ = i.split('.')
            self.filtered_categories.add(cat)

        for i in self.exclude_items:
            cat, _ = i.split('.')
            self.filtered_categories.add(cat)


@dataclass
class Item:
    full_name: str
    name: str
    description: str
    mandatory_code: bool
    type_code: str
    default_value: str
    index: bool = field(default=False)

    def __post_init__(self):
        try:
            if self.default_value:
                if self.type_code in ("int", "positive_int"):
                    self.default_value = int(self.default_value)
                elif self.type_code == "float":
                    self.default_value = float(self.default_value)
        except ValueError:
            logger.warning(f"Could not convert default value {self.default_value} to {self.type_code} for `{self.full_name}`")

    def __hash__(self) -> int:
        return hash(self.full_name)


@dataclass
class Category:
    id: str
    description: str
    key_names: list[str]
    items: list[Item] = field(default_factory=list)

    def add_item(self, item: Item, filter: ItemFilter = None):
        if self.id in filter.filtered_categories:
            cat_item = f"{self.id}.{item.name}"
            if filter.include_items and cat_item not in filter.include_items:
                print(f"Skipping item {cat_item}")
                return

            if filter.exclude_items and cat_item in filter.exclude_items:
                print(f"Skipping item {cat_item}")
                return

        if item.name in self.key_names:
            item.index = True
        self.items.append(item)


class DictReader:
    def __init__(self, path: str) -> None:
        self._doc = cif.read_file(path)

    def get_categories(self, categories: list[str], filter: ItemFilter = None) -> list[Category]:
        cat_objs = {}
        search_set = set(categories)
        filter = filter or ItemFilter()
        block = self._doc.sole_block()
        grouped_items = self._find_grouped_items(block, search_set)

        for i in block:
            # first iteration is to create the category objects
            if i.frame is None:
                continue

            frame = i.frame
            if frame.name in search_set:
                logger.debug(f"Found category {frame.name}")
                cat_objs[frame.name] = self._parse_category(frame)

        for i in block:
            if i.frame is None:
                continue

            frame = i.frame
            cat_name = self._cat_from_frame(frame.name)
            if cat_name not in search_set:
                continue

            if frame.name in grouped_items:
                logger.debug(f"Found grouped item {frame.name}")
                cat_objs[cat_name].add_item(grouped_items[frame.name], filter)
                continue

            if frame.find_value("_item.name"):
                logger.debug(f"Found item {frame.name}")
                item = self._parse_item(frame)
                cat_objs[cat_name].add_item(item, filter)
                continue

        return list(cat_objs.values())

    def _cat_from_frame(self, frame_name):
        if frame_name is not None:
            return frame_name.lstrip("_").split('.')[0]

    def _find_grouped_items(self, block, search_set):
        # this is to find items defined in loops for
        # categories that have a group
        items = {}
        table = block.find_mmcif_category("_pdbx_item_linked_group_list")

        for row in table:
            cat_name = row["child_category_id"]
            
            if cat_name not in search_set:
                continue

            parent_item = cif.as_string(row["parent_name"])
            parent_frame = block.find_frame(parent_item)
            child_item = cif.as_string(row["child_name"])
            child_frame = block.find_frame(child_item)

            description = cif.as_string(parent_frame.find_value('_item_description.description'))
            type_code = self._strip_value(parent_frame.find_value('_item_type.code'))
            default_value = self._strip_value(parent_frame.find_value('_item_default.value'))
            full_name = child_item
            name = self._strip_value(full_name).split('.')[1]
            mandatory_code = child_frame.find_value('_item.mandatory_code') == 'yes'

            items[full_name] = Item(full_name, name, description, mandatory_code, type_code, default_value)
        return items

    def _parse_item(self, frame):
        full_name = frame.name
        name = self._strip_value(frame.find_value('_item.name')).split('.')[1]
        description = self._strip_value(frame.find_value('_item_description.description'))
        mandatory_code = frame.find_value('_item.mandatory_code') == 'yes'
        type_code = self._strip_value(frame.find_value('_item_type.code'))
        default_value = self._strip_value(frame.find_value('_item_default.value'))

        return Item(full_name, name, description, mandatory_code, type_code, default_value)

    def _parse_category(self, frame):
        id = frame.name
        description = self._strip_value(frame.find_value('_category.description'))
        key_names = []
        if frame.find_value('_category_key.name'):
            kn = frame.find_value('_category_key.name')
            key_names.append(self._strip_value(kn).split('.')[1])
        else:
            # try to find in a loop
            table = frame.find_loop("_category_key.name")
            if table:
                for row in table:
                    key_names.append(self._strip_value(row).split('.')[1])

        return Category(id, description, key_names)

    def _strip_value(self, value):
        if value is None:
            return None

        return value.strip('"').strip(";").strip("'").strip()
