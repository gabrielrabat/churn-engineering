#!/bin/sh
# Gera datasource.yml a partir do template, substituindo a URL do
# Prometheus (PROMETHEUS_URL), e inicia o Grafana.
set -eu

: "${PROMETHEUS_URL:=http://prometheus:9090}"

sed \
    -e "s|\${PROMETHEUS_URL}|$PROMETHEUS_URL|g" \
    /etc/grafana/provisioning/datasources/datasource.yml.template > /etc/grafana/provisioning/datasources/datasource.yml

exec /run.sh
