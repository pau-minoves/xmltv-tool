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
                print('{0} {1} {2}: {3}'.format(Y,M,D, stats_accumulate[Y][M][D]))

def do_print_channels(xmltv):
    global channel_count
    channels = xmltv.findall('./channel')

    for channel in channels:
        accumulate_channel(channel)
        channel_count += 1

    for c in channel_accumulate:
        print(str(c) + ': ' + str(channel_accumulate[c]))

def main(inspect: ('Print stats about the files instead of the resulting file','flag','i'),
        print_channels: ('Inspect channels.', 'flag', 'c'),
        print_days: ('Inspect dates.', 'flag', 'd'),
        filter_channels: ('Filter by channels id (comma separated)', 'option', 'C'),
        shift_time: ('Shift the start time dates','option','s'),
        utc: ('Normalize start time to UTC','flag','u'),
        *xmltv_files):
    """
    Utility to inspect and manipulate XMLTV files.

    If -i, -c or -d are used, a summary of the input files is printed. Otherwise a resulting processed XMLTV is printed.

    Input files are merged into one before processing.
    """

    filter_channels_list = None

    # Parameters

    if inspect:
        print_channels = True
        print_days = True

    if filter_channels:
        filter_channels_list = [f.strip() for f in  filter_channels.split(',')]

    # Input

    xmltv = ET.parse(xmltv_files[0]).getroot()
    for xmltv_file in xmltv_files[1:]:
        one_xmltv = ET.parse(xmltv_file).getroot()
        xmltv.extend(one_xmltv)

    # Process

    if filter_channels:
        for channel_elem in xmltv.findall('./channel'):
            if 'id' in channel_elem.attrib:
                if channel_elem.attrib['id'] not in filter_channels_list:
                    xmltv.remove(channel_elem)
            else:
                print('WARNING: channel element without id ' + channel_elem.tostring())
        for programme_elem in xmltv.findall('./programme'):
            if 'channel' in programme_elem.attrib:
                if programme_elem.attrib['channel'] not in filter_channels_list:
                    xmltv.remove(programme_elem)
            else:
                print('WARNING: programme element without id ' + programme_elem.tostring())

    # Output

    if print_channels:
            do_print_channels(xmltv)

    if print_days:
            do_print_days(xmltv)

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

