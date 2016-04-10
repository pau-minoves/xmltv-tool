import plac
#import xml.etree.ElementTree as ET
from lxml import etree as ET
from datetime import datetime
from yattag import indent

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

def do_print_days(xmltv):
    programs = xmltv.findall('./programme')

    for program in programs:
        start = datetime.strptime( program.attrib['start'], '%Y%m%d%H%M%S %z')
        accumulate_by_date(start.year, start.month, start.day)

    for Y in stats_accumulate:
        for M in stats_accumulate[Y]:
            for D in stats_accumulate[Y][M]:
                print('\t{0} {1} {2}: {3}'.format(Y,M,D, stats_accumulate[Y][M][D]))

def do_print_channels(xmltv):
    global channel_count
    channels = xmltv.findall('./channel')

    for channel in channels:
        accumulate_channel(channel)
        channel_count += 1

    for c in channel_accumulate:
        print(str(c) + ' - ' + str(channel_accumulate[c]))

def main(inspect: ('Print stats about the files instead of the resulting file','flag','i'),
        print_channels: ('Inspect channels.', 'flag', 'c'),
        print_days: ('Inspect dates.', 'flag', 'd'),
        shift_dates: ('Shift the start time dates','option','s'),
        utc: ('Normalize start time to UTC','option','u'),
        *xmltv_files):
    """
    Utility to inspect and manipulate XMLTV files.

    If -i, -c or -d are used, a summary of the input files is printed. Otherwise a resulting processed XMLTV is printed.

    Input files are merged into one before processing.
    """

    # Parameters

    if inspect:
        print_channels = True
        print_days = True

    # Input

    xmltv = ET.parse(xmltv_files[0]).getroot()
    for xmltv_file in xmltv_files[1:]:
        one_xmltv = ET.parse(xmltv_file).getroot()
        xmltv.extend(one_xmltv)

    # Process


    # Output

    if print_days:
            do_print_days(xmltv)

    if print_channels:
            do_print_channels(xmltv)

    if not print_days and not print_channels:
       print(ET.tostring(xmltv, pretty_print=True).decode('utf-8'))

if  __name__ == '__main__':
    try:
        import plac; plac.call(main)
#    except (FileNotFoundError, ValueError) as e:
    except FileNotFoundError as e:
        print(e)
    except IsADirectoryError as e:
        print(e)

