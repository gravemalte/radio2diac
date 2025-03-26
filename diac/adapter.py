from datetime import datetime
from xml.etree.ElementTree import SubElement, Element, tostring

from diac.function_block import MetaData


MAX_ARRAY_SIZE = 4096

class AdapterType:
    def __init__(self):
        self.interface_list = []
        self.services = []

    def add_event_input(self, name, var):
        self.interface_list.append(("EventInput", name, var))

    def add_event_output(self, name, var):
        self.interface_list.append(("EventOutput", name, var))

    def add_input_var(self, name, var_type, comment):
        self.interface_list.append(("InputVar", name, var_type, comment))

    def add_output_var(self, name, var_type, comment):
        self.interface_list.append(("OutputVar", name, var_type, comment))

    def add_service_sequence(self, name, transactions):
        self.services.append((name, transactions))

    def to_xml(self, parent):
        # Add meta data
        metadata = MetaData(standard="61499-1", version="1.0", author="radio2diac",
                            date=datetime.now().strftime("%Y-%m-%d"),
                            package_name="gnu_radio")
        metadata.to_xml(parent)

        interface_list_elem = SubElement(parent, "InterfaceList")
        event_inputs_elem = SubElement(interface_list_elem, "EventInputs")
        event_outputs_elem = SubElement(interface_list_elem, "EventOutputs")
        input_vars_elem = SubElement(interface_list_elem, "InputVars")
        output_vars_elem = SubElement(interface_list_elem, "OutputVars")

        for item in self.interface_list:
            if item[0] == "EventInput":
                event_elem = SubElement(event_inputs_elem, "Event", Name=item[1], Type="Event")
                SubElement(event_elem, "With", Var=item[2])
            elif item[0] == "EventOutput":
                event_elem = SubElement(event_outputs_elem, "Event", Name=item[1], Type="Event")
                SubElement(event_elem, "With", Var=item[2])
            elif item[0] == "InputVar":
                SubElement(input_vars_elem, "VarDeclaration", Name=item[1], Type=item[2], Comment=item[3])
            elif item[0] == "OutputVar":
                SubElement(output_vars_elem, "VarDeclaration", Name=item[1], Type=item[2], ArraySize="0.." + str(MAX_ARRAY_SIZE), Comment=item[3])

        service_elem = SubElement(parent, "Service", RightInterface="SOCKET", LeftInterface="PLUG",
                                  Comment="Adapter Interface")
        for name, transactions in self.services:
            sequence_elem = SubElement(service_elem, "ServiceSequence", Name=name)
            for input_primitive, output_primitive in transactions:
                transaction_elem = SubElement(sequence_elem, "ServiceTransaction")
                SubElement(transaction_elem, "InputPrimitive", Interface=input_primitive[0], Event=input_primitive[1],
                           Parameters=input_primitive[2])
                SubElement(transaction_elem, "OutputPrimitive", Interface=output_primitive[0],
                           Event=output_primitive[1], Parameters=output_primitive[2])
        return parent


def generate_generic_adapter(type_of_data: str):
    adapter_elem = Element("AdapterType", Name="GenericAdapter_"+type_of_data, Comment="Generic Adapter for GNU Radio")
    adapter = AdapterType()
    if type_of_data == "COMPLEX":
        type_of_data = "gnu_radio::COMPLEX"

    adapter.add_event_output("CNF", "CNFD")
    adapter.add_output_var("CNFD", type_of_data, "Confirmation Data from Plug")
    adapter.add_service_sequence("request_confirm", [
        (("SOCKET", "REQ", "REQD"), ("PLUG", "REQ", "REQD")),
        (("PLUG", "CNF", "CNFD"), ("SOCKET", "CNF", "CNFD"))
    ])
    adapter.add_service_sequence("indication_response", [
        (("PLUG", "IND", "INDD"), ("SOCKET", "IND", "INDD")),
        (("SOCKET", "RSP", "RSPD"), ("PLUG", "RSP", "RSPD"))
    ])

    adapter.to_xml(adapter_elem)

    xml = tostring(adapter_elem, encoding='utf8', method='xml').decode().replace("utf8", "utf-8")
    return xml
