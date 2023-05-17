import os
from PIL import Image
from pydub import AudioSegment


def compress_image(image_file):
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

def compress_audio(audio_file):
    file_name = "Files/compressed_audio.mp3"
    audio = AudioSegment.from_file(audio_file)[:22000]
    audio.export(file_name, format='mp3', parameters=["-ac","1","-ar","8000"])
    # low_sample_rate = audio.set_frame_rate(1)
    # low_sample_rate.export(file_name, bitrate="1k", format="mp3")
    return file_name


if __name__ == '__main__':
    filename = 'Files/Rick.mp3'
    compressed_file = compress_audio(filename)
    packets = []
    with open(compressed_file, "rb") as fi:
        packet_size = 232
        buf = fi.read(packet_size)
        while (buf):
            packets.append(buf)
            buf = fi.read(packet_size)
    print(len(packets))

