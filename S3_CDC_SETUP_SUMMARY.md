# S3 CDC Setup Summary

## Issues Fixed:

1. ✅ **Database Connection Types**: Fixed all `'aws_s3'` values to `'s3'` in the database
2. ✅ **Pipeline Mode**: Changed S3 pipelines from `FULL_LOAD_ONLY` to `FULL_LOAD_AND_CDC` to enable CDC
3. ✅ **S3 Sink Config**: 
   - Removed `"name"` field from config (should only be in outer request)
   - Added validation for required fields (`flush.size`, AWS credentials, topics)
   - Added default value for `flush.size` if not provided
4. ✅ **Schema Creation**: Skip schema creation for S3 targets (S3 doesn't support schemas)
5. ✅ **Connector Reuse**: Updated code to reuse existing running Debezium connectors instead of recreating them
6. ✅ **Error Handling**: Improved error messages from Kafka Connect

## Current Status:

The pipeline `PostgreSQL_to_S3_cdctest` is still failing with:
```
400 Client Error: Bad Request for url: http://72.61.233.209:8083/connectors
```

## Next Steps to Debug:

1. **Check Backend Logs**: The improved error logging should now show the actual validation error from Kafka Connect. Check the backend terminal for detailed error messages.

2. **Verify Topics**: Ensure Kafka topics exist for the pipeline:
   ```bash
   # Topics should be in format: {pipeline_name}.{schema}.{table}
   # Example: PostgreSQL_to_S3_cdctest.public.alembic_version
   ```

3. **Check S3 Connection**: Verify the S3 connection has valid AWS credentials:
   - Access Key ID should be in the `username` field
   - Secret Access Key should be in the `password` field
   - Bucket name should be in the `database` field

4. **Manual Connector Creation**: Try creating the S3 sink connector manually to see the exact error:
   ```bash
   curl -X POST "http://72.61.233.209:8083/connectors" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "sink-postgresql_to_s3_cdctest-s3-public",
       "config": {
         "connector.class": "io.confluent.connect.s3.S3SinkConnector",
         "tasks.max": "1",
         "topics": "PostgreSQL_to_S3_cdctest.public.alembic_version",
         "s3.region": "us-east-1",
         "s3.bucket.name": "mycdcbucket26",
         "s3.part.size": "5242880",
         "flush.size": "3000",
         "storage.class": "io.confluent.connect.s3.storage.S3Storage",
         "format.class": "io.confluent.connect.s3.format.json.JsonFormat",
         "partitioner.class": "io.confluent.connect.storage.partitioner.DefaultPartitioner",
         "schema.compatibility": "NONE",
         "aws.access.key.id": "YOUR_ACCESS_KEY",
         "aws.secret.access.key": "YOUR_SECRET_KEY"
       }
     }'
   ```

## Files Modified:

1. `ingestion/sink_config.py` - Fixed S3 sink config generation
2. `ingestion/cdc_manager.py` - Added S3 schema skip, connector reuse logic
3. `ingestion/schema_service.py` - Added S3 validation
4. `ingestion/api.py` - Added database type normalization
5. `ingestion/kafka_connect_client.py` - Improved error logging

## To Restart Pipeline:

After backend restart, the pipeline should:
1. Skip full load (already completed)
2. Skip schema creation (S3 doesn't support schemas)
3. Reuse existing Debezium connector (if running)
4. Create S3 sink connector with proper config

Try starting the pipeline again from the frontend or use:
```bash
python3 start_specific_pipeline.py
```


