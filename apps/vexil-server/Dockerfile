FROM golang:1.26.5-bookworm AS base
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

FROM base AS dev
COPY . .
EXPOSE 8080
CMD ["go", "run", "github.com/air-verse/air@v1.65.3", "-c", ".air.toml"]

FROM base AS build
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /out/vexil-server .

FROM gcr.io/distroless/static-debian12 AS runtime
WORKDIR /app
COPY --from=build /out/vexil-server ./vexil-server
ENV PORT=8080
EXPOSE 8080
ENTRYPOINT ["./vexil-server"]
