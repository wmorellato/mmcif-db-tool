import logging

from gemmi import cif
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Item:
    full_name: str
    name: str
    description: str
    mandatory_code: bool
    type_code: str
    default_value: str
    index: bool = field(default=False)

    def __hash__(self) -> int:
        return hash(self.full_name)


@dataclass
class Category:
    id: str
    description: str
    key_names: list[str]
    items: list[Item] = field(default_factory=list)

    def add_item(self, item: Item):
        if item.name in self.key_names:
            item.index = True
        self.items.append(item)


class DictReader:
    def __init__(self, path: str) -> None:
        self._doc = cif.read_file(path)

    def get_categories(self, categories: list[str]) -> list[Category]:
        cat_objs = []
        block = self._doc.sole_block()
        search_set = set(categories)
        grouped_items = self._find_grouped_items(block, search_set)

        current_category = None
        for i in block:
            if i.frame is None:
                continue

            frame = i.frame
            if frame.name in search_set:
                logger.debug(f"Found category {frame.name}")

                if current_category is not None:
                    cat_objs.append(current_category)

                current_category = self._parse_category(frame)
                continue

            if current_category is None:
                continue

            if self._cat_from_frame(frame.name) != current_category.id:
                logger.debug(f"Finished category {current_category.id}. Frame name: {frame.name}")
                cat_objs.append(current_category)
                current_category = None
                continue

            if frame.name in grouped_items:
                logger.debug(f"Found grouped item {frame.name}")
                current_category.add_item(grouped_items[frame.name])
                continue

            if frame.find_value("_item.name"):
                logger.debug(f"Found item {frame.name}")
                item = self._parse_item(frame)
                current_category.add_item(item)
                continue

        if current_category is not None:
            # I think this can happen for the last category
            # in the dictionary
            cat_objs.append(current_category)
        return cat_objs

    def _cat_from_frame(self, frame_name):
        if frame_name is not None:
            return frame_name.lstrip("_").split('.')[0]

    def _find_grouped_items(self, block, search_set):
        # this is to find items defined in loops for
        # categories that have a group
        items = {}
        for i in block:
            if i.frame is None:
                continue

            frame = i.frame
            if not frame.find_loop("_item.name"):
                continue

            table = frame.find(["_item.name", "_item.category_id", "_item.mandatory_code"])
            for row in table:
                if row[1] in search_set:
                    full_name = cif.as_string(row[0])
                    name = self._strip_value(row[0]).split('.')[1]
                    description = cif.as_string(frame.find_value('_item_description.description'))
                    mandatory_code = row[2] == 'yes'
                    type_code = self._strip_value(frame.find_value('_item_type.code'))
                    default_value = self._strip_value(frame.find_value('_item_default.value'))

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

        return value.strip('"').strip(";").strip()


# table infos
# description: _category.description
# name: _category.id
# index: _category_key.name

# column infos
# name: _item.name
# type: _item_type.code 
# nullable: _item.mandatory_code
# default value: _item_default.value
# foreign key: _item_linked.child_name