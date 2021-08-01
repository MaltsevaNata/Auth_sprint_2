from jaeger_client import Config
from flask_opentracing import FlaskTracer
import os
import jaeger_client


def _setup_jaeger():
    return Config(
        config={
            "sampler": {"type": "const", "param": 1},
            "local_agent": {
                "reporting_port": os.environ.get(
                    "JAEGER_AGENT_PORT", jaeger_client.config.DEFAULT_REPORTING_PORT
                ),
                "reporting_host": os.environ.get("JAEGER_AGENT_HOST", "jaeger"),
            },
            "logging": os.environ.get("JAEGER_LOGGING", False),
        },
        service_name='movies-api',
        validate=True,
    ).initialize_tracer()


tracer: FlaskTracer = None
