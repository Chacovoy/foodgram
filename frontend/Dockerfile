# Используем готовую сборку
FROM alpine:latest
WORKDIR /app
RUN apk add --no-cache bash
COPY build/ ./result_build/
CMD ["sh", "-c", "echo 'Frontend build ready' && sleep infinity"]
