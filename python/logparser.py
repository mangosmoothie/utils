from builtins import print
import sys
import getopt
import os
import re
import datetime



#####################################################################
#
# SIMPLE LOG PARSER - READS A LOG FILE, AGGREGATES THE RESULTS AND
# PRINTS A SUMMARY TXT AS WELL AS A DETAIL CSV FOR USE WITH XL
#
# REQUIRES PYTHON 3.X
#
#
# SIMPLY CALL THIS SCRIPT FROM YOUR FAVORITE SHELL TO USE: python.exe logparser.py -i C:\logs\log.out
#


time_pattern = r'\d{1,2}:\d{2}:\d{2}'
time_pattern_am_pm = r'\d{1,2}:\d{2}:\d{2}(\s(A|P)M)?'

def parse_file(input_file_location):
    print('starting file parsing')

    last_line = ''
    events = []
    # total seconds - num of occurrences - average seconds
    event_summary = {}

    current_ag = ''

    with open(input_file_location) as fileobject:
        for line in fileobject:
            if check_for_main_event(line):
                if line.startswith('INFO: STARTING DISTRIBUTION FOR AG:'):
                    current_ag = line.split(':')[2].replace('\n', '')
                time = re.search(time_pattern, last_line)
                event_key = get_event_key(line.replace('\n', ''))
                events.append([current_ag, event_key, time.group()])
                event_summary.update({event_key: [0, 0, 0]})
            last_line = line

    total_exec_time = 0

    for i in range(len(events)):
        if i + 1 < len(events):
            s1 = [int(x) for x in events[i][2].split(':')]
            s2 = [int(x) for x in events[i + 1][2].split(':')]
            d1 = datetime.datetime(2015, month=1, day=1, hour=s1[0], minute=s1[1], second=s1[2])
            d2 = datetime.datetime(2015, month=1, day=1, hour=s2[0], minute=s2[1], second=s2[2])
            exec_time = (d2-d1).total_seconds()
            total_exec_time += exec_time
            events[i].append(exec_time)
            es = event_summary.get(events[i][1])
            es[0] += exec_time
            es[1] += 1

    print_above_execution_time(events, event_summary)

    for i in event_summary.keys():
        print('\n\n' + str(i).replace('\n', ''))
        print('TOTAL SECONDS: ' + str(event_summary.get(i)[0]))
        print('AVERAGE DURATION: ' + str(round(event_summary.get(i)[0] / event_summary.get(i)[1], 2)) + ' SECONDS')
        print('TOTAL RUNS: ' + str(event_summary.get(i)[1]))

    summary = 'TOTAL EXECUTION TIME: '+str(total_exec_time)+' SECONDS ('+str(round(total_exec_time/60))+' MINUTES)'
    print(summary)

    return [events, event_summary, summary]


def print_above_execution_time(events, event_summary):
    for i in range(len(events) - 1):
        es = event_summary.get(events[i][1])
        events[i].append(round(es[0]/es[1], 2))
        if 0 < events[i][4] and 0 < events[i][3]:
            events[i].append(str(100 * round((events[i][3]-events[i][4])/events[i][4], 4)) + '%')
        else:
            events[i].append('')


def get_event_key(event_line):
    if ':' in event_line:
        parts = str(event_line).split(':')
        if len(parts) > 1:
            return parts[1]
        return parts[0]
    return event_line


def check_for_main_event(log_line):
    if log_line.startswith('INFO: STARTING DISTRIBUTION FOR AG:'):
        return True
    if log_line.startswith('INFO: CD->'):
        return True
    return False


def main(argv):
    input_file = ''
    output_file = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["input=", "output="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    if len(opts) == 0:
        print_usage()
        sys.exit()
    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("-i", "--input"):
            input_file = arg
        elif opt in ("-o", "--output"):
            output_file = arg
    print('Input file is ', input_file)
    print('Output file is ', output_file)

    if not os.path.exists(input_file):
        print('file not found at location: ' + input_file)
        sys.exit(2)

    result = parse_file(input_file)
    if output_file != '':
        with open(output_file, 'w') as f:
            for r in result[0]:
                f.write(','.join([str(x) for x in r]) + '\n')
        with open(output_file + '.txt', 'w') as f:
            f.write(result[2] + '\n')
            for i in result[1].keys():
                f.write(i + '\n')
                f.write('TOTAL EXECUTION TIME: ' + str(result[1].get(i)[0]) + ' SECONDS\n')
                f.write('AVERAGE DURATION: ' + str(round(result[1].get(i)[0] / result[1].get(i)[1], 2)) + ' SECONDS\n')
                f.write('TOTAL RUNS FOR STEP: ' + str(result[1].get(i)[1]) + '\n')
                f.write('\n')


def print_usage():
    print('usage: logparser.py -i <input log file> -o <output file>')

if __name__ == "__main__":
    main(sys.argv[1:])
