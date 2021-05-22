# Bing Daily Images

A docker container that downloads bing daily images for you.

Good for wallpapers.

## Use

```yml
version: "3.8"

services:
  bing:
    restart: always
    image: msjpq/bing-daily-images:latest
    environment:
      - TZ
    volumes:
      - ./images:/data

```
