# Write the python class into an XML format file compatible with the 4diac IDE.
import xml.etree.ElementTree as ET
from datetime import datetime

from diac.adapter import AdapterType, generate_generic_adapter
from diac.function_block import InterfaceList, Event, VarDeclaration, FunctionBlock, MetaData, Plug, AdapterDeclaration
from diac.fb_network import FunctionBlockNetwork
from diac.types import generate_complex_datatype_struct, IEC61499Converter
from radio.block import Block

def write_to_file(file_path, content):
    with open(file_path, 'w+') as file:
        file.write(content)


def check_file(file_path):
    try:
        with open(file_path, 'r'):
            return True
    except FileNotFoundError:
        return False


def generate_complex_type(filepath):
    complex_struct = generate_complex_datatype_struct()
    write_to_file(filepath + '/COMPLEX.dtp', complex_struct)


def generate_adapters(filepath, complex_or_real):
    adapter = generate_generic_adapter(complex_or_real)
    write_to_file(filepath + "/GenericAdapter_" + complex_or_real + ".adp", adapter)


def create_meta_data():
    return MetaData(standard="61499-2", version="1.0", author="radio2diac", date=datetime.now().strftime("%Y-%m-%d"),
                    package_name="gnu_radio")


def create_function_block(radio_block: Block):
    meta_data = create_meta_data()
    complex_or_real = "COMPLEX" if radio_block.type == "complex" else "Real"
    interface_example = create_interface(radio_block.parameters, radio_block.has_inputs, radio_block.has_outputs,
                                         complex_or_real)
    fb = FunctionBlock(name=str(radio_block.id).upper(), interface_list=interface_example, meta_data=meta_data)

    # Bind the variables to the events
    for var in interface_example.input_vars:
        fb.add_var_to_event("REQ", var.name)
        if fb.interface_list.plugs is not None:
            fb.add_adapter_to_event("REQ", "Data")
    for var in interface_example.output_vars:
        fb.add_var_to_event("CNF", var.name)
        if fb.interface_list.sockets is not None:
            fb.add_adapter_to_event("CNF", "Data")
    return fb


def create_interface(parameters: dict[str, str], is_input: bool, is_output: bool, complex_or_real: str):
    interface_list = InterfaceList()

    # Convert the parameters to IEC61499 data types
    converter = IEC61499Converter(parameters)
    parameters = converter.convert()

    # Create InputVars
    for parameter in parameters:
        interface_list.add_input_var(
            VarDeclaration(name=parameter[0].capitalize(), var_type=parameter[2],
                           comment=f"Input parameter {parameter[0]}"))

    # Decide if socket or plug is needed
    if is_input > 0:
        socket = AdapterDeclaration(name="DataIn", type_name="gnu_radio::GenericAdapter_" + complex_or_real,
                                    comment="Socket for Adapter")
        interface_list.add_socket(socket)
    if is_output > 0:
        plug = AdapterDeclaration(name="DataOut", type_name="gnu_radio::GenericAdapter_" + complex_or_real, comment="Plug for Adapter")
        interface_list.add_plug(plug)

    return interface_list


def generate_fb_xml(parameters):
    fb = create_function_block(parameters)
    fb_xml = fb.to_xml()
    xml = ET.tostring(fb_xml, encoding='utf8', method='xml').decode()
    # Search for utf8 and replace it with utf-8 due to how Eclipse 4diac reads the data
    xml = xml.replace("utf8", "utf-8")
    return xml, fb.name


def generate_fbn(radio_blocks: list[Block], function_blocks: list[FunctionBlock]):
    network = FunctionBlockNetwork()

    # Get the Function Block Name
    for block in radio_blocks:
        for fb in function_blocks:
            if block.id.upper() == fb:
                network.add_function_block(block.name, "gnu_radio::" + str(fb), block.connections, block.parameters)
    fbn_xml = network.to_xml()
    return fbn_xml


def replace_subappnetwork_in_file(file_path, new_subappnetwork_xml):
    # Parse the existing XML file
    tree = ET.ElementTree()
    tree.parse(file_path)
    root = tree.getroot()

    # Find the existing <SubAppNetwork> element
    def find_and_replace_subappnetwork(element):
        for child in element:
            if child.tag == "SubAppNetwork":
                # Replace the <SubAppNetwork> element
                element.remove(child)
                new_subapp_elem = ET.fromstring(new_subappnetwork_xml)
                element.append(new_subapp_elem)
                return True
            # Recursively search child elements
            if find_and_replace_subappnetwork(child):
                return True
        return False

    if not find_and_replace_subappnetwork(root):
        raise ValueError("No <SubAppNetwork> element found in the file.")
    xml = ET.tostring(root, encoding="utf8", method="xml").decode()
    xml = xml.replace("utf8", "utf-8")
    write_to_file(file_path, xml)
