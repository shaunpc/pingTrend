# PingTrend - GRAPH.PY
#   to visualise the recorded PING results

from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import matplotlib.dates as mdates
import time
import logging
from database import Database

# Configuration
PING_TARGET = "www.google.com"
DB_FILE = r"C:\Users\shaun\PycharmProjects\pingTrend\pingdatabase.sqlite"
MAX_POINTS = 400 # Maximum number of data points to keep in memory and display
HISTORY_DAYS = 3 # Number of days of historical data to load on startup
CHECK_INTERVAL = 60 # seconds between checks for new data (data stored at rate 1/min)
DEBUG = False  # Set to True for verbose output

# Setup logging
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Replace SQL to compare full timestamp (not date(...))
SQL_QUERY = (
    "SELECT ping_timestamp, response_min, response_ave, response_max, error_count "
    "FROM pingdata WHERE ping_timestamp > ? "
    "ORDER by ping_timestamp ASC LIMIT ?"
)

TIMESTAMP_FORMATS = ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S']


class PingDataManager:
    """Manages ping data retrieval and storage."""

    def __init__(self, db_file):
        self.db = Database(db_file)
        self.ping_time = []
        self.ping_min = []
        self.ping_ave = []
        self.ping_max = []
        self.ping_err = []

    def get_ping_data(self, cutoff):
        """Retrieve ping data from database since cutoff timestamp."""
        if not isinstance(cutoff, datetime):
            raise ValueError("cutoff must be a datetime object")

        # convert cutoff to the DB timestamp string format before querying
        cutoff_param = cutoff.strftime(TIMESTAMP_FORMATS[0])

        try:
            pingdata = self.db.select(SQL_QUERY, (cutoff_param, MAX_POINTS))
        except Exception as ex:
            logger.error(f"Database query failed: {ex}")
            return cutoff, 0

        max_time = cutoff
        logger.debug(f"Cutoff: {cutoff}")

        for i, row in enumerate(pingdata):
            # Validate row has required columns
            if len(row) < 5:
                logger.warning(f"Row {i} missing columns, skipping: {row}")
                continue

            # Parse timestamp with fallback formats
            ping_timestamp = self._parse_timestamp(row[0], i)
            if ping_timestamp is None:
                continue

            logger.debug(f"Data Row {i} Timestamp: {ping_timestamp}")
            self.ping_time.append(ping_timestamp)
            self.ping_min.append(row[1])
            self.ping_ave.append(row[2])
            self.ping_max.append(row[3])
            self.ping_err.append(row[4])

            if ping_timestamp > max_time:
                max_time = ping_timestamp
                logger.debug(f"Next data load only from: {max_time}")

        # Truncate once after loading all data
        self._truncate_if_needed()

        return max_time, len(pingdata)

    @staticmethod
    def _parse_timestamp(timestamp_str, row_index):
        """Parse timestamp string with multiple format support."""
        for fmt in TIMESTAMP_FORMATS:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue

        logger.warning(f"Could not parse timestamp at row {row_index}: {timestamp_str}")
        return None

    def _truncate_if_needed(self):
        """Trim data arrays if they exceed MAX_POINTS."""
        if len(self.ping_time) > MAX_POINTS:
            excess = len(self.ping_time) - MAX_POINTS
            logger.info(f"Truncating data set from {len(self.ping_time)} to {MAX_POINTS}")
            self.ping_time[:] = self.ping_time[excess:]
            self.ping_min[:] = self.ping_min[excess:]
            self.ping_ave[:] = self.ping_ave[excess:]
            self.ping_max[:] = self.ping_max[excess:]
            self.ping_err[:] = self.ping_err[excess:]

    def close(self):
        """Close database connection."""
        self.db.close()


