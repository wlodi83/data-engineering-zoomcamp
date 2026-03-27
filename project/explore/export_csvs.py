"""Export Athena mart tables to CSV for Tableau."""

import boto3
import csv
import time

athena = boto3.client("athena", region_name="eu-central-1")

for table in ["workflow_health", "block_performance", "platform_adoption"]:
    r = athena.start_query_execution(
        QueryString=f"SELECT * FROM pushmetrics_analytics_marts.{table}",
        WorkGroup="pushmetrics-analytics",
    )
    eid = r["QueryExecutionId"]
    while True:
        s = athena.get_query_execution(QueryExecutionId=eid)["QueryExecution"]["Status"]["State"]
        if s in ("SUCCEEDED", "FAILED"):
            break
        time.sleep(1)
    if s == "SUCCEEDED":
        rows = athena.get_query_results(QueryExecutionId=eid, MaxResults=1000)
        cols = [c["VarCharValue"] for c in rows["ResultSet"]["Rows"][0]["Data"]]
        with open(f"{table}.csv", "w") as f:
            w = csv.writer(f)
            w.writerow(cols)
            for row in rows["ResultSet"]["Rows"][1:]:
                w.writerow([d.get("VarCharValue", "") for d in row["Data"]])
        print(f"{table}.csv exported ({len(rows['ResultSet']['Rows'])-1} rows)")
    else:
        print(f"{table}: FAILED")
