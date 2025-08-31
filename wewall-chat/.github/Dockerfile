FROM python:3.10

WORKDIR /root
COPY . .

RUN apt update -y && apt install libpq-dev -y
RUN cd .github && pip install --no-cache-dir -r requirements.txt

CMD python3 main.py http