import os
import time
import Packaging_Data
from meshtastic import portnums_pb2
import tqdm

class FileTransferReceiver:
    """Class used to store and handle incoming file packets and should be created when the first request packet is
    acknowledged. Added to as the packets come in. Checked when the last packet number arrives or when a timeout is
    reached"""
    def __init__(self, file_name, file_id, num_packets, interface, sending_id, timeout=30, disable_bar=False):
        self.name = file_name
        self.id = file_id
        self.num_packets = int(num_packets)
        self.interface = interface
        self.sending_id = sending_id
        self.packet_dict = {}
        self.timeout = timeout + 10
        self.last_packet = time.time()
        self.progress_bar = tqdm.tqdm(total=num_packets, unit='packet', disable=disable_bar)
        initial_ack = Packaging_Data.make_status_packet(file_id, 1)  # Make ack array
        self.send_data(bytes(initial_ack))
        self.kill = False
        self.finished = False
        self.saved = False

    def update(self):
        if time.time()-self.last_packet > self.timeout:
            if self.get_missing_nums():  # Try to see if all the packets somehow made it
                print(f'File Transfer "{self.name}" Failed')
                self.progress_bar.close()
                self.kill = True
            else:
                self.save_to_file()
                self.kill = True
                self.progress_bar.close()

    def add_packet(self, packet: bytearray):
        """Send byte array received from radio and it will parse it and save it to the packet_dict
        -Returns true if it added it and false if it didn't"""
        self.last_packet = time.time()
        packet.pop(0)  # gives file id
        num = packet.pop(0)  # Packet index
        if num < self.num_packets:
            self.packet_dict[num] = packet
            self.progress_bar.update(1)
            if len(self.packet_dict) == self.num_packets:
                self.save_to_file()
            return True
        return False

    def manage_com_packet(self, packet: bytearray):
        """Receives and Responds to fcom Packets"""
        self.last_packet = time.time()
        packet_type = packet[5]
        if packet_type == 2:  # Done Transmitting
            missing_packets = self.get_missing_nums()
            if missing_packets:  # Ask for missing packets
                # print(missing_packets)
                ret_packet = Packaging_Data.make_status_packet(self.id, 3, opt_data=missing_packets)
            else:  # Let it know all packets are received
                ret_packet = Packaging_Data.make_status_packet(self.id, 4)
                self.save_to_file()
                self.kill = True
            self.send_data(ret_packet)

    def get_missing_nums(self):
        """Returns a list of missing packets based on the indexes stored in the packet_dict"""
        missing_nums = []
        for num in range(self.num_packets):
            if num not in self.packet_dict.keys():
                missing_nums.append(num)
        return missing_nums

    def save_to_file(self):
        check = self.get_missing_nums()
        if len(check) == 0 and not self.saved:
            self.progress_bar.close()
            os.makedirs(os.path.dirname(self.name), exist_ok=True)
            with open(self.name, 'wb') as fi:
                for num in range(self.num_packets):
                    fi.write(self.packet_dict[num])
            self.finished = True
            self.saved = self.finished
            return True
        return False

    def send_data(self, data):
        """Sends data over interface to destination"""
        self.interface.sendData(bytes(data), destinationId=self.sending_id, portNum=portnums_pb2.IP_TUNNEL_APP,
                                wantAck=False)


class FileTransferSender:
    """Class used to communicate and send files with a desired target. Sends Initial Packet, receives ack packets and
    sends packets and a confirmation packet at the end."""
    def __init__(self, file_name, file_id: int, interface, destination_id, send_delay=10, packet_len=218,
                 disable_bar=True):
        self.name = file_name
        self.id = file_id  # 0 Reserved for file meta packets
        self.interface = interface
        self.destination_id = destination_id
        self.packet_queue = []
        self.packet_len = packet_len
        data_dict = Packaging_Data.split_data(file_name, packet_len)  # Unlabeled
        self.data_dict = Packaging_Data.package_data(data_dict, self.id) # Labeled
        self.delay = send_delay
        self.packet_num = len(self.data_dict)
        self.last_send = time.time()
        # Modes- 0: Send Initial Packet, 2:Send Data, 3:Send Finish
        self.mode = 0
        self.kill = False
        self.finished = False
        # Send initial Req packet
        self.send_initial()
        self.disable_bar = disable_bar
        self.progress_bar = tqdm.tqdm(total=len(data_dict)+1, unit='packet', disable=self.disable_bar)
        self.progress_bar.update()
        self.min_delay = 10

    def send_initial(self):
        # Sends initial packet
        init_str = Packaging_Data.make_initial_req(self.name, len(self.data_dict), self.id)
        self.interface.sendText(init_str, destinationId=self.destination_id)

    def update(self):
        """-Sees if it has a packet to send and can send a packet and sends one if it can
        - Deletes itself if it's been too long and not heard anything"""
        if self.packet_queue and time.time()-self.last_send > self.delay:
            self.last_send = time.time()
            data = self.packet_queue.pop(0)
            # print(f'sending: {data}')
            self.interface.sendData(bytes(data), portNum=portnums_pb2.IP_TUNNEL_APP, destinationId=self.destination_id,
                                    wantAck=False)
            self.progress_bar.update()
        elif time.time()-self.last_send >= self.delay*self.packet_num and time.time()-self.last_send >= self.min_delay:
            print(time.time() - self.last_send)
            print('failed Send Timeout')

            self.kill = True

    def manage_com_packet(self, packet: bytearray):
        """Returns a list of missing packets based on the indexes stored in the packet_dict
        packet_types = {0: Deny initial Request, 1: Confirm Initial Request, 2: Done Transmitting,
        3: Need Packets(list Packets after one byte at a time), 4: Received all Packets(finished)}
        inputs:
            - packet = bytes(0, c, o, m, file_num, packet_type, opt data...)

        Mainly Adds to the sending queue in accordance with the received packet or deletes the object
        """
        packet_type = packet[5]
        if packet_type == 0:
            print('Sending Denied')
            self.kill = True
        elif packet_type == 1:  # First Pass
            for data in self.data_dict.values():
                self.packet_queue.append(data)
            self.packet_queue.append(Packaging_Data.make_status_packet(self.id, 2))
        elif packet_type == 3:  # Next Pass
            needed_packets = list(packet[6:])
            for num in needed_packets:
                self.packet_queue.append(self.data_dict[num])
            self.packet_queue.append(Packaging_Data.make_status_packet(self.id, 2))
            self.progress_bar.close()
            self.progress_bar = tqdm.tqdm(total=len(self.packet_queue), unit='packet', disable=self.disable_bar)
        else:
            self.progress_bar.close()
            print(f'Confirmed File Transfer #{self.id} Complete')
            self.finished = True
            self.kill = True
        self.last_send = time.time()
