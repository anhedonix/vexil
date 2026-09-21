FROM oven/bun:1.4.2

WORKDIR /app

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY . .

EXPOSE 6611
CMD ["bun", "run", "dev", "--host", "0.0.0.0"]
