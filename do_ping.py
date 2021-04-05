import subprocess
import datetime
import time
from counter import Counter


# Executes a PING on the passed address, and returns either response time or the error message returned
def ping(host):
    error = None
    r_time = -1
    exec_ping = subprocess.run(["ping", "-n", "1" "-4", host], capture_output=True)
    if exec_ping.returncode == 0:
        lines = exec_ping.stdout.splitlines()
        if lines[2][:10] == b'Reply from':
            r_time = lines[2].split()[4][5:-2].decode('utf-8')
        else:
            error = "Error(0): {}".format(lines[2])
    else:
        error = "Error({}): {}".format(exec_ping.returncode, exec_ping.stdout)
    return float(r_time), error


def batch_ping(host):
    # Start the counters
    timestamp = datetime.datetime.now()
    counter = Counter("DATA")
    counter_err = Counter("ERROR")
    last_min = timestamp.minute
    this_min = last_min
    error_details = []

    while this_min == last_min:
        time.sleep(1.0)
        timestamp = datetime.datetime.now()
        this_min = timestamp.minute
        rt, err_full = ping(host)
        if err_full:
            print("ERROR @ {}: {}".format(timestamp.__str__(), err_full))
            err_type = "UNKNOWN"
            if "Request timed out" in err_full:
                err_type = "TIMEOUT"
            if "Ping request could not find host" in err_full:
                err_type = "NO HOST"
            error_details.append([timestamp.__str__(), host, err_type, err_full])
            counter_err.add(1)  # increment the error count
            counter.add(0)   # add a big fat zero to the latency counter
        else:
            counter.add(rt)

    counter.show()
    if counter_err.count() > 0:
        counter_err.show()

    return counter, counter_err.count(), error_details
