from builtins import print
import getopt
import sys
import os
from time import clock

#####################################################################
#
# SIMPLE FILE SPLITTER
# SPLITS GIVEN FILE INTO X NUMBER OF MEGABYTE SIZED CHUNKS
#
# REQUIRES PYTHON 3.X
#
# AUTHOR: NATHAN LLOYD
#
# SIMPLY CALL THIS SCRIPT FROM YOUR FAVORITE SHELL TO USE: python.exe splitter.py -i C:\logs\log.out
#


def main(argv):
    start_time = clock()
    input_file = ''
    output_file_size = None
    try:
        opts, args = getopt.getopt(argv, "hi:s:", ["input=", "size="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    if len(opts) == 0:
        print_usage()
        sys.exit()
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt in ("-i", "--input"):
            input_file = arg
        elif opt in ("-s", "--size"):
            output_file_size = int(arg) * 1000000

    print('input file is ', input_file)
    if output_file_size is None:
        output_file_size = 100000000
    input_file_size = os.stat(input_file).st_size
    print('input file size is ', str(input_file_size // 1000000) + 'MB')
    print('output file size is ', str(output_file_size // 1000000) + 'MB')
    split_file(input_file, output_file_size, input_file_size)
    end_time = clock()
    print("time elapsed: " + str(round(end_time - start_time, 4)) + ' seconds')


def split_file(input_file_path, output_file_size, input_file_size):
    if not os.path.isfile(input_file_path):
        print('no file found at location: ' + input_file_path)
        sys.exit(2)

    max_file_index = input_file_size // output_file_size
    try:
        file_ext_index = input_file_path.rindex('.')
    except ValueError:
        file_ext_index = len(input_file_path)

    file_number = 0

    with open(input_file_path, 'rb') as f_in:
        while file_number <= max_file_index:
            chunk = f_in.read(output_file_size)
            out_file_path = input_file_path[:file_ext_index] + '-' + str(file_number) + input_file_path[file_ext_index:]
            out_file = open(out_file_path, 'wb')
            out_file.write(chunk)
            out_file.close()
            file_number += 1
            print('file: ' + out_file_path + ' successfully written!')

    print('file has been successfully split into ' + str(max_file_index + 1) + ' files of approx size '
          + str(output_file_size // 1000000) + 'MB')


def print_usage():
    print('usage: splitter.py -i <input file> [-s <output file size (MB)>]')
    print('-h for help')


def print_help():
    print('')
    print('simple file splitter')
    print('')
    print('takes a large input file and splits it into multiple output ')
    print('file of a given size')
    print('')
    print('params: -i --input    input file location (required)')
    print('params: -s --size     size of output files in megabytes: default is 100MB (optional)')
    print('')
    print_usage()


if __name__ == "__main__":
    main(sys.argv[1:])
