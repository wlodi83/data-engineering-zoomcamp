#!/usr/bin/env python
# coding: utf-8

import click
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm

dtype = {
    "LocationID": "Int64",
    "Borough": "string",
    "Zone": "string",
    "service_zone": "string"
}

@click.command()
@click.option('--pg-user', default='postgres', help='PostgreSQL user')
@click.option('--pg-pass', default='postgres', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5443, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--year', default=2025, type=int, help='Year of the data')
@click.option('--month', default=11, type=int, help='Month of the data')
@click.option('--target-table', default='yellow_taxi_data', help='Target table name')
@click.option('--chunksize', default=100000, type=int, help='Chunk size for reading CSV')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, target_table, chunksize):
    """Ingest NYC taxi data into PostgreSQL database."""
    prefix = 'https://d37ci6vzurychx.cloudfront.net/trip-data'
    url = f'{prefix}/green_tripdata_{year}-{month:02d}.parquet'

    zones_url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv'

    df_iter = pd.read_csv(
        zones_url,
        dtype=dtype,
        chunksize=chunksize,
        iterator=True,
    )

    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    data = pd.read_parquet(
        url,
        engine='fastparquet',
    )

    data.to_sql(target_table, engine, if_exists='replace', index=False)

    first = True

    target_table = 'zones'

    for df_chunk in tqdm(df_iter):
        if first:
            df_chunk.head(0).to_sql(
                name=target_table,
                con=engine,
                if_exists='replace'
            )
            first = False

        df_chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists='append'
        )

if __name__ == '__main__':
    run()