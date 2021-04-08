import xml.etree.ElementTree as ET
import datetime


def read_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    res = {}
    pre = '{http://www.xes-standard.org/}'


    for trace in root.findall(pre + "trace"):
        case_node = trace.find(pre + 'string')
        case_id = case_node.get('value')
        if not case_id in res:
            res[case_id] = []
        
        for event in trace.findall(pre + 'event'):
            item = {}
            for str_item in event.findall(pre + 'string'):
                key = str_item.get('key')
                value = str_item.get('value')
                item[key] = value 

            for int_item in event.findall(pre + 'int'):
                key = int_item.get('key')
                value = int_item.get('value')
                item[key] = int(value)

            for date_item in event.findall(pre + 'date'):
                key = date_item.get('key')
                value = date_item.get('value')
                parts = value.split('T')
                date = parts[0]
                date_parts = date.split('-')
                year = int(date_parts[0])
                month = int(date_parts[1])
                day = int(date_parts[2])
                time = parts[1].split('+')[0]
                time_parts = time.split(':')
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                second = int(time_parts[2])

                item[key] = datetime.datetime(year, month, day, hour, minute, second, 0)

        
            res[case_id].append(item)
    
    return res

def dependency_graph(log):
    res = {}

    for case_id in log.keys():
        items = log[case_id]
        
        for idx in range(0, len(items) - 1):
            first = items[idx]['concept:name']
            second = items[idx + 1]['concept:name']
            if not first in res:
                res[first]= {}
            if  not second in res[first]:
                res[first][second] = 0
            
            res[first][second] = res[first][second] + 1

    return res


log = read_from_file('extension-log.xes')
case_id = "case_123"
event_no = 0

print(log[case_id])
print(log[case_id][event_no]["concept:name"], log[case_id][event_no]["org:resource"], log[case_id][event_no]["time:timestamp"],  log[case_id][event_no]["cost"])
