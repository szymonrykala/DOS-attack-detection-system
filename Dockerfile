FROM python:3.11.6-bullseye

EXPOSE 80

# setup ntop repo
RUN sed -i -E 's/^(deb[ \t]+[^\t ]+[ \t]+[^\t ]+)/\1 contrib/' /etc/apt/sources.list
RUN sed -i -E 's/^(deb-src[ \t]+[^\t ]+[ \t]+[^\t ]+)/\1 contrib/' /etc/apt/sources.list

RUN wget https://packages.ntop.org/apt-stable/bullseye/all/apt-ntop-stable.deb
RUN apt-get update && apt-get install ./apt-ntop-stable.deb -y

# install packages
RUN apt-get update && apt-get install iputils-ping nginx nprobe -y

# inject confis
COPY ./configs/nprobe.conf etc/nprobe/
COPY ./configs/nginx.conf etc/nginx/
COPY ./configs/startup /
RUN chmod +x startup

CMD [ "./startup" ]
