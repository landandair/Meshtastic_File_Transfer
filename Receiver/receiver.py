"""Land_and_air
Connect 2 Radios to the USB ports running meshtastic and then run the file. A progress bar should show up
100%|██████████| 36/36 [02:52<00:00,  4.79s/packet] (ex. progress bar) - Long Fast(4 sec send delay) 50 bytes/sec
100%|██████████| 36/36 [01:06<00:00,  1.84s/packet] - Medium Fast(1.6 sec sending delay) 138 bytes/sec
100%|██████████| 36/36 [00:15<00:00,  2.32packet/s] - Short Fast(.4 sec sending delay) 300-500 bytes/sec
"""
import os
os.path.join('..')
from serial.serialutil import SerialException
import sys
import time
from meshtastic.serial_interface import SerialInterface
from meshtastic.util import findPorts
from pubsub import pub
import argparse
from File_Class_Manager import FileTransManager
Text_Queue = []
Queue = []


def main(interface):
    args = parser.parse_args()
    # Args to be used
    time_out = int(args.time_out)
    auto_accept = args.auto_accept
    try:
        manager = FileTransManager(interface, auto_restart=auto_accept)  # Sender
        # Selecting the destination(to be changed)
        looping = True
        while looping:
            time.sleep(.05)  # For performance lol
            # Sending update
            manager.update_all()
            if Queue:  # Handle binary data
                name, packet = Queue.pop(0)
                payload = packet['decoded']['payload']
                manager.new_data_packet(bytearray(payload))
            if Text_Queue:  # handle text data
                name, packet = Text_Queue.pop(0)
                text = packet['decoded']['text']
                print(f'Text Received: {text}')
                if text[0:5] == '!fcom':
                    manager.new_req_packet(text, packet['fromId'], timeout=time_out)
        interface.close()
    except KeyboardInterrupt:
        sys.exit('\nUser Interrupted')


def on_receive(packet, interface): # called when a packet arrives
    # print(packet['decoded']['portnum'], interface.getShortName())
    # print(f'received_1: {packet["decoded"]["payload"]}')
    if packet['decoded']['portnum'] == 'IP_TUNNEL_APP':
        Queue.append((interface.getShortName(), packet))
    elif packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':
        Text_Queue.append((interface.getShortName(), packet))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Meshtastic File Receiver',
        description='Reveives a file or directory to another node running the receiver program',)
    parser.add_argument('-t', '--time_out', default=300, help='Time between packets before giving up')
    parser.add_argument('-a', '--auto_accept', default=False, help='Automatically accepts file transfers')
    ports = findPorts(True)
    print(f'Number of Radios: {len(ports)}')
    interface = None
    if ports:
        for port in ports:
            try:
                interface = SerialInterface(devPath=port)
                print(f'connected to {interface.getShortName()}')
                break
            except (BlockingIOError, SerialException) as e:
                pass
    if interface:
        pub.subscribe(on_receive, "meshtastic.receive")
        main(interface)
    else:
        sys.exit('Error: No Radio Available')
