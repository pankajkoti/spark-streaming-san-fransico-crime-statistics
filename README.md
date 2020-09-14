# Spark Streaming: San Fransico Crime Statistics

## Project Overview
In this project, we are provided with a real-world dataset, extracted from Kaggle, on San Francisco crime incidents, 
and we will provide statistical analyses of the data using Apache Spark Structured Streaming. We create a Kafka server to produce data,
 and ingest data through Spark Structured Streaming.

We try to answer the following question with the dataset:

What are the top types of crimes in San Fransisco?


###Development Environment
We need to set up our environment properly as described below:
    
    1. Spark 2.4.3
    2. Scala 2.11.x
    3. Java 1.8.x
    4. Kafka build with Scala 2.11.x
    5. Python 3.6.x or 3.7.x
    
###Environment Setup 
For Macs or Linux:
Download Spark from https://spark.apache.org/downloads.html. Choose "Prebuilt for Apache Hadoop 2.7 and later."
Unpack Spark in one of your folders (I usually put all my dev requirements in /home/users/user/dev).
<br/>
Download binary for Kafka from this location https://kafka.apache.org/downloads, with Scala 2.11, version 2.3.0.
 Unzip in your local directory where you unzipped your Spark binary as well. 
<br/><br/>Exploring the Kafka folder, 
 we’ll see the scripts to execute in bin folders, and config files under config folder.
  You’ll need to modify zookeeper.properties and server.properties.
Download Scala from the official site, or for Mac users, you can also use brew install scala, 
but make sure you download version 2.11.x.
Run below to verify correct versions:
```jsunicoderegexp
java -version
scala -version
```
Make sure your ~/.bash_profile looks like below (might be different depending on your directory):
```code 
export SPARK_HOME=/Users/dev/spark-2.4.3-bin-hadoop2.7
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home
export SCALA_HOME=/usr/local/scala/
export PATH=$JAVA_HOME/bin:$SPARK_HOME/bin:$SCALA_HOME/bin:$PATH
```

### Steps to run the project
This project requires creating topics, starting Zookeeper and Kafka servers, and 
your Kafka bootstrap server. You’ll need to choose a port number (e.g., 9092, 9093..) 
for your Kafka topic, and come up with a Kafka topic name and modify the zookeeper.properties 
and server.properties appropriately.

Install requirements using ./start.sh if you use conda for Python.
 If you use pip rather than conda, then use ```pip install -r requirements.txt```

Use the commands below to start the Zookeeper and Kafka servers. You can find the bin and config folder in the Kafka binary that you have downloaded and unzipped.
```
bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties
```

**Step 1:** <br/>
The first step is to run a simple Kafka server.
The code for the server is in producer_server.py and kafka_server.py.
Run ```python kafka_server.py``` to start writing to kafka topic <br/>
Local Environment
To see the messages from the server, use the command <br/> 
```
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic police.sf.calls --from-beginning
```

**Step 2:**<br/>
To check messages via python consumer, run the following:
```jsunicoderegexp
python consumer.server.py
```

Apache Spark already has an integration with Kafka brokers, so we would not normally need a separate Kafka consumer<br/>
Do a spark-submit using this command: 
```
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.3.4 --master local[*] data_stream.py
```

### Screenshots:
Please unzip and refer to the screenshots.zip to observe my runtime screenshots

###Project Questions:
1. How did changing values on the SparkSession property parameters affect the throughput and latency of the data?
    <br/> An important property is the maxOffsetsPerTrigger and differences can be seen by increasing or decreasing this value
2. What were the 2-3 most efficient SparkSession property key/value pairs? Through testing multiple variations on values, how can you tell these were the most optimal?
    1. maxOffsetsPerTrigger: how many messages each trigger event will wait
    2. maxRatePerPartition: max messages per partition per topic
    3. spark.executor.memory : setting executor memory 
    4. spark.executor.cores : setting executor cores
    5. spark.driver.memory : setting driver memory
    
    I did not do an extensive testing of these variables as it was difficult to understand from the verbose logs, however the results were performant enough for the given dataset