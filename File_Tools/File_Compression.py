import os
import zipfile
import argparse
from PIL import Image
from pydub import AudioSegment


def main():
    args = parser.parse_args()
    file_name = args.file_name
    quality_level = args.quality_level
    new_file = None
    try:
        new_file = compress_audio(file_name, quality_level)
    except IndexError as e:
        print('not an audio file')
    try:
        new_file = compress_image(file_name, quality_level)
    except IndexError as e:
        print('not an image file')
    if not new_file:
        new_file = replace_ext(file_name, 'zip')
        os.chdir(os.path.dirname(file_name))
        with zipfile.ZipFile(os.path.basename(new_file), "w", zipfile.ZIP_DEFLATED) as f:
            f.write(os.path.basename(file_name))
    print(f"saved file to {new_file}")


def replace_ext(fname, ext):
    dirname = os.path.dirname(fname)
    file = os.path.basename(fname)
    file = file.split('.')[0]
    comp_filename = f'{dirname}/{file}_compressed.{ext}'
    return comp_filename


def compress_image(image_file, quality):
    comp_filename = replace_ext(image_file, 'webp')
    # Compress image
    quality = (quality-1)*3
    filepath = os.path.join(os.getcwd(), image_file)
    image = Image.open(filepath)
    base_width = 540
    width_percent = (base_width / float(image.size[0]))
    hsize = int(float(image.size[1]) * float(width_percent))
    image = image.resize((base_width, hsize))
    image.save(comp_filename,
               "webp",
               optimize=True,
               quality=quality)
    return comp_filename

def compress_audio(audio_file, quality):
    comp_filename = replace_ext(audio_file, 'mp3')
    # Compress audio
    audio = AudioSegment.from_file(audio_file)
    audio.export(comp_filename, format='mp3', parameters=["-ac","1","-ar","8000"])
    return comp_filename


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='File Compressor',
        description='Take a File Compress it into an audio, image, or zip file', )
    parser.add_argument('-f', '--file_name', help='File to split')
    parser.add_argument('-q', '--quality_level', type=int, help='Level of detail for audio 1-5', default=1)
    main()

