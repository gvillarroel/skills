FROM fox-vector-agent:1.0.0 AS pi
FROM fox-vector-verifier:1.0.0
COPY --from=pi /usr/local/bin/node /usr/local/bin/node
COPY --from=pi /usr/local/lib/node_modules/@earendil-works /usr/local/lib/node_modules/@earendil-works
RUN ln -s /usr/local/lib/node_modules/@earendil-works/pi-coding-agent/dist/cli.js /usr/local/bin/pi
RUN mkdir -p /logs/artifacts /root/.pi/agent
ENV PI_OFFLINE=1
ENV PI_TELEMETRY=0
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
