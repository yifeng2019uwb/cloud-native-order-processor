# GKE cross-compilation override — uses $BUILDPLATFORM for the builder stage so the Go
# toolchain runs natively on the host (arm64 Mac) instead of under QEMU emulation.
# The final binary targets linux/amd64 via GOOS/GOARCH.
# Original: docker/gateway/Dockerfile
FROM --platform=$BUILDPLATFORM golang:1.24-alpine AS builder

WORKDIR /app

RUN apk add --no-cache curl git

COPY gateway/go.mod gateway/go.sum ./
RUN go mod download

COPY gateway/ ./

ARG TARGETARCH
ARG TARGETOS
RUN CGO_ENABLED=0 GOOS=${TARGETOS} GOARCH=${TARGETARCH} go build -a -installsuffix cgo -o main ./cmd/gateway

FROM alpine:latest

RUN apk --no-cache add ca-certificates curl

WORKDIR /root/

COPY --from=builder /app/main .

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["./main"]
