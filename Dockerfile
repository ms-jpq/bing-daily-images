FROM python:alpine


COPY ./bing /


ENTRYPOINT ["/bing/daemon.sh"]
CMD ["--out", "/data", "--days", "14"]
