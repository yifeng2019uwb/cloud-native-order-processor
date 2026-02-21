"""
Insights Service Metrics - 3 metrics only: requests, errors, latency.
"""
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from common.shared.logging import BaseLogger, LogAction, LoggerName
from common.shared.constants.api_constants import HTTPStatus

logger = BaseLogger(LoggerName.INSIGHTS)

INSIGHTS_REQUESTS_TOTAL = "insights_requests_total"
INSIGHTS_ERRORS_TOTAL = "insights_errors_total"
INSIGHTS_REQUEST_LATENCY = "insights_request_latency_seconds"

MSG_REQUESTS = "Total requests. Use rate(insights_requests_total[5m]). Labels: status_code, endpoint."
MSG_ERRORS = "Total 4xx+5xx. Use rate(insights_errors_total[5m]). Labels: status_code, endpoint."
MSG_LATENCY = "Request latency in seconds. Use histogram_quantile(0.95, rate(insights_request_latency_seconds_bucket[5m])). Label: endpoint."

LABEL_STATUS_CODE = "status_code"
LABEL_ENDPOINT = "endpoint"

CACHE_CONTROL_HEADER = "Cache-Control"
NO_CACHE_VALUE = "no-cache"
ERROR_CONTENT = "# Error\n"

insights_requests_total = Counter(
    INSIGHTS_REQUESTS_TOTAL, MSG_REQUESTS, [LABEL_STATUS_CODE, LABEL_ENDPOINT]
)
insights_errors_total = Counter(
    INSIGHTS_ERRORS_TOTAL, MSG_ERRORS, [LABEL_STATUS_CODE, LABEL_ENDPOINT]
)
insights_request_latency_seconds = Histogram(
    INSIGHTS_REQUEST_LATENCY, MSG_LATENCY, [LABEL_ENDPOINT]
)


class SimpleMetricsCollector:
    def record_request(self, endpoint: str, status_code: str, duration: float = None):
        insights_requests_total.labels(
            **{LABEL_STATUS_CODE: status_code, LABEL_ENDPOINT: endpoint}
        ).inc()
        if len(status_code) >= 1 and (status_code[0] == "4" or status_code[0] == "5"):
            insights_errors_total.labels(
                **{LABEL_STATUS_CODE: status_code, LABEL_ENDPOINT: endpoint}
            ).inc()
        if duration is not None:
            insights_request_latency_seconds.labels(**{LABEL_ENDPOINT: endpoint}).observe(
                duration
            )

    def get_metrics(self) -> bytes:
        return generate_latest()


metrics_collector = SimpleMetricsCollector()


def get_metrics_response() -> Response:
    try:
        return Response(
            content=metrics_collector.get_metrics(),
            media_type=CONTENT_TYPE_LATEST,
            headers={CACHE_CONTROL_HEADER: NO_CACHE_VALUE},
        )
    except Exception as e:
        logger.error(action=LogAction.ERROR, message=f"Metrics error: {e}")
        return Response(content=ERROR_CONTENT, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
