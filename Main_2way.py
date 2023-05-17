"""Land_and_air
Connect 2 Radios to the USB ports running meshtastic and then run the file. A progress bar should show up
100%|██████████| 21/21 [02:50<00:00,  8.14s/packet] (ex. progress bar)
"""


import time
from meshtastic.serial_interface import SerialInterface
from meshtastic.util import findPorts
from pubsub import pub
from File_Class_Manager import FileTransManager
Text_Queue1 = []
Queue1 = []


def main(interface_1, interface_2):
    file_name = 'compressed_audio.mp3'
    Manager_1 = FileTransManager(interface_1)  # Sender
    Manager_2 = FileTransManager(interface_2)  # Receiver
    destination_id = interface_2.getMyNodeInfo()['user']['id']
    print(f'Starting transfer of {file_name} to {destination_id}')
    Manager_1.send_new_file(file_name, destination_id)
    looping = True
    while looping:
        time.sleep(1)  # For performance lol
        # Sending update
        Manager_1.update_all()
        Manager_2.update_all()
        if Queue1:
            name, packet = Queue1.pop(0)
            payload = packet['decoded']['payload']
            if name == interface_1.getShortName():  # Sender
                Manager_1.new_data_packet(bytearray(payload))
            elif name == interface_2.getShortName():  # Receiver
                Manager_2.new_data_packet(bytearray(payload))
        if Text_Queue1:
            name, packet = Text_Queue1.pop(0)
            text = packet['decoded']['text']
            if text[0:5] == '!fcom' and name == interface_2.getShortName():
                Manager_2.new_req_packet(text, packet['fromId'])
            else:
                print(f'Receiver_received {text}')

        if len(Manager_1.transfer_objects) == 0 and len(Manager_2.transfer_objects) == 0:
            looping = False
        elif len(Manager_1.transfer_objects) == 0:
            print(Manager_2.transfer_objects)
    interface_1.close()
    interface_2.close()

def on_receive(packet, interface): # called when a packet arrives
    # print(packet['decoded']['portnum'], interface.getShortName())
    # print(f'received_1: {packet["decoded"]["payload"]}')
    if packet['decoded']['portnum'] == 'IP_TUNNEL_APP':
        Queue1.append((interface.getShortName(), packet))
    elif packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':
        Text_Queue1.append((interface.getShortName(), packet))


if __name__ == '__main__':
    try:
        ports = findPorts(True)
        print(f'Number of Radios: {len(ports)}')
        interface_1 = SerialInterface(devPath=ports[0])
        pub.subscribe(on_receive, "meshtastic.receive")
        interface_2 = SerialInterface(devPath=ports[1])
        main(interface_1, interface_2)
    except KeyboardInterrupt:
        interface_1.close()
        interface_2.close()
        print('closed')
