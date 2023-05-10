import random
import file_classes
from Packaging_Data import decode_initial_req

class FileTransManager:
    def __init__(self, interface, send_delay=10, packet_len=232):
        self.transfer_objects = {}  # id: file_sender/file_receiver
        self.interface = interface
        self.send_delay = send_delay
        self.packet_len = packet_len

    def update_all(self):
        """Calls update method on each object"""
        deleted_keys = []
        for key in self.transfer_objects.keys():
            self.transfer_objects[key].update()
            if self.transfer_objects[key].kill:
                deleted_keys.append(key)

        for key in deleted_keys:
            self.transfer_objects.pop(key)

    def new_data_packet(self, packet):
        """Called to process new data packet"""
        if packet[0] == bytearray('f'.encode('utf8'))[0]:
            # print(f'com packet: {packet}')
            f_id = packet[4]
            self.transfer_objects[f_id].manage_com_packet(packet)
        elif packet[0] in self.transfer_objects.keys():
            # print(f'file packet received for {int(packet[0])}: {packet}')
            self.transfer_objects[packet[0]].add_packet(packet)
        else:
            print(f'something went Wrong: {packet}')

    def new_req_packet(self, initial_req, sending_id):
        """Called to make new file_receiving packet based on a request packet"""
        file_name, f_id, num = decode_initial_req(initial_req)
        self.transfer_objects[f_id] = file_classes.FileTransferReceiver(file_name, f_id, num, self.interface,
                                                                        sending_id, timeout=self.send_delay*4)

    def send_new_file(self, file_name, destination):
        """Called to make new file sending object"""
        file_id = random.randint(0, 256)
        while file_id == bytearray('f'.encode('utf8'))[0] or file_id in self.transfer_objects.keys():
            file_id = random.randint(0, 256)
        self.transfer_objects[file_id] = file_classes.FileTransferSender(file_name, file_id, self.interface,
                                                                         destination, self.send_delay, self.packet_len)
