# PingTrend - GRAPH.PY
#   to visualise the recorded PING results

from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from database import Database
from matplotlib.ticker import MultipleLocator

sql_get_latest_ping_data = ('SELECT ping_timestamp, response_min, response_ave, \n'
                            '                            response_max, error_count FROM pingdata \n'
                            '                            ORDER by ping_timestamp DESC LIMIT 400')

# Main Routine.
if __name__ == '__main__':
    db = Database(r"C:\Users\shaun\PycharmProjects\pingTrend\pingdatabase.sqlite")
    ping_target = "www.google.com"

    # Setup the display
    fig, (ax_err, ax) = plt.subplots(2, sharex='all', gridspec_kw={'height_ratios': [1, 4]})
    fig.canvas.set_window_title('Ping Trends')
    fig.set_size_inches(14.0, 6.0)
    fig.suptitle('Ping Trends : {}'.format(ping_target))

    # Set characteristics of ERROR chart
    ax_err.set_ylabel('Errors')
    ax_err.set_ylim([0, 2])
    ax_err.yaxis.set_major_formatter('{x:.0f}')
    # ax_err.xaxis.set_major_locator(MultipleLocator(5))
    # ax_err.xaxis.set_minor_locator(MultipleLocator(1))
    ax_err.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    # ax_err.xaxis.set_major_locator(MultipleLocator(5))
    ax_err.grid(b=True, which='both', axis='y', color='silver', linewidth=0.25)

    # Set characteristics of MAIN DATA chart
    ax.set_xlabel('Time')
    ax.set_ylabel('Ping Response Time (ms)')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.setp(ax.get_xticklabels(), rotation=30, ha='right', rotation_mode="anchor")
    minlocator = mdates.MinuteLocator(byminute=range(0, 60, 5))
    ax.xaxis.set_minor_locator(minlocator)
    # ax.xaxis.set_major_locator(MultipleLocator(5))
    # ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_minor_locator(MultipleLocator(2.5))
    ax.grid(b=True, which='both', axis='y', color='silver', linewidth=0.25)

    print("Starting data visualisation at {}".format(datetime.now()))
    first_time = True
    try:
        while True:
            ping_time = []
            ping_min = []
            ping_ave = []
            ping_max = []
            ping_err = []
            pingdata = db.select(sql_get_latest_ping_data)
            for row in pingdata:
                ping_time.append(datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f'))
                ping_min.append(row[1])
                ping_ave.append(row[2])
                ping_max.append(row[3])
                ping_err.append(row[4])

            if first_time:
                # Plot the lines with formatting charactistics
                l_min, = ax.plot_date(ping_time, ping_min, marker='', color='green', linewidth=1, linestyle='dashed', label='Min')
                l_ave, = ax.plot_date(ping_time, ping_ave, marker='',  color='blue', linewidth=2, linestyle='solid', label='Ave')
                l_max, = ax.plot_date(ping_time, ping_max, marker='',  color='orange', linewidth=1, linestyle='dashed', label='Max')
                l_err, = ax_err.plot_date(ping_time, ping_err, marker='', color='red', linewidth=3, linestyle='solid', label='Error Count')
                plt.pause(0.1)
                first_time = False
            else:
                # Just update the lines with the latest data points
                l_min.set_xdata(ping_time)
                l_min.set_ydata(ping_min)
                l_ave.set_xdata(ping_time)
                l_ave.set_ydata(ping_ave)
                l_max.set_xdata(ping_time)
                l_max.set_ydata(ping_max)
                l_err.set_xdata(ping_time)
                l_err.set_ydata(ping_err)
                fig.canvas.draw()
                fig.canvas.flush_events()
                plt.pause(0.1)
    except KeyboardInterrupt:
        print("Finishing data visualisation at {}".format(datetime.now()))
        db.close()
        plt.show()              # Interactive mode this defaults to FALSE and doesn't return until window closed
