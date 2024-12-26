"""Take a File and split it into a bunch of files in a directory"""
import argparse
import sys
import os


def main():
    args = parser.parse_args()
    file_name = args.file_name
    buffer_size = 51_200

    fname = os.path.basename(file_name)
    name, ext = os.path.splitext(fname)
    dirname = os.path.dirname(file_name)
    new_dir_name = dirname + '/' + name
    os.makedirs(new_dir_name, exist_ok=True)
    with open(file_name, 'rb') as f:
        buff = f.read(buffer_size)
        n = 1
        while buff:
            with open(f'{new_dir_name}/{name}_{n}{ext}', 'wb') as wf:
                wf.write(buff)
            buff = f.read(buffer_size)
            n += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='File splitter',
        description='Take a File and split it into a bunch of files in a directory', )
    parser.add_argument('-f', '--file_name', help='File to split')
    main()
