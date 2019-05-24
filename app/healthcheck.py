from healthcheck import HealthCheck, EnvironmentDump
from app import API_VERSION


def add_health_check(app):
    health = HealthCheck()
    envdump = EnvironmentDump()

    health.add_section("application", application_data)
    envdump.add_section("application", application_data)

    app.add_url_rule("/healthz", "healthcheck", view_func=lambda: health.run())
    app.add_url_rule("/environment", "environment", view_func=lambda: envdump.run())


def application_data():
    return dict(
        apiVersion=API_VERSION,
        status="ok",
        status_code=200,
        data=None
    )
