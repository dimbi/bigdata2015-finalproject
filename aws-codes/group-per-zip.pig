-------------------------------------------------------------------------------
--
-- Big Data - Final Project
-- group-only.pig
-- Group by the combination of pickup zipcode and dropoff zipcode
-- contact: drp354@nyu.edu
--
-------------------------------------------------------------------------------

-- load the data
in1 = LOAD 's3://final-project-big-data/output/mr1-rtree-output' 
USING PigStorage(',') 
AS (id:chararray,pickup_datetime:chararray,dropoff_datetime:chararray, passenger_count:float, trip_time_in_secs:float, trip_distance:float, fare_amount:float, 
    tip_amount:float, total_amount:float, tip_percentage:float, pickup_zipcode:int, dropoff_zipcode:int);

-- group by pickup_zipcode^dropoff_zipcode (id)
in2 = FOREACH (GROUP in1 BY pickup_zipcode)
      GENERATE
             (INT) AVG(in1.pickup_zipcode) AS pickup_zipcode,
             AVG(in1.tip_percentage) AS tip_percentage,
             COUNT(in1.tip_percentage) AS num_trips;

-- group by pickup_zipcode^dropoff_zipcode (id)
in3 = FOREACH (GROUP in1 BY dropoff_zipcode)
      GENERATE
             (INT) AVG(in1.dropoff_zipcode) AS dropoff_zipcode,
             AVG(in1.tip_percentage) AS tip_percentage,
             COUNT(in1.tip_percentage) AS num_trips;

-- store the data
STORE in2 INTO 's3://final-project-big-data/output/group-per-pickup-zip' USING PigStorage (',');
STORE in3 INTO 's3://final-project-big-data/output/group-per-dropoff-zip' USING PigStorage (',');
