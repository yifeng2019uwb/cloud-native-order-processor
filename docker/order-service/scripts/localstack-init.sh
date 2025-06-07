#!/bin/bash
set -e

echo "Initializing LocalStack AWS resources..."

# Set AWS CLI configuration for LocalStack
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
export AWS_ENDPOINT_URL=http://localhost:4566

# Wait for LocalStack to be ready
echo "Waiting for LocalStack to be ready..."
sleep 10

# Create SNS Topics
echo "Creating SNS topics..."
aws sns create-topic --name order-events --endpoint-url=http://localhost:4566
aws sns create-topic --name payment-events --endpoint-url=http://localhost:4566
aws sns create-topic --name inventory-events --endpoint-url=http://localhost:4566
aws sns create-topic --name notification-events --endpoint-url=http://localhost:4566

# Create SQS Queues
echo "Creating SQS queues..."
aws sqs create-queue --queue-name order-processing-queue --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name payment-processing-queue --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name inventory-processing-queue --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name notification-processing-queue --endpoint-url=http://localhost:4566

# Create Dead Letter Queues
echo "Creating dead letter queues..."
aws sqs create-queue --queue-name order-dlq --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name payment-dlq --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name inventory-dlq --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name notification-dlq --endpoint-url=http://localhost:4566

# Get queue URLs and topic ARNs
ORDER_QUEUE_URL=$(aws sqs get-queue-url --queue-name order-processing-queue --endpoint-url=http://localhost:4566 --query 'QueueUrl' --output text)
PAYMENT_QUEUE_URL=$(aws sqs get-queue-url --queue-name payment-processing-queue --endpoint-url=http://localhost:4566 --query 'QueueUrl' --output text)
INVENTORY_QUEUE_URL=$(aws sqs get-queue-url --queue-name inventory-processing-queue --endpoint-url=http://localhost:4566 --query 'QueueUrl' --output text)
NOTIFICATION_QUEUE_URL=$(aws sqs get-queue-url --queue-name notification-processing-queue --endpoint-url=http://localhost:4566 --query 'QueueUrl' --output text)

ORDER_TOPIC_ARN=$(aws sns list-topics --endpoint-url=http://localhost:4566 --query 'Topics[?ends_with(TopicArn, `order-events`)].TopicArn' --output text)
PAYMENT_TOPIC_ARN=$(aws sns list-topics --endpoint-url=http://localhost:4566 --query 'Topics[?ends_with(TopicArn, `payment-events`)].TopicArn' --output text)
INVENTORY_TOPIC_ARN=$(aws sns list-topics --endpoint-url=http://localhost:4566 --query 'Topics[?ends_with(TopicArn, `inventory-events`)].TopicArn' --output text)
NOTIFICATION_TOPIC_ARN=$(aws sns list-topics --endpoint-url=http://localhost:4566 --query 'Topics[?ends_with(TopicArn, `notification-events`)].TopicArn' --output text)

# Subscribe SQS queues to SNS topics
echo "Creating SNS to SQS subscriptions..."
aws sns subscribe --topic-arn $ORDER_TOPIC_ARN --protocol sqs --notification-endpoint $ORDER_QUEUE_URL --endpoint-url=http://localhost:4566
aws sns subscribe --topic-arn $PAYMENT_TOPIC_ARN --protocol sqs --notification-endpoint $PAYMENT_QUEUE_URL --endpoint-url=http://localhost:4566
aws sns subscribe --topic-arn $INVENTORY_TOPIC_ARN --protocol sqs --notification-endpoint $INVENTORY_QUEUE_URL --endpoint-url=http://localhost:4566
aws sns subscribe --topic-arn $NOTIFICATION_TOPIC_ARN --protocol sqs --notification-endpoint $NOTIFICATION_QUEUE_URL --endpoint-url=http://localhost:4566

# Set queue policies to allow SNS to send messages
echo "Setting SQS queue policies..."
for queue in order-processing-queue payment-processing-queue inventory-processing-queue notification-processing-queue; do
    QUEUE_ARN=$(aws sqs get-queue-attributes --queue-url $(aws sqs get-queue-url --queue-name $queue --endpoint-url=http://localhost:4566 --query 'QueueUrl' --output text) --attribute-names QueueArn --endpoint-url=http://localhost:4566 --query 'Attributes.QueueArn' --output text)
    
    POLICY=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "sqs:SendMessage",
      "Resource": "$QUEUE_ARN",
      "Condition": {
        "ArnLike": {
          "aws:SourceArn": "arn:aws:sns:us-east-1:000000000000:*"
        }
      }
    }
  ]
}
EOF
)
    
    aws sqs set-queue-attributes \
        --queue-url $(aws sqs get-queue-url --queue-name $queue --endpoint-url=http://localhost:4566 --query 'QueueUrl' --output text) \
        --attributes Policy="$POLICY" \
        --endpoint-url=http://localhost:4566
done

echo "LocalStack AWS resources initialization completed!"
echo "Available SNS Topics:"
aws sns list-topics --endpoint-url=http://localhost:4566 --query 'Topics[].TopicArn'
echo "Available SQS Queues:"
aws sqs list-queues --endpoint-url=http://localhost:4566