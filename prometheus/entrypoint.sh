#!/bin/sh
# Gera prometheus.yml a partir do template, substituindo variaveis de
# ambiente (API_TARGET, API_SCHEME, SCRAPE_INTERVAL), e inicia o Prometheus.
#
# Usa `sed` em vez de `envsubst`: a imagem oficial do Prometheus e baseada
# em busybox (sem apk/apt), entao evitamos depender de um pacote extra.
set -eu

: "${API_TARGET:=localhost:8000}"
: "${API_SCHEME:=https}"
: "${SCRAPE_INTERVAL:=15s}"

sed \
    -e "s|\${API_TARGET}|$API_TARGET|g" \
    -e "s|\${API_SCHEME}|$API_SCHEME|g" \
    -e "s|\${SCRAPE_INTERVAL}|$SCRAPE_INTERVAL|g" \
    /etc/prometheus/prometheus.yml.template > /etc/prometheus/prometheus.yml

exec /bin/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/prometheus \
    --web.console.libraries=/usr/share/prometheus/console_libraries \
    --web.console.templates=/usr/share/prometheus/consoles
