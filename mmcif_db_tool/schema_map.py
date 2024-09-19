import sys
import logging

logger = logging.getLogger(__name__)

TYPE_MAP = {
    "text": ("tinytext",),
    "line": ("varchar", 128),
    "float": ("float",),
    "ucode": ("varchar", 10),
    "code": ("varchar", 20),
    "uline": ("varchar", 50),
    "int": ("int",),
    "uchar5": ("varchar", 6),
    "orcid_id": ("varchar", 20),
    "yyyy-mm-dd:hh:mm": ("date",),
    "pdbx_PDB_obsoleted_db_id": ("tinytext",),
    "pdbx_related_db_id": ("varchar", 80),
    "ec-type": ("varchar", 10),
    "uchar1": ("varchar", 2),
    "yyyy-mm-dd": ("datetime",),
    "3x4_matrix": ("tinytext",),
    "operation_expression": ("varchar", 511),
    "author": ("varchar", 150),
    "positive_int": ("int",),
    "atcode": ("varchar", 6),
    "symop": ("varchar", 10),
    "fax": ("varchar", 25),
    "phone": ("varchar", 25),
    "email": ("varchar", 80),
    "yyyy-mm-dd:hh:mm-flex": ("datetime",),
    "float-range": ("varchar", 30),
    "ucode-alphanum-csv": ("varchar", 25),
    "exp_data_doi": ("varchar", 80),
    "int-range": ("varchar", 20),
    "pdb_id_u": ("varchar", 20),
    "asym_id": ("varchar", 80),
    "point_group_helical": ("varchar", 5),
    "point_group": ("varchar", 20),
    "emd_id": ("varchar", 15),
    "boolean": ("varchar", 80),
    "pdb_id": ("varchar", 20),
    "3x4_matrices": ("varchar", 10),
    "symmetry_operation": ("varchar", 80),
    "id_list_spc": ("varchar", 200),
    "name": ("varchar", 80),
    "entity_id_list": ("tinytext",),
    "uniprot_ptm_id": ("varchar", 20),
    "binary": ("tinytext",),
}

ORM_IMPORTS = [
    "from typing import List", 
    "from typing import Optional", 
    "from sqlalchemy import ForeignKey", 
    "from sqlalchemy import String", 
    "from sqlalchemy.orm import DeclarativeBase", 
    "from sqlalchemy.orm import Mapped", 
    "from sqlalchemy.orm import mapped_column", 
    "from sqlalchemy.orm import relationship", 
]

CORE_IMPORTS = [
    "from sqlalchemy import MetaData, Table, Column, Integer, String, Float"
]

ORM_SETUP = ["class Base(DeclarativeBase):", "    pass"]

CORE_SETUP = ["metadata = MetaData()"]


def snakecase_to_camelcase(snake_str):
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)


class Table:
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns


class Column:
    def __init__(self, name, type, subtype = None, index=False, nullable=True, default=None):
        self.name = name
        self.type = type
        self.subtype = subtype
        self.index = index
        self.nullable = nullable
        self.default = default

    def __repr__(self):
        return f"Column({self.name}, {self.type}, {self.subtype}, {self.index}, {self.nullable}, {self.default})"


class SqlAlchemyCorePrinter:
    def __init__(self, fp = sys.stdout, include_imports=False):
        self._fp = fp
        self._include_imports = include_imports
        self._tables = []

    def add_table(self, table):
        self._tables.append(table)
    
    def _column_text(self, column):
        params = []
        if column.index:
            params.append("primary_key=True")
        if column.nullable:
            params.append(f"nullable={column.nullable}")
        if column.default is not None:
            params.append(f'default="{column.default!r}"')

        params_str = ", ".join(params)
        if params_str:
            return f'Column("{column.name}", {column.subtype}, {params_str})'
        else:
            return f'Column("{column.name}", {column.subtype})'

    def _table_text(self, table):
        columns = []
        for column in table.columns:
            print(column)
            columns.append(f"    {self._column_text(column)}")

        return f'{table.name} = Table("{table.name}",\n    metadata_obj,\n' + ",\n".join(columns) + "\n)"

    def print(self):
        if self._include_imports:
            for i in CORE_IMPORTS:
                self._fp.write(i + "\n")
            self._fp.write("\n\n")

        for table in self._tables:
            self._fp.write(self._table_text(table) + "\n\n")


class SqlAlchemyOrmPrinter:
    def __init__(self, fp = sys.stdout, include_imports=False):
        self._fp = fp
        self._include_imports = include_imports
        self._tables = []

    def add_table(self, table):
        self._tables.append(table)

    def _column_text(self, column):
        params = []
        if column.index:
            params.append("primary_key=True")
        if column.type == "str":
            params.append(f"type_={column.subtype}")
        if column.default is not None:
            params.append(f'default="{column.default!r}"')

        params_str = ", ".join(params)
        if column.nullable:
            return f'{column.name}: Mapped[Optional[{column.type}]] = mapped_column({params_str})'
        else:
            return f'{column.name}: Mapped[{column.type}] = mapped_column({params_str})'

    def _table_text(self, table):
        class_name = snakecase_to_camelcase(table.name)
        class_template = f"""class {class_name}(Base):
    __tablename__ = '{table.name}'\n\n"""
        
        for column in table.columns:
            class_template += f"    {self._column_text(column)}\n"

        return class_template

    def print(self):
        if self._include_imports:
            for i in ORM_IMPORTS:
                self._fp.write(i + "\n")
            self._fp.write("\n\n")

        for i in ORM_SETUP:
            self._fp.write(i + "\n")
        self._fp.write("\n\n")

        for table in self._tables:
            self._fp.write(self._table_text(table) + "\n\n")


class SchemaMap:
    def __init__(self, printer, ignore_relationships=False):
        self._printer = printer
        self._ignore_relationships = ignore_relationships
        self._categories = []

    def add_categories(self, categories):
        for category in categories:
            self._categories.append(category)

    def print_models(self):
        for c in self._categories:
            columns = []
            for item in c.items:
                itype, istype = self._type_map(item.type_code)

                if not itype:
                    logger.warning(f"Unknown type for {item.name}: {item.type_code}")
                    continue

                column = Column(item.name, itype, istype, index=item.index, nullable=item.mandatory_code, default=item.default_value)
                columns.append(column)

            table = Table(c.id, columns)
            self._printer.add_table(table)
        
        self._printer.print()
    
    def _type_map(self, itype_code):
        if itype_code in TYPE_MAP:
            if TYPE_MAP[itype_code][0] == "varchar":
                return "str", f"String({TYPE_MAP[itype_code][1]})"
            
            if TYPE_MAP[itype_code][0] == "tinytext":
                return "str", f"String(255)"
        
            if TYPE_MAP[itype_code][0] == "datetime":
                return "datetime.datetime", "DateTime"
            
            if TYPE_MAP[itype_code][0] == "date":
                return "datetime.date", "Date"
        
            if TYPE_MAP[itype_code][0] == "float":
                return "float", "Float"
            
            if TYPE_MAP[itype_code][0] == "int":
                return "int", "Integer"
            
            if TYPE_MAP[itype_code][0] == "boolean":
                return "bool", "Boolean"

            return TYPE_MAP[itype_code][0], None
        return None, None