def setup_chart_axis(axis, ylabel, is_error=False):
    """Configure common chart axis properties."""
    axis.set_ylabel(ylabel)
    axis.set_ylim(ymin=0, auto=True)
    axis.yaxis.set_major_formatter(tck.StrMethodFormatter('{x:.0f}'))
    axis.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.setp(axis.get_xticklabels(), rotation=30, ha='right', rotation_mode="anchor")
    axis.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=range(0, 60, 10), interval=1))
    axis.yaxis.set_major_locator(tck.MaxNLocator(integer=True))
    if not is_error:
        axis.yaxis.set_minor_locator(tck.AutoMinorLocator())
    axis.grid(visible=True, which='both', axis='y', color='silver', linewidth=0.25)


# Main Routine
if __name__ == '__main__':
    logger.info("Parameters:")
    logger.info(f"  Ping Target      : {PING_TARGET}")
    logger.info(f"  Database File    : {DB_FILE}")
    logger.info(f"  Max Points       : {MAX_POINTS}")
    logger.info(f"  History Days     : {HISTORY_DAYS}")

    # Initialize database and the DataManager object
    try:
        manager = PingDataManager(DB_FILE)
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        exit(1)

    # Setup display
    plt.ion()
    fig, (ax_err, ax) = plt.subplots(2, sharex='all', gridspec_kw={'height_ratios': [1, 4]})
    fig.canvas.manager.set_window_title('Ping Trends')
    fig.set_size_inches(14.0, 6.0)
    fig.suptitle(f'Ping Trends: {PING_TARGET}')

    setup_chart_axis(ax_err, 'Errors', is_error=True)
    setup_chart_axis(ax, 'Ping Response Time (ms)', is_error=False)
    ax.set_xlabel('Time')

    logger.info(f"Starting data visualisation at {datetime.now()}")

    # Load initial data
    cutoff = datetime.now() - timedelta(days=HISTORY_DAYS)
    logger.info(f"Initial data loading from date {cutoff}")
    cutoff, rows = manager.get_ping_data(cutoff)

    # Plot initial lines (handle empty data gracefully)
    l_min, = ax.plot_date(manager.ping_time or [], manager.ping_min or [], fmt="--g", linewidth=1, label='Min')
    l_ave, = ax.plot_date(manager.ping_time or [], manager.ping_ave or [], fmt="-b", linewidth=2, label='Ave')
    l_max, = ax.plot_date(manager.ping_time or [], manager.ping_max or [], fmt="--y", linewidth=1, label='Max')
    l_err, = ax_err.plot_date(manager.ping_time or [], manager.ping_err or [], fmt="-r", linewidth=3, label='Error Count')

    ax_err.legend(loc="upper left")
    ax.legend(loc="upper left")
    plt.show(block=False)
    fig.canvas.draw()
    fig.canvas.flush_events()

    logger.info(f"Completed initial data load with {rows} rows. Next data load only from: {cutoff}")

    # Main loop - continuously update with new data
    try:
        while True:
            cutoff, rows = manager.get_ping_data(cutoff)
            if rows > 0:
                logger.info(f"Grabbed {rows} rows, next data load only from: {cutoff}")
                l_min.set_xdata(manager.ping_time)
                l_min.set_ydata(manager.ping_min)
                l_ave.set_xdata(manager.ping_time)
                l_ave.set_ydata(manager.ping_ave)
                l_max.set_xdata(manager.ping_time)
                l_max.set_ydata(manager.ping_max)
                l_err.set_xdata(manager.ping_time)
                l_err.set_ydata(manager.ping_err)
                ax.relim()
                ax.autoscale_view()
                if manager.ping_err and max(manager.ping_err) == 0:  # correct the tick mark issue if only zeros
                    ax_err.set_ylim(ymin=-2, ymax=2)
                else:
                    ax_err.relim()
                    ax_err.autoscale_view()
                fig.canvas.draw_idle()
                fig.canvas.flush_events()
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        logger.info(f"Stopping visualisation at {datetime.now()}")
    except Exception as e:
        logger.error(f"Finishing data visualisation at {datetime.now()} with error: {e}")

    finally:
        manager.close()
        plt.close('all')
