# Class that holds an IEC 61499 Eclipse 4diac compatible function block representation
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree


class FunctionBlock:
    def __init__(self, name, meta_data, interface_list, comment=None):
        self.name = name
        self.comment = comment
        self.meta_data = meta_data
        self.interface_list = interface_list

    def add_socket(self, socket):
        self.interface_list.add_socket(socket)

    def add_plug(self, plug):
        self.interface_list.add_plug(plug)

    def add_event_input(self, event):
        self.interface_list.add_event_input(event)

    def add_event_output(self, event):
        self.interface_list.add_event_output(event)

    def add_input_var(self, var):
        self.interface_list.add_input_var(var)

    def add_output_var(self, var):
        self.interface_list.add_output_var(var)

    def add_var_to_event(self, event_name, var_name):
        for event in self.interface_list.event_inputs:
            if event.name == event_name:
                event.add_with_var(var_name)
                return
        for event in self.interface_list.event_outputs:
            if event.name == event_name:
                event.add_with_var(var_name)
                return

    def add_adapter_to_event(self, event_name, adapter_name):
        for event in self.interface_list.event_inputs:
            if event.name == event_name:
                event.add_with_var(adapter_name)
                return
        for event in self.interface_list.event_outputs:
            if event.name == event_name:
                event.add_with_var(adapter_name)
                return

    def to_xml(self):
        fb_elem = Element("FBType")
        fb_elem.set("Name", self.name)
        if self.comment:
            fb_elem.set("Comment", self.comment)
        else:
            fb_elem.set("Comment", "This is a generated function block of type " + self.name)

        # Add MetaData
        self.meta_data.to_xml(fb_elem)

        # Add InterfaceList
        interface_list_elem = self.interface_list.to_xml()
        fb_elem.append(interface_list_elem)

        # A dummy ECC
        basic_fb_elem = SubElement(fb_elem, "BasicFB")
        ecc_elem = SubElement(basic_fb_elem, "ECC")
        ecstate_elem = SubElement(ecc_elem, "ECState", Name="START", Comment="Initial State", x="475", y="1125")
        ecstate_elem.text = ''  # Ensure explicit closing tag

        return fb_elem


class MetaData:
    def __init__(self, standard, version, author, date, package_name):
        self.standard = standard
        self.version = version
        self.author = author
        self.date = date
        self.package_name = package_name

    def to_xml(self, parent):
        ident_elem = SubElement(parent, "Identification", Standard=self.standard)
        ident_elem.text = ' \n'
        version_elem = SubElement(parent, "VersionInfo", Version=self.version, Author=self.author, Date=self.date)
        version_elem.text = ' \n'
        compiler_elem = SubElement(parent, "CompilerInfo", packageName=self.package_name)
        compiler_elem.text = ' \n'
        return ident_elem, version_elem, compiler_elem


class Event:
    def __init__(self, name, event_type, comment=None):
        self.name = name
        self.type = event_type
        self.comment = comment
        self.with_vars = []

    def add_with_var(self, var_name):
        self.with_vars.append(var_name)

    def to_xml(self, parent):
        event_elem = SubElement(parent, "Event", Name=self.name, Type=self.type)
        if self.comment:
            event_elem.set("Comment", self.comment)
        #for var in self.with_vars:
            # SubElement(event_elem, "With", Var=var)
        return event_elem


class Plug:

    def to_xml(self, parent):
        plug_elem = SubElement(parent, "Plug")
        return plug_elem


class Socket:

    def to_xml(self, parent):
        socket_elem = SubElement(parent, "Socket")
        return socket_elem


class VarDeclaration:
    def __init__(self, name, var_type, comment=None):
        self.name = name
        self.type = var_type
        self.comment = comment

    def to_xml(self, parent):
        attributes = {"Name": self.name, "Type": self.type}
        if self.comment:
            attributes["Comment"] = self.comment
        return SubElement(parent, "VarDeclaration", **attributes)


class AdapterDeclaration:
    def __init__(self, name, type_name, comment=None):
        self.name = name
        self.type_name = type_name
        self.comment = comment

    def to_xml(self, parent):
        attributes = {"Name": self.name, "Type": self.type_name}
        if self.comment:
            attributes["Comment"] = self.comment
        return SubElement(parent, "AdapterDeclaration", **attributes)


class InterfaceList:
    def __init__(self):
        self.event_inputs = []
        self.event_outputs = []
        self.input_vars = []
        self.output_vars = []
        self.sockets = []
        self.plugs = []

    def add_socket(self, socket):
        self.sockets.append(socket)

    def add_plug(self, plug):
        self.plugs.append(plug)

    def add_event_input(self, event):
        self.event_inputs.append(event)

    def add_event_output(self, event):
        self.event_outputs.append(event)

    def add_input_var(self, var):
        self.input_vars.append(var)

    def add_output_var(self, var):
        self.output_vars.append(var)

    def to_xml(self):
        interface_list_elem = Element("InterfaceList")

        # Add EventInputs
        if self.event_inputs:
            event_inputs_elem = SubElement(interface_list_elem, "EventInputs")
            for event in self.event_inputs:
                event.to_xml(event_inputs_elem)

        # Add EventOutputs
        if self.event_outputs:
            event_outputs_elem = SubElement(interface_list_elem, "EventOutputs")
            for event in self.event_outputs:
                event.to_xml(event_outputs_elem)

        # Add InputVars
        if self.input_vars:
            input_vars_elem = SubElement(interface_list_elem, "InputVars")
            for var in self.input_vars:
                var.to_xml(input_vars_elem)

        # Add OutputVars
        if self.output_vars:
            output_vars_elem = SubElement(interface_list_elem, "OutputVars")
            for var in self.output_vars:
                var.to_xml(output_vars_elem)

        # Add Sockets
        if self.sockets:
            sockets_elem = SubElement(interface_list_elem, "Sockets")
            for socket in self.sockets:
                socket.to_xml(sockets_elem)

        # Add Plugs
        if self.plugs:
            plugs_elem = SubElement(interface_list_elem, "Plugs")
            for plug in self.plugs:
                plug.to_xml(plugs_elem)

        return interface_list_elem


class Adapter:
    def __init__(self, name, adapter_type):
        self.name = name
        self.adapter_type = adapter_type
        self.connections = {}

    def add_connection(self, connection):
        self.connections[connection.src] = connection.dst

    def __str__(self):
        return f'Adapter({self.name}, {self.adapter_type}, {self.connections})'

    def __repr__(self):
        return str(self)
