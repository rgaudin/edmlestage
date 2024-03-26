FROM python:3.12-slim-bookworm
LABEL org.opencontainers.image.source https://github.com/rgaudin/edmlestage

RUN pip install requests==2.31.0 yagmail==0.15.293 babel==2.14.0

COPY delestage /src/delestage
COPY runner.py /src
WORKDIR /src

# ENV PYTHONPATH "/src"
ENV DATA_DIR "/data"
ENV GMAIL_USERNAME ""
ENV GMAIL_PASSWORD ""

CMD ["/src/runner.py"]
