import plac
import xml.etree.ElementTree as ET
from datetime import datetime

stats_accumulate = dict()
channel_accumulate = dict()
channel_count = 0

def accumulate_by_date(Y,M,D):
    if Y in stats_accumulate:
        if M in stats_accumulate[Y]:
            if D in stats_accumulate[Y][M]:
                stats_accumulate[Y][M][D] += 1
            else:
                stats_accumulate[Y][M][D] = 1
        else:
            stats_accumulate[Y][M] = dict()
            stats_accumulate[Y][M][D] = 1
    else:
        stats_accumulate[Y] = dict()
        stats_accumulate[Y][M] = dict()
        stats_accumulate[Y][M][D] = 1

def accumulate_channel(channel):
    if channel.attrib['id'] in channel_accumulate:
        channel_accumulate[channel.attrib['id']] += 1
    else:
        channel_accumulate[channel.attrib['id']] = 1

def print_accumulate():
    print('Number of channels: ' + str(len(channel_accumulate)))
    print('Programs per day: ')
    for Y in stats_accumulate:
        for M in stats_accumulate[Y]:
            for D in stats_accumulate[Y][M]:
                print('\t{0} {1} {2}: {3}'.format(Y,M,D, stats_accumulate[Y][M][D]))

def main(stats: ('Print stats about the files','flag','s'),
        accumulate: ('Accumulate all input XMLTV files as if they where a single file', 'flag', 'a'),
        *xmltv_files):
    "Utility to inspect and manipulate XMLTV files"

    global channel_count

    for xmltv_file in xmltv_files:
        xmltv = ET.parse(xmltv_file)

        channels = xmltv.findall('./channel')
        programs = xmltv.findall('./programme')

        if stats:
            for channel in channels:
                accumulate_channel(channel)
                channel_count += 1

            for program in programs:
                start = datetime.strptime( program.attrib['start'], '%Y%m%d%H%M%S %z')
                accumulate_by_date(start.year, start.month, start.day)

            if not accumulate:
                print_accumulate()
                stats_accumulate.clear()
                channel_accumulate.clear()

    if stats and accumulate:
        print_accumulate()
        print('Total number of channels: ' + str(channel_count))


if  __name__ == '__main__':
    import plac; plac.call(main)
