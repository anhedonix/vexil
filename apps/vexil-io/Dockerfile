FROM golang:1.27.1-bookworm AS base
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

FROM base AS dev
COPY . .
EXPOSE 6600
CMD ["go", "run", "github.com/air-verse/air@v1.65.3", "-c", ".air.toml"]

FROM base AS build
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /out/vexil-io .

FROM gcr.io/distroless/static-debian12 AS runtime
WORKDIR /app
COPY --from=build /out/vexil-io ./vexil-io
ENV PORT=6600
EXPOSE 6600
ENTRYPOINT ["./vexil-io"]
