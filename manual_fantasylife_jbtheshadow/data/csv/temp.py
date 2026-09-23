from csv import DictReader
from json import dumps

requests = []
with open("requests.csv") as file:
    csv_reader = DictReader(file, ["region", "issuer", "no", "name", "rank", "life1", "life2", "life3", "requires", "dlc"])
    for row in csv_reader:
        request = {}
        request["name"] = f"Request for {row["issuer"]} #{row["no"]} - {row["name"]}"
        request["category"] = [
            f"Other Requests",
            f"Other Requests {row["no"]}",
            f"Other Requests - {row["region"]} - {row["issuer"]}"
        ]
        for extra in [row["rank"], row["life1"], row["life2"], row["life3"], row["dlc"]]:
            if len(extra):
                request["category"].append(extra)
        request["region"] = row["region"]
        request["requires"] = row["requires"]
        requests.append(request)

print(dumps(requests))
