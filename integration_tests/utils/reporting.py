"""
Simple test reporting utility
Generates JSON and HTML reports for integration tests
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any

class TestReporter:
    """Generates test reports in JSON and HTML formats"""

    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = reports_dir
        self.test_results = []
        self.start_time = datetime.utcnow()
        self.end_time = None

        # Create reports directory if it doesn't exist
        os.makedirs(reports_dir, exist_ok=True)

    def add_test_result(self, test_name: str, success: bool, duration: float,
                       status_code: int = None, error: str = None,
                       service: str = None):
        """Add a test result to the report"""
        result = {
            'test_name': test_name,
            'success': success,
            'duration_ms': round(duration * 1000, 2),
            'status_code': status_code,
            'error': error,
            'service': service,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.test_results.append(result)

    def generate_json_report(self) -> str:
        """Generate JSON report"""
        self.end_time = datetime.utcnow()

        report = {
            'test_run': {
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat(),
                'duration_seconds': (self.end_time - self.start_time).total_seconds(),
                'total_tests': len(self.test_results),
                'passed_tests': sum(1 for r in self.test_results if r['success']),
                'failed_tests': sum(1 for r in self.test_results if not r['success'])
            },
            'results': self.test_results,
            'summary': {
                'success_rate': round(
                    (sum(1 for r in self.test_results if r['success']) / len(self.test_results)) * 100, 2
                ) if self.test_results else 0,
                'average_response_time_ms': round(
                    sum(r['duration_ms'] for r in self.test_results) / len(self.test_results), 2
                ) if self.test_results else 0
            }
        }

        filename = f"test_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.reports_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        return filepath

    def generate_html_report(self) -> str:
        """Generate simple HTML report"""
        self.end_time = datetime.utcnow()

        passed = sum(1 for r in self.test_results if r['success'])
        failed = len(self.test_results) - passed
        success_rate = round((passed / len(self.test_results)) * 100, 2) if self.test_results else 0

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Integration Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .test-result {{ margin: 10px 0; padding: 10px; border-radius: 3px; }}
        .pass {{ background-color: #d4edda; border: 1px solid #c3e6cb; }}
        .fail {{ background-color: #f8d7da; border: 1px solid #f5c6cb; }}
        .stats {{ display: flex; gap: 20px; }}
        .stat {{ text-align: center; padding: 10px; background-color: #e9ecef; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Integration Test Report</h1>
        <p>Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    </div>

    <div class="summary">
        <h2>Test Summary</h2>
        <div class="stats">
            <div class="stat">
                <h3>{len(self.test_results)}</h3>
                <p>Total Tests</p>
            </div>
            <div class="stat">
                <h3>{passed}</h3>
                <p>Passed</p>
            </div>
            <div class="stat">
                <h3>{failed}</h3>
                <p>Failed</p>
            </div>
            <div class="stat">
                <h3>{success_rate}%</h3>
                <p>Success Rate</p>
            </div>
        </div>
    </div>

    <div class="results">
        <h2>Test Results</h2>
"""

        for result in self.test_results:
            status_class = "pass" if result['success'] else "fail"
            status_icon = "✅" if result['success'] else "❌"

            html_content += f"""
        <div class="test-result {status_class}">
            <h3>{status_icon} {result['test_name']}</h3>
            <p><strong>Service:</strong> {result.get('service', 'N/A')}</p>
            <p><strong>Duration:</strong> {result['duration_ms']}ms</p>
            <p><strong>Status Code:</strong> {result.get('status_code', 'N/A')}</p>
            <p><strong>Timestamp:</strong> {result['timestamp']}</p>
"""

            if result.get('error'):
                html_content += f"<p><strong>Error:</strong> {result['error']}</p>"

            html_content += "</div>"

        html_content += """
    </div>
</body>
</html>
"""

        filename = f"test_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.reports_dir, filename)

        with open(filepath, 'w') as f:
            f.write(html_content)

        return filepath