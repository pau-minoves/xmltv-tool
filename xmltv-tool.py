import plac
import xml.etree.ElementTree as ET
from datetime import datetime

stats_accumulate = dict()
channel_accumulate = dict()
channel_count = 0

def accumulate_by_date(Y,M,D):
    if Y not in stats_accumulate:
        stats_accumulate[Y] = dict()
        stats_accumulate[Y][M] = dict()
    else:
        if M not in stats_accumulate[Y]:
            stats_accumulate[Y][M] = dict()

    if D in stats_accumulate[Y][M]:
        stats_accumulate[Y][M][D] += 1
    else:
        stats_accumulate[Y][M][D] = 1

def accumulate_channel(channel):
    if channel.attrib['id'] in channel_accumulate:
        channel_accumulate[channel.attrib['id']] += 1
    else:
        channel_accumulate[channel.attrib['id']] = 1

def print_accumulate():
    print('channels: ' + str(len(channel_accumulate)))
    print('programs: ')
    for Y in stats_accumulate:
        for M in stats_accumulate[Y]:
            for D in stats_accumulate[Y][M]:
                print('\t{0} {1} {2}: {3}'.format(Y,M,D, stats_accumulate[Y][M][D]))

def do_stats(xmltv):
    global channel_count
    channels = xmltv.findall('./channel')
    programs = xmltv.findall('./programme')

    for channel in channels:
        accumulate_channel(channel)
        channel_count += 1

    for program in programs:
        start = datetime.strptime( program.attrib['start'], '%Y%m%d%H%M%S %z')
        accumulate_by_date(start.year, start.month, start.day)

def main(stats: ('Print stats about the files instead of the resulting file','flag','i'),
        shift_dates: ('Shift the start time dates','option','s'),
        utc: ('Normalize start time to UTC','option','u'),
        *xmltv_files):
    """
    Utility to inspect and manipulate XMLTV files.

    Input files are merged in the output.
    """

    # Input

    xmltv = ET.parse(xmltv_files[0]).getroot()
    for xmltv_file in xmltv_files[1:]:
        one_xmltv = ET.parse(xmltv_file).getroot()
        for elem in one_xmltv:
            xmltv.extend(elem)

    # Process



    # Output

    if stats:
        for xmltv_file in xmltv_files:
            xmltv = ET.parse(xmltv_file)
            do_stats(xmltv)
        print_accumulate()

if  __name__ == '__main__':
    try:
        import plac; plac.call(main)
#    except (FileNotFoundError, ValueError) as e:
    except FileNotFoundError as e:
        print(e)

