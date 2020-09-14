import logging

import pyspark.sql.functions as psf
from pyspark.sql import SparkSession
from pyspark.sql.types import *

schema = StructType([
    StructField("crime_id", StringType(), True),
    StructField("original_crime_type_name", StringType(), True),
    StructField("report_date", StringType(), True),
    StructField("call_date", StringType(), True),
    StructField("offense_date", StringType(), True),
    StructField("call_time", StringType(), True),
    StructField("call_date_time", StringType(), True),
    StructField("disposition", StringType(), True),
    StructField("address", StringType(), True),
    StructField("city", StringType(), True),
    StructField("state", StringType(), True),
    StructField("agency_id", StringType(), True),
    StructField("address_type", StringType(), True),
    StructField("common_location", StringType(), True)
])


def run_spark_job(spark):
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "police-calls") \
        .option("startingOffsets", "earliest") \
        .option("maxOffsetPerTrigger", 200) \
        .load()
    # Show schema for the incoming resources for checks
    df.printSchema()

    # Take only value and convert it to String
    kafka_df = df.selectExpr("CAST(value AS STRING)")

    service_table = kafka_df \
        .select(psf.from_json(psf.col('value'), schema).alias("DF")) \
        .select("DF.*")

    # select original_crime_type_name and disposition
    distinct_table = service_table \
        .select("original_crime_type_name", "disposition") \
        .distinct()

    # count the number of original crime type
    agg_df = distinct_table \
        .dropna() \
        .select("original_crime_type_name") \
        .groupby("original_crime_type_name") \
        .agg({"original_crime_type_name": "count"}) \
        .orderBy("count(original_crime_type_name)", ascending=False)

    # write output stream
    query = agg_df \
        .writeStream \
        .format('console') \
        .outputMode('Complete') \
        .trigger(processingTime="10 seconds") \
        .start()

    query.awaitTermination()

    # get the right radio code json path
    radio_code_json_filepath = "./radio-code.json"
    radio_code_df = spark.read.json(radio_code_json_filepath)

    # rename disposition_code column to disposition
    radio_code_df = radio_code_df.withColumnRenamed("disposition_code", "disposition")

    # join on disposition column
    join_query = agg_df \
        .join(radio_code_df, psf.col("agg_df.disposition") == psf.col("radio_code_df.disposition"), "left_outer")

    join_query.awaitTermination()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    # Create Spark in Standalone mode
    spark = SparkSession \
        .builder \
        .master("local[*]") \
        .appName("KafkaSparkStructuredStreaming") \
        .config("spark.ui.port", 3000) \
        .getOrCreate()

    logger.info("Spark started")

    run_spark_job(spark)

    spark.stop()
