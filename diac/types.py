# This file holds the type convertion from GNU Radio to IEC 61499 and type generation for IEC 61499 data types.
from datetime import datetime
from xml.etree.ElementTree import SubElement, Element, tostring

from diac.function_block import MetaData


class IEC61499Converter:
    def __init__(self, data):
        self.data = data

    def determine_type(self, value):
        """Determine the IEC 61499 data type based on the value."""
        if isinstance(value, int) or value.isdigit():
            return "INT"
        try:
            float(value)
            return "REAL"
        except ValueError:
            pass
        if value == "True" or value == "False":
            return "BOOL"
        if value == "COMPLEX":
            return "COMPLEX"

        return "STRING"  # Default to STRING for other types

    def convert(self):
        """Convert the dictionary to IEC 61499 datatype format."""
        converted_data = []
        for key, value in self.data.items():
            iec_type = self.determine_type(value)
            converted_data.append([key, float(value) if iec_type == "REAL" else value, iec_type])
        return converted_data


class StructuredType:
    def __init__(self):
        self.variables = []

    def add_variable(self, name, var_type):
        self.variables.append((name, var_type))

    def to_xml(self, parent):
        structured_type_elem = SubElement(parent, "StructuredType")
        for name, var_type in self.variables:
            SubElement(structured_type_elem, "VarDeclaration", Name=name, Type=var_type)
        return structured_type_elem


# Generate a complex data type using a IEC 61499 struct
def generate_complex_datatype_struct():
    struct_elem = Element("DataType", Name="COMPLEX", Comment="Complex data type for GNU Radio")

    # MetaData Example
    metadata = MetaData(standard="61499-2", version="1.0", author="radio2diac",
                        date=datetime.now().strftime("%Y-%m-%d"),
                        package_name="gnu_radio")
    metadata.to_xml(struct_elem)

    # StructuredType Example
    structured_type = StructuredType()
    structured_type.add_variable("Re", "REAL")
    structured_type.add_variable("Im", "REAL")
    structured_type.to_xml(struct_elem)

    xml = tostring(struct_elem, encoding="utf8", method="xml").decode().replace("utf8", "utf-8")
    return xml
