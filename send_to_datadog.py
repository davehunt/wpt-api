import json
import pprint
import os
import sys

from datadog import api, initialize, statsd


options = {
    "api_key": os.getenv("DATADOG_API_KEY"),
    "app_key": os.getenv("DATADOG_APP_KEY"),
    "statsd_host": "localhost",
    "statsd_port": "8125",
}


def main(path):

    initialize(**options)

    dashboard_list_name = "WebPageTest"
    dashboard_lists = api.DashboardList.get_all()
    pprint.pprint(dashboard_lists)

    if dashboard_list_name in dashboard_lists:
        print(f"Using existing {dashboard_list_name} dashboard list")
        dashboard_list = dashboard_lists[dashboard_list_name]
    else:
        print(f"Creating {dashboard_list_name} dashboard list")
        # dashboard_list = api.DashboardList.create(name=name)

    timeboards = {}
    # timeboards = api.Timeboard.get_all()
    # pprint.pprint(timeboards)

    with open(path) as f:
        data = json.load(f)

    with open("metrics.json") as f:
        metrics = json.load(f)

    for test in data:
        target_url = test["data"]["testUrl"]
        timeboard = timeboards.setdefault(target_url, {})  # use dataclass?
        timeboard["title"] = target_url
        timeboard["description"] = f"WebPageTest results for {target_url}"
        graphs = timeboard.setdefault("graphs", [])

        sample = test["data"]["median"]["firstView"]
        browser_name = sample["browser_name"]
        browser_version = sample["browser_version"]
        label = test["data"]["label"]
        print(f"{target_url} - {browser_name} ({browser_version})")
        for metric in metrics:
            requests = []
            for graph in graphs:
                if graph["title"] == metric:
                    requests = graph["definition"]["requests"]

            query = f"avg:wpt.batch.{label}.median.firstView.{metric}{{*}}"
            if query not in requests:
                requests.append({"q": query})

            value = test["data"]["median"]["firstView"][metric]
            print(f"- {metric}: {value}")
            # statsd.gauge(f"wpt.batch.{label}.median.firstView.{metric}", value)
            graphs.append({
                "title": metric,
                "definition": {
                    "requests": requests,
                    "viz": "timeseries",
                }
            })

    pprint.pprint(timeboards)

    for timeboard in timeboards.items():
        title = timeboard["title"]
        description = timeboard["description"]
        graphs = timeboard["graphs"]

        if title in timeboards:
            print(f"Updating {title} timeboard")
            timeboard_id = timeboards[title]["id"]
            # result = api.Timeboard.update(
            #     timeboard_id,
            #     title=title,
            #     description=description,
            #     graphs=graphs,
            # )
        else:
            print(f"Creating {title} timeboard")
        #     result = api.Timeboard.create(
        #         timeboard_id,
        #         title=title,
        #         description=description,
        #         graphs=graphs,
        #     )
        # pprint.pprint(result)

        print(f"Adding {title} timeboard to {dashboard_list_name} dashboard list")
        # result = api.DashboardList.add_items(dashboard_list["id"], dashboards=[result])
        # pprint.pprint(result)


if __name__ == "__main__":
    if not len(sys.argv) == 2:
        print("Usage: python send_to_datadog.py path")
        exit()
    main(*sys.argv[1:])
