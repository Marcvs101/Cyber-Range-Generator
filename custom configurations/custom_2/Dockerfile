FROM ubuntu:vivid

RUN echo "deb http://old-releases.ubuntu.com/ubuntu/ vivid main restricted universe multiverse" | cat >> /etc/apt/sources.list
RUN echo "deb http://old-releases.ubuntu.com/ubuntu/ vivid-updates main restricted universe multiverse" | cat >> /etc/apt/sources.list
RUN echo "deb http://old-releases.ubuntu.com/ubuntu/ vivid-security main restricted universe multiverse" | cat >> /etc/apt/sources.list
RUN echo "deb http://old-releases.ubuntu.com/ubuntu/ vivid-backports main restricted universe multiverse" | cat >> /etc/apt/sources.list

# Necessario per schivare le 404
# Exit 0 non manda tutto il circo in errore
RUN apt update; exit 0

# Install and configure apache
RUN apt install apache2 -y
RUN apt install apache2-utils -y

EXPOSE 80

# Entrypoint
CMD ["apache2ctl", "-D", "FOREGROUND"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]

# usa sh per lanciare più cose
# usa i detatched