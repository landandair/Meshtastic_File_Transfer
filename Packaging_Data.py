import random


def split_data(path, packet_size=230):
    """Splits data into byte arrays and stores them into a dictionary to allow for easy recall of missing packets
    inputs:
    -Compressed File name to be sent
    return:
    -Dictionary of packets
    """
    packets = []
    with open(path, "rb") as fi:
        buf = bytearray(fi.read(packet_size))
        while len(buf):
            packets.append(buf)
            buf = bytearray(fi.read(packet_size))
    packet_dict = dict(enumerate(packets))
    return packet_dict


def package_data(byte_dict: dict, file_id_num: int):
    """Add file_id byte followed by a packet number byte to the beginning
    inputs:
    -byte_dict: dictionary made by split_data
    return:
    -file_id_num: of packets
    """
    for key in byte_dict.keys():
        byte_dict[key].insert(0, key)
        byte_dict[key].insert(0, file_id_num)
        byte_dict[key] = bytes(byte_dict[key])
    return byte_dict


def send_packets_dict_to_file(byte_dict: dict, file_name='Sending/packets.txt'):
    with open(file_name, "wb") as fi:
        for b_list in byte_dict.values():
            fi.write(bytes(b_list))


def make_initial_req(file_name: str, packet_num, id):
    return f'!fcom,file:{file_name},packets:{packet_num},id:{id}'

def decode_initial_req(string: str):
    """Returns file_name, packet_num, and file id of request
    ex:!fcom,file:rImages/image-file-compressed.webp,packets:21,id:194"""
    fields = string.split(',')
    ret = {}
    for field in fields[1:]:
        field = field.split(':')
        ret[field[0]] = field[1]
    file_name = ret['file']
    f_id = int(ret['id'])
    num = int(ret['packets'])
    return file_name, f_id, num


def make_status_packet(file_id: int, packet_type: int, opt_data: list = []):
    """makes communication packets to use for talking about the file transfer state
    inputs:
        -file_id: int of what id this is talking about
        -packet_type: {0: Deny initial Request, 1: Confirm Initial Request, 2: Done Transmitting,
        3: Need Packets(list Packets after one byte at a time), 4: Received all Packets(finished)}
        -opt_data: List of integers or bytes
    Returns:
        - packet = bytes(f, c, o, m, file_num, packet_type, opt data...)
    """
    packet = bytearray('fcom'.encode('utf8'))
    packet.append(file_id)
    packet.append(packet_type)
    for data in opt_data:
        packet.append(data)
    return packet


def send_packets_list_to_file(byte_list: list, file_name='Sending/radio_packets.txt'):
    with open(file_name, "wb") as fi:
        for b_list in byte_list:
            fi.write(bytes(b_list))

