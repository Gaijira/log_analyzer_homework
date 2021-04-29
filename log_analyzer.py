import argparse
from collections import Counter, defaultdict
import re
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument('-d', dest='directory', action='store', help='Directory to search files for parsing')
parser.add_argument('-f', dest='file', action='store', help='File to parse')
args = parser.parse_args()
directory = args.directory
file = args.file

methods = r"OPTIONS|GET|HEAD|POST|PUT|PATCH|DELETE|TRACE|T"
url = r'\".+\s(.+)\sHTTP'
status = r'HTTP\/1\.[10]\"\s(\d{3})\s'
ips = r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'
client_error = r'HTTP\/1\.[10]\"\s([4]\d{2})\s'
server_error = r'HTTP\/1\.[10]\"\s([5]\d{2})\s'

sumlist = []


def method_counter(file):
    'Counts methods in file'
    dict_ips = defaultdict(int)
    with open(file) as file_handler:
        for line in file_handler:
            if re.search(methods, line)[0]:
                method = re.search(methods, line)[0]
            dict_ips[method] += 1
    sumlist.append(dict_ips)


def ip_cather(file):
    'Parsing all ips in the file and collecting 10 most common'
    top_ips = []
    with open(file) as file_handler:
        text = file_handler.read()
        file_handler.seek(0)
        all_ips = re.findall(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', text)
        for ip, count in Counter(all_ips).most_common(10):
            top_ips.append(ip)
    sumlist.append(top_ips)


def duration_parser(file):
    'Parsing the file and collecting top 10 requests by duration'
    duration_list = []
    with open(file) as file_handler:
        text = file_handler.read()
        file_handler.seek(0)
        duration = re.findall(r'\"\s\d{3}\s(\d+)\s', text)
        top_10_duration_requests = sorted(duration, reverse=True, key=len)[:10]
        for line in file_handler:
            for item in top_10_duration_requests:
                if item in line:
                    record = {}
                    record['IP'] = re.search(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', line)[0]
                    record['METHOD'] = re.search(r"OPTIONS|GET|HEAD|POST|PUT|PATCH|DELETE|TRACE|Head|T", line)[0]
                    record['STATUS'] = re.search(status, line)[1]
                    record['URL'] = re.search(r'\".+\s(.+)\sHTTP', line)[1]
                    record['DURATION'] = item
                    duration_list.append(record)

    sumlist.append(duration_list)


def eror_catcher(status, error_list, file):
    'Parsing file and collecting the all records by status provided into error list'
    with open(file) as file_handler:
        for line in file_handler:
            if re.search(status, line):
                error_list.append(line)


def requests_collector(error_list, status, parsed_list):
    'Collects the records from provided list with requests by status provided into parsed list'
    for line in error_list:
        record = {}
        record['IP'] = re.search(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', line)[0]
        record['METHOD'] = re.search(r"OPTIONS|GET|HEAD|POST|PUT|PATCH|DELETE|TRACE|Head|T", line)[0]
        record['STATUS'] = re.search(status, line)[1]
        record['URL'] = re.search(r'\".+\s(.+)\sHTTP', line)[1]
        record['DURATION'] = re.search(r'\"\s\d{3}\s(\d+)\s', line)[1]
        parsed_list.append(record)


def directory_parser():
    'Parses directory and if any file with .log ext is found, parses file and dumps results into json file'
    if directory:
        for filename in os.listdir(directory):
            file = filename
            if filename.endswith('.log'):
                method_counter(file)
                ip_cather(file)
                duration_parser(file)
                client_error_list = []
                server_error_list = []
                eror_catcher(client_error, client_error_list, file)
                eror_catcher(server_error, server_error_list, file)
                client_list = []
                server_list = []
                requests_collector(client_error_list, client_error, client_list)
                requests_collector(server_error_list, server_error, server_list)
                top_10_client_errors = sorted(client_list, key=lambda i: len(i['DURATION']), reverse=True)[:10]
                sumlist.append(top_10_client_errors)
                top_10_server_errors = sorted(server_list, key=lambda i: len(i['DURATION']), reverse=True)[:10]
                sumlist.append(top_10_server_errors)
                with open('output.json', 'w') as pfile:
                    json.dump(sumlist, pfile, indent=4)
    else:
        pass


# If --f key provided, parses provided file and outputs results into json file
if file:
    dict_ips = defaultdict(int)
    method_counter(file)
    ip_cather(file)
    duration_parser(file)
    client_error_list = []
    server_error_list = []
    eror_catcher(client_error, client_error_list, file)
    eror_catcher(server_error, server_error_list, file)
    client_list = []
    server_list = []
    requests_collector(client_error_list, client_error, client_list)
    requests_collector(server_error_list, server_error, server_list)
    top_10_client_errors = sorted(client_list, key=lambda i: len(i['DURATION']), reverse=True)[:10]
    sumlist.append(top_10_client_errors)
    top_10_server_errors = sorted(server_list, key=lambda i: len(i['DURATION']), reverse=True)[:10]
    sumlist.append(top_10_server_errors)
    with open('output.json', 'w') as pfile:
        json.dump(sumlist, pfile, indent=4)
else:
    pass

directory_parser()
