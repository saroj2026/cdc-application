#!/usr/bin/env python3
"""Check Kafka topic message count to see if messages are there."""

import requests

print("=" * 70)
print("CHECKING KAFKA TOPIC MESSAGES")
print("=" * 70)

# Note: Kafka Connect API doesn't directly provide message count
# We need to use Kafka Admin API or kafka-console-consumer
# For now, we'll check via Kafka UI if available, or provide instructions

topic_name = "oracle_sf_p.CDC_USER.TEST"
kafka_ui_url = "http://72.61.233.209:8080"  # Kafka UI

print(f"\n1. Kafka Topic: {topic_name}")
print("-" * 70)
print(f"   To check message count, use one of these methods:")
print(f"   ")
print(f"   Method 1: Kafka UI")
print(f"   - Open: {kafka_ui_url}")
print(f"   - Navigate to Topics → {topic_name}")
print(f"   - Check message count and latest messages")
print(f"   ")
print(f"   Method 2: Kafka Console Consumer (via SSH)")
print(f"   - SSH to server: ssh root@72.61.233.209")
print(f"   - Run: docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic {topic_name} --from-beginning --max-messages 10")
print(f"   ")
print(f"   Method 3: Check Consumer Group Offsets")
print(f"   - This shows if sink connector is consuming messages")

print(f"\n2. Checking Sink Connector Consumer Group...")
print("-" * 70)

# The consumer group name for Snowflake sink is: connect-{connector-name}
consumer_group = f"connect-sink-oracle_sf_p-snow-public"

print(f"   Consumer group: {consumer_group}")
print(f"   ")
print(f"   To check offsets (via SSH):")
print(f"   docker exec -it kafka kafka-consumer-groups --bootstrap-server localhost:9092 --group {consumer_group} --describe")
print(f"   ")
print(f"   This will show:")
print(f"   - Current offset (how many messages consumed)")
print(f"   - Log end offset (total messages in topic)")
print(f"   - LAG (difference = unprocessed messages)")

print("\n" + "=" * 70)
print("NEXT STEPS:")
print("  1. Check Kafka UI to see if messages are in the topic")
print("  2. Check consumer group offsets to see if sink is consuming")
print("  3. If messages are in topic but not consumed, check sink connector logs")
print("  4. If no messages in topic, check source connector (Debezium)")
print("=" * 70)
