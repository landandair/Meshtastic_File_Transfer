"""Take a bunch of files in a directory and combine them into a single file"""
import argparse
import os

def main():
    args = parser.parse_args()
    dir_name = args.dir_name
    files = os.listdir(dir_name)
    order_dict = {}
    extension = None
    for file in files:
        name, ext = os.path.splitext(file)
        extension = ext
        num = int(name.split('_')[-1])
        order_dict[num] = file
    with open(dir_name + extension, 'wb') as wf:
        for i in sorted(order_dict.keys()):
            with open(f'{dir_name}/{order_dict[i]}', 'rb') as rf:
                wf.write(rf.read())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='File Combiner',
        description='Take a bunch of files in a directory and combine them into a single file', )
    parser.add_argument('-d', '--dir_name', help='directory to combine in format name_xx.ext')
    main()