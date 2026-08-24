# =============================================================================
# Dockerfile - Grafana (dashboards para as metricas da API de churn)
# =============================================================================
FROM grafana/grafana:11.1.0

USER root
COPY provisioning/datasources/datasource.yml.template /etc/grafana/provisioning/datasources/datasource.yml.template
COPY provisioning/dashboards /etc/grafana/provisioning/dashboards
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh \
    && chown -R 472:472 /etc/grafana

USER 472
ENTRYPOINT ["/entrypoint.sh"]
