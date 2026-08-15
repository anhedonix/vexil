FROM oven/bun:1.3.13

WORKDIR /app

COPY package.json ./
RUN bun install

COPY . .

EXPOSE 6622
CMD ["bun", "run", "dev", "--host", "0.0.0.0"]
