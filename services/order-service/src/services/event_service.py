import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'common'))

import boto3
import os
import json
import uuid
from datetime import datetime
from models.events import OrderEvent, EventType
from models.order import OrderResponse

class EventService:
    def __init__(self):
        self.sns_client = boto3.client('sns', region_name=os.getenv('AWS_REGION', 'us-west-2'))
        self.s3_client = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'us-west-2'))
        self.sns_topic_arn = os.getenv('SNS_TOPIC_ARN')
        self.s3_events_bucket = os.getenv('S3_EVENTS_BUCKET')

    async def publish_order_event(self, event_type: str, order: OrderResponse):
        """Publish order event to SNS and store in S3"""
        try:
            event = OrderEvent(
                event_id=str(uuid.uuid4()),
                event_type=EventType(event_type),
                order_id=order.order_id,
                customer_email=order.customer_email,
                timestamp=datetime.utcnow(),
                service_name="order-service",
                data=order.dict()
            )
            
            # Publish to SNS
            if self.sns_topic_arn:
                self.sns_client.publish(
                    TopicArn=self.sns_topic_arn,
                    Message=event.json(),
                    Subject=f"Order Event: {event_type}"
                )
            
            # Store in S3
            if self.s3_events_bucket:
                key = f"events/{datetime.utcnow().strftime('%Y/%m/%d')}/{event_type}_{order.order_id}_{int(datetime.utcnow().timestamp())}.json"
                self.s3_client.put_object(
                    Bucket=self.s3_events_bucket,
                    Key=key,
                    Body=event.json(),
                    ContentType='application/json'
                )
        
        except Exception as e:
            print(f"Failed to publish event: {e}")