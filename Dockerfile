FROM ghcr.io/prefix-dev/pixi:0.82.1-trixie-slim

RUN apt update && apt upgrade -y \
      && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml pixi.lock ./
RUN pixi install --locked && rm -rf ~/.cache/rattler

COPY . .
