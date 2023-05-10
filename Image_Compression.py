import os
from PIL import Image


def compress(image_file):
    comp_filename = "Files/image-file-compressed.webp"
    filepath = os.path.join(os.getcwd(), image_file)

    image = Image.open(filepath)

    base_width = 640
    width_percent = (base_width / float(image.size[0]))
    hsize = int(float(image.size[1]) * float(width_percent))
    image = image.resize((base_width, hsize))
    image.save(comp_filename,
               "webp",
               optimize=True,
               quality=0)
    return comp_filename

def zip_file(file_name):
    with open(file_name, 'rb') as fi:
        pass
    return file_name


if __name__ == '__main__':
    filename = 'Files/Image 7.jpeg'
    compress(filename)
    packets = []
    with open('Sending/image-file-compressed.webp', "rb") as fi:
        packet_size = 237
        buf = fi.read(packet_size)
        while (buf):
            packets.append(buf)
            buf = fi.read(packet_size)
    print(bin(int(255)))
    print(packets[0])
    print(len(packets))

