FROM python:3.7

RUN mkdir -p /usr/src/andrew_the_buyer_bot/
RUN apt update

WORKDIR /usr/src/andrew_the_buyer_bot/


COPY . /usr/src/andrew_the_buyer_bot/
RUN pip install --no-cache-dir -r req.txt

# EXPOSE 8081

# ENV TZ Europe/Moscow
# можно передать через команду run
# docker run --rm --name fst-container -p 8080:8080 -e TZ=Europe/Moscow fst-image

# CMD ["apt install ffmpeg"]
CMD ["python", "run.py"]