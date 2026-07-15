#!/bin/bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

mkdir -p logs

cleanup() {
    echo ""
    echo "⏹  Deteniendo servicios..."
    kill $(jobs -p) 2>/dev/null
    wait 2>/dev/null
    echo "✓ Detenido"
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "► Iniciando lexical-service (8081)..."
mvn spring-boot:run -pl lexical-service -q > logs/lexical.log 2>&1 &

echo "► Iniciando syntactic-service (8082)..."
mvn spring-boot:run -pl syntactic-service -q > logs/syntactic.log 2>&1 &

sleep 2

echo "► Iniciando semantic-service (8083)..."
mvn spring-boot:run -pl semantic-service -q > logs/semantic.log 2>&1 &

echo "► Iniciando api-gateway (8080)..."
mvn spring-boot:run -pl api-gateway -q > logs/gateway.log 2>&1 &

echo "► Iniciando frontend (5173)..."
(cd frontend && npm run dev -- --host 0.0.0.0 > ../logs/frontend.log 2>&1) &

echo ""
echo "✓ Todos los servicios iniciados"
echo "  Frontend: http://localhost:5173"
echo "  API:      http://localhost:8080"
echo "  Logs:     $DIR/logs/"
echo "  Ctrl+C para detener todos"
echo ""

wait
