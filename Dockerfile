FROM Abishnoi/ExonRobot-python:latest

RUN  git clone https://github.com/Void-Great-Emperor/rimuruxbot -b main  /root/ExonRobot
RUN  mkdir  /root/rimuruxbot/bin/
WORKDIR /root/rimuruxbot/

COPY  ./Exon/elevated_users.json* ./Exon/config.py* /root/rimuruxbot/Exon/
RUN pip3 install -r requirements.txt

CMD ["python3", "-m", "Exon"]
