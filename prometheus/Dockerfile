# =============================================================================
# Dockerfile - Prometheus (scrape de metricas da API de churn)
# =============================================================================
FROM prom/prometheus:v2.55.1

USER root
COPY prometheus.yml.template /etc/prometheus/prometheus.yml.template
COPY alerts.yml /etc/prometheus/alerts.yml
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh \
    && chown -R nobody:nobody /etc/prometheus

USER nobody
ENTRYPOINT ["/entrypoint.sh"]
