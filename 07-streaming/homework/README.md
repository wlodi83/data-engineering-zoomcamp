# Module 7 Homework: Streaming with Kafka (Redpanda) and PyFlink

## Prerequisites

The workshop infrastructure must be running:

```bash
cd ../workshop/
docker compose build
docker compose up -d
```

Install local Python dependencies:

```bash
cd ../homework/
pip install -r requirements.txt
```

## Questions

### Q1: Redpanda version

```bash
docker exec -it workshop-redpanda-1 rpk version
```

### Q2: Sending data to Redpanda

Create the topic, then run the producer:

```bash
docker exec -it workshop-redpanda-1 rpk topic create green-trips
python3.12 producer.py
```

### Q3: Consumer - trip distance

```bash
python3.12 consumer.py
```

### Q4-Q6: PyFlink jobs

First, create the PostgreSQL tables:

```bash
python3.12 create_tables.py
```

Then submit the Flink jobs (one at a time):

```bash
# Q4: Tumbling window - pickup location
docker exec -it workshop-jobmanager-1 flink run -py /opt/src/job/tumbling_window_pu.py

# Q5: Session window - longest streak
docker exec -it workshop-jobmanager-1 flink run -py /opt/src/job/session_window_pu.py

# Q6: Tumbling window - largest tip
docker exec -it workshop-jobmanager-1 flink run -py /opt/src/job/tumbling_window_tips.py
```

Wait 1-2 minutes for results, then query PostgreSQL:

```bash
python3.12 query_results.py
```

Cancel running Flink jobs from the UI at http://localhost:8081.

## Cleanup

```bash
# Delete topic if you need to re-send data
docker exec -it workshop-redpanda-1 rpk topic delete green-trips
```
