"""
Kafka Producer Service for Task Event Publishing

This module provides a Kafka producer configured for Confluent Cloud
to publish task lifecycle events (Create, Update, Delete) to the task-events topic.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# Kafka producer instance (lazy initialization)
_producer: Optional[object] = None


def get_kafka_config() -> dict:
    """
    Build Kafka configuration from environment variables.
    Supports Confluent Cloud with SASL/SSL authentication.
    """
    bootstrap_server = os.getenv("KAFKA_BOOTSTRAP_SERVER", "")
    sasl_username = os.getenv("KAFKA_SASL_USERNAME", "")
    sasl_password = os.getenv("KAFKA_SASL_PASSWORD", "")

    if not all([bootstrap_server, sasl_username, sasl_password]):
        logger.warning("Kafka credentials not fully configured - event publishing disabled")
        return {}

    return {
        "bootstrap.servers": bootstrap_server,
        "security.protocol": "SASL_SSL",
        "sasl.mechanisms": "PLAIN",
        "sasl.username": sasl_username,
        "sasl.password": sasl_password,
        "client.id": "todo-backend-producer",
        "acks": "all",
    }


def get_producer():
    """
    Get or create a Kafka producer instance.
    Uses lazy initialization to avoid import errors when Kafka is not configured.
    """
    global _producer

    if _producer is not None:
        return _producer

    config = get_kafka_config()
    if not config:
        return None

    try:
        from confluent_kafka import Producer
        _producer = Producer(config)
        logger.info("Kafka producer initialized successfully")
        return _producer
    except ImportError:
        logger.error("confluent-kafka library not installed")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Kafka producer: {e}")
        return None


def delivery_callback(err, msg):
    """Callback for message delivery reports."""
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}")


def publish_task_event(task_id: int, action: str, user_id: Optional[int] = None) -> bool:
    """
    Publish a task event to the task-events Kafka topic.

    Args:
        task_id: The ID of the task
        action: The action performed (create, update, delete)
        user_id: Optional user ID who performed the action

    Returns:
        bool: True if message was queued successfully, False otherwise
    """
    producer = get_producer()
    if producer is None:
        logger.debug("Kafka producer not available - skipping event publish")
        return False

    # Build standardized event payload per spec
    event_payload = {
        "task_id": task_id,
        "action": action,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Add optional user context
    if user_id:
        event_payload["user_id"] = user_id

    try:
        producer.produce(
            topic="task-events",
            key=str(task_id),
            value=json.dumps(event_payload),
            callback=delivery_callback,
        )
        # Trigger delivery (non-blocking)
        producer.poll(0)
        logger.info(f"Task event queued: {action} for task_id={task_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to publish task event: {e}")
        return False


def flush_producer(timeout: float = 5.0) -> int:
    """
    Flush any pending messages in the producer queue.
    Call this during application shutdown.

    Args:
        timeout: Maximum time to wait for flush in seconds

    Returns:
        int: Number of messages still in queue (0 = all delivered)
    """
    producer = get_producer()
    if producer is None:
        return 0

    remaining = producer.flush(timeout)
    if remaining > 0:
        logger.warning(f"{remaining} messages were not delivered before flush timeout")
    return remaining
