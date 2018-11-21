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

    dbl_name = "WebPageTest"
    dbls = api.DashboardList.get_all()["dashboard_lists"]
    pprint.pprint(dbls)
    dbl = next(dbl for dbl in dbls if dbl["name"] == dbl_name)
    print(f"Using existing {dbl_name} dashboard list")

    # print(f"Creating {dbl_name} dashboard list")
    # dashboard_list = api.DashboardList.create(name=name)

    tbdata = {}
    tbs = api.Timeboard.get_all()
    pprint.pprint(tbs)

    with open(path) as f:
        data = json.load(f)

    with open("metrics.json") as f:
        metrics = json.load(f)

    for test in data:
        target_url = test["data"]["testUrl"]

        tbdata = tbdata.setdefault(target_url, {})
        tbdata["title"] = target_url
        tbdata["description"] = f"WebPageTest results for {target_url}"
        graphs = tbdata.setdefault("graphs", [])

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

    pprint.pprint(tbdata)

    for data in tbdata.values():
        title = data["title"]
        description = data["description"]
        graphs = data["graphs"]

        if title in tbs:
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

        print(f"Adding {title} timeboard to {dbl_name} dashboard list")
        # result = api.DashboardList.add_items(dbl["id"], dashboards=[result])
        # pprint.pprint(result)


if __name__ == "__main__":
    if not len(sys.argv) == 2:
        print("Usage: python send_to_datadog.py path")
        exit()
    main(*sys.argv[1:])
