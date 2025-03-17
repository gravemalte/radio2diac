from xml.etree.ElementTree import SubElement, Element, tostring


class FunctionBlockNetwork:
    def __init__(self):
        self.function_blocks = []
        self.adapter_connections = []
        self.event_connections = []
        self.fb_counters = {}  # To track FB types and ensure unique names
        self.x_base = 500  # Starting x-coordinate
        self.y_base = 1400  # Starting y-coordinate

    def add_function_block(self, name, fb_type, connections, parameters=None):
        if fb_type not in self.fb_counters:
            self.fb_counters[fb_type] = 0
        self.fb_counters[fb_type] += 1

        # Generate a unique name with a suffix if needed
        suffix = f"_{self.fb_counters[fb_type]}" if self.fb_counters[fb_type] > 1 else ""
        unique_name = f"{name}{suffix}"

        # Add FB details
        self.function_blocks.append({
            "name": unique_name,
            "type": fb_type,
            "parameters": parameters or [],
            "x": self.x_base,
            "y": self.y_base
        })

        # Increment x and y coordinates for the next FB
        self.x_base += 10
        self.y_base += 10

        # Event Store connections
        for connection in connections:
            self.event_connections.append({
                "source": f"{connection.src}.CNF",
                "destination": f"{connection.dst}.REQ"})

        # Adapter Store connections
        for connection in connections:
            self.adapter_connections.append({
                "source": f"{connection.src}.DataOut",
                "destination": f"{connection.dst}.DataIn"
            })

    def to_xml(self):
        sub_app_elem = Element("SubAppNetwork")

        # Add FB elements
        for fb in self.function_blocks:
            fb_elem = SubElement(sub_app_elem, "FB", Name=fb["name"], Type=fb["type"], x=str(fb["x"]), y=str(fb["y"]))

            # Check if fb["parameters"] is not a list
            if not isinstance(fb["parameters"], list):
                for param_name, param_value in fb["parameters"].items():
                    # If params does not contain numbers its a string enquote it with ''
                    try:
                        float(param_value)
                    except ValueError:
                        # Check if the value is a boolean
                        if not (param_value == "True" or param_value == "False"):
                            param_value = f"'{param_value}'"
                        else:
                            param_value = param_value
                    SubElement(fb_elem, "Parameter", Name=param_name.capitalize(), Value=param_value)
            else:
                for parameter in fb["parameters"]:
                    try:
                        float(parameter)
                    except ValueError:
                        # Check if the value is a boolean
                        if not (parameter == "True" or parameter == "False"):
                            parameter = f"'{parameter}'"
                        else:
                            parameter = parameter

                    SubElement(fb_elem, "Parameter", Name=parameter[0].capitalize(), Value=parameter[1])


        # EventConnections
        #event_connections_elem = SubElement(sub_app_elem, "EventConnections")
        #for connection in self.event_connections:
        #    SubElement(event_connections_elem, "Connection", Source=connection["source"],
        #               Destination=connection["destination"])

        # Add AdapterConnections
        adapter_connections_elem = SubElement(sub_app_elem, "AdapterConnections")
        for connection in self.adapter_connections:
            SubElement(adapter_connections_elem, "Connection", Source=connection["source"],
                       Destination=connection["destination"])

        return tostring(sub_app_elem, encoding="unicode", method="xml").replace("utf-8", "utf8")
