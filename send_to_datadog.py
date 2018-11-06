import json
import sys

from datadog import initialize, statsd


options = {
    "statsd_host": "localhost",
    "statsd_port": "8125",
}

metrics = [
    "TTFB",
    "render",
    "firstPaint",
    "timeToDOMContentFlushed",
    "SpeedIndex",
    "bytesInDoc",
    "visualComplete",
    "requestsFull",
]


def main(path, label):

    with open(path) as f:
        data = json.load(f)

    test = [t for t in data if t["data"]["label"] == label]
    assert len(test) > 0, f"Test with label {label} not found in data!"
    assert len(test) == 1, f"Multiple tests with label {label} found in data!"

    initialize(**options)

    print(f"{label}")
    for metric in metrics:
        value = test[0]["data"]["median"]["firstView"][metric]
        print(f"- {metric}: {value}")
        statsd.gauge(f"wpt.batch.{label}.median.firstView.{metric}", value)


if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print("Usage: python send_to_datadog.py path label")
        exit()
    main(*sys.argv[1:])
