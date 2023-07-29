import json
from collections import Counter
import re
from datetime import datetime

# Stage 1/6. Required inputs and data type validation.
in_str = input()
data = json.loads(in_str)
dtypes = {"bus_id": int, "stop_id": int, "stop_name": str, "next_stop": int, "stop_type": str, "a_time": str}
dic_errors_type = Counter([key for d in data
                      for key, value in d.items()
                      if (not isinstance(value, dtypes[key]))
                      or ((key != "stop_type") and (value == ""))
                      or ((key == "stop_type") and (value not in ["", "S", "O", "F"]))])

# print("Type and required field validation:", sum(dic_errors_type.values()), "errors")
# for key in dtypes.keys():
#     print(key + ":", dic_errors_type[key])

# Stage 2/6. Data format validation.
templates = {"stop_name": r"^[A-Z].+ (Road|Avenue|Boulevard|Street)$",
             "stop_type": r"^(S|O|F)$|^$",
             "a_time": r"^(\d{2}):(\d{2})$"}
dic_errors_format = Counter([key for d in data
                      for key, value in d.items()
                      if ((key in templates)
                          and not re.match(templates[key], value))
                             or ((key == "a_time")
                                 and (re.match(templates[key], value)
                                      and (not (0 <= int(re.match(templates[key], value).group(1)) <= 23)
                                           or not(0 <= int(re.match(templates[key], value).group(2)) <= 59))))])
# print("Format validation:", sum(dic_errors_format.values()), "errors")
# for key in templates.keys():
#     print(key + ":", dic_errors_format[key])


# Stage 3/6. Get bus lines and number of stops
bus_stops = {}
for d in data:
    bus_stops.setdefault(d["bus_id"], [])
    bus_stops[d["bus_id"]].append(d["stop_id"])
# print("Line names and number of stops:")
# for line, stops in bus_stops.items():
#     print("bus_id:", line, "stops:", len(stops))


# Stage 4/6. Get start, transfer and finish stops.
stops_info = {(d["bus_id"], d["stop_id"]): (d["stop_name"], d["stop_type"]) for d in data}
unique_starts = set()
unique_finals = set()
possible_transfers = []
ok = True
line_start = {}
for line, stop_list in bus_stops.items():
    starts = [stops_info[(line, stop)][0] for stop in stop_list if stops_info[(line, stop)][1] == "S"]
    start_id = [stop for stop in stop_list if stops_info[(line, stop)][1] == "S"]
    finals = [stops_info[(line, stop)][0] for stop in stop_list if stops_info[(line, stop)][1] == "F"]
    possible_transfers = possible_transfers + [stops_info[(line, stop)][0] for stop in stop_list]
    if (len(starts) != 1) or (len(finals) != 1):
        print("There is no start or end stop for the line:", line)
        ok = False
        break
    line_start[line] = start_id[0]
    unique_starts.update(set(starts))
    unique_finals.update(set(finals))
if ok:
    unique_starts = list(unique_starts)
    unique_starts.sort()
    unique_finals = list(unique_finals)
    unique_finals.sort()
    transfers = Counter(possible_transfers)
    transfers = [name for name, value in transfers.items() if value > 1]
    transfers.sort()
    # print("Start stops:", len(unique_starts), unique_starts)
    # print("Transfer stops:", len(transfers), transfers)
    # print("Finish stops:", len(unique_finals), unique_finals)

# Stage 5/6. Check that all the arrival times in bus stops pointed by "next_stop" are increasing in the same line.
# print("Arrival time test:")
time_info = {(d["bus_id"], d["stop_id"]): (d["a_time"], d["next_stop"], d["stop_name"]) for d in data}
arrival_test_ok = True
for line_id, stops_list in bus_stops.items():
    stop_id = line_start[line_id]
    next_stop_id = time_info[(line_id, stop_id)][1]
    while next_stop_id != 0:
        a_time = datetime.strptime(time_info[(line_id, stop_id)][0], "%H:%M")
        a_time_next = datetime.strptime(time_info[(line_id, next_stop_id)][0], "%H:%M")
        time_delta = (a_time_next - a_time).total_seconds()
        if time_delta <= 0:
            arrival_test_ok = False
            print("bus_id line", str(line_id) + ": wrong time on station", time_info[(line_id, next_stop_id)][2])
            next_stop_id = 0
        else:
            stop_id = next_stop_id
            next_stop_id = time_info[(line_id, next_stop_id)][1]
# if arrival_test_ok:
#     print("OK")

# Stage 6/6: check on-demand stops. Stops that are S, F or transfer cannot be "on-demand".
print("On demand stops test:")
SFT_Stops = set(unique_starts)
SFT_Stops.update(set(unique_finals))
SFT_Stops.update(set(transfers))
O_Stops = set([d["stop_name"] for d in data if d["stop_type"]=="O"])
wrong_stops = list(O_Stops.intersection(SFT_Stops))
if wrong_stops:
    wrong_stops.sort()
    print("Wrong stop type:", wrong_stops)
else:
    print("OK")