from serial_core import Communication, port_list_number

class BittleX:
    def __init__(self, selected_port=None):
        if selected_port is None:
            Communication.Print_Used_Com()
            selected_port = port_list_number[0]  # Use first available port

        self.connection = Communication(selected_port, 115200, 0.5)

    def send_command(self, command):
        print(f"Sending: {command}")
        self.connection.Send_data((command + '\n').encode())

    def close(self):
        self.connection.Close_Engine()
