import json
import os
import pprint
import sys

from datadog import api, initialize


options = {
    "api_key": os.getenv("DATADOG_API_KEY"),
    "app_key": os.getenv("DATADOG_APP_KEY"),
}


def main():

    initialize(**options)

    dashboard_list = api.DashboardList.create(name="WebPageTest")
    pprint.pprint(dashboard_list)

    with open("metrics.json") as f:
        metrics = json.load(f)

    with open("top50.json") as f:
        targets = json.load(f)

    dashboards = []

    for target in targets:
        safe_name = target["name"].translate(str.maketrans(". ", "--"))
        title = f"{target['name']} ({target['url']})"
        description = f"WebPageTest results for {target['name']} ({target['url']})"
        graphs = []

        for metric in metrics:
            requests = []

            for browser in ("chrome.release", "chrome.canary", "fx.release"):
                requests.append(f"avg:wpt.batch.{safe_name}.{browser}.median.firstView.{metric}{{*}}")

            graphs.append({
                "title": metric,
                "definition": {
                    "requests": requests,
                    "viz": "timeseries",
                }
            })

        pprint.pprint(graphs)
        dashboard = api.Timeboard.create(
            title=title,
            description=description,
            graphs=graphs)
        pprint.pprint(dashboard)
        dashboards.append(dashboard)

    api.DashboardList.update_items(dashboard_list["id"], dashboards=dashboards)


if __name__ == "__main__":
    if not len(sys.argv) == 1:
        print("Usage: python create_dashboards.py")
        exit()
    main()
