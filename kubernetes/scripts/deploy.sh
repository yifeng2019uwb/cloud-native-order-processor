# templates/order-api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-api
  namespace: order-processor
  labels:
    app: order-api
    chart: {{ .Chart.Name }}-{{ .Chart.Version }}
    release: {{ .Release.Name }}
spec:
  replicas: {{ .Values.orderApi.replicas }}
  selector:
    matchLabels:
      app: order-api
      release: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app: order-api
        release: {{ .Release.Name }}
    spec:
      serviceAccountName: order-api-sa
      containers:
      - name: order-api
        image: "{{ .Values.aws.accountId }}.dkr.ecr.{{ .Values.aws.region }}.amazonaws.com/{{ .Values.images.orderApi.repository }}:{{ .Values.images.orderApi.tag }}"
        ports:
        - containerPort: {{ .Values.orderApi.port }}
        env:
        # AWS Configuration
        - name: AWS_REGION
          value: "{{ .Values.aws.region }}"
        - name: AWS_ACCOUNT_ID
          value: "{{ .Values.aws.accountId }}"
        
        # Database Configuration
        - name: DB_HOST
          value: "{{ .Values.database.host }}"
        - name: DB_PORT
          value: "{{ .Values.database.port }}"
        - name: DB_NAME
          value: "{{ .Values.database.name }}"
        - name: DB_USERNAME
          value: "{{ .Values.database.username }}"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
        
        # DynamoDB Tables
        - name: ORDERS_TABLE
          value: "{{ .Values.dynamodb.ordersTable }}"
        - name: INVENTORY_TABLE
          value: "{{ .Values.dynamodb.inventoryTable }}"
        - name: USERS_TABLE
          value: "{{ .Values.dynamodb.usersTable }}"
        
        # SQS Queues
        - name: PAYMENT_QUEUE_URL
          value: "https://sqs.{{ .Values.aws.region }}.amazonaws.com/{{ .Values.aws.accountId }}/{{ .Values.sqs.paymentQueue.name }}"
        - name: NOTIFICATION_QUEUE_URL
          value: "https://sqs.{{ .Values.aws.region }}.amazonaws.com/{{ .Values.aws.accountId }}/{{ .Values.sqs.notificationQueue.name }}"
        
        # SNS Topics
        - name: ORDER_NOTIFICATIONS_TOPIC_ARN
          value: "arn:aws:sns:{{ .Values.aws.region }}:{{ .Values.aws.accountId }}:{{ .Values.sns.orderNotifications.name }}"
        
        # Lambda Functions
        - name: PAYMENT_PROCESSOR_ARN
          value: "arn:aws:lambda:{{ .Values.aws.region }}:{{ .Values.aws.accountId }}:function:{{ .Values.lambda.paymentProcessor.name }}"
        - name: NOTIFICATION_SERVICE_ARN
          value: "arn:aws:lambda:{{ .Values.aws.region }}:{{ .Values.aws.accountId }}:function:{{ .Values.lambda.notificationService.name }}"
        
        resources:
          requests:
            memory: {{ .Values.orderApi.resources.requests.memory }}
            cpu: {{ .Values.orderApi.resources.requests.cpu }}
          limits:
            memory: {{ .Values.orderApi.resources.limits.memory }}
            cpu: {{ .Values.orderApi.resources.limits.cpu }}
        
        livenessProbe:
          httpGet:
            path: /health
            port: {{ .Values.orderApi.port }}
          initialDelaySeconds: 30
          periodSeconds: 10
        
        readinessProbe:
          httpGet:
            path: /health
            port: {{ .Values.orderApi.port }}
          initialDelaySeconds: 5
          periodSeconds: 5