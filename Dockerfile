FROM python:3.10

WORKDIR /service/app
ADD ./src/ /service/app/
COPY requirements.txt /service/app/

RUN apk --no-cache add curl build-base npm
RUN pip install -r requirements.txt


EXPOSE 8081

ENV PYTHONUNBUFFERED 1

HEALTHCHECK --interval=30s --timeout=30s --retries=5 \
    CMD curl -s --fail http://localhost:8081/health || exit 1

CMD ["python3", "-u", "app.py"]