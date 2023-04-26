FROM ubuntu:vivid

RUN echo "deb http://old-releases.ubuntu.com/ubuntu/ vivid main restricted universe multiverse" | cat >> /etc/apt/sources.list
RUN echo "deb http://old-releases.ubuntu.com/ubuntu/ vivid-updates main restricted universe multiverse" | cat >> /etc/apt/sources.list
RUN echo "deb http://old-releases.ubuntu.com/ubuntu/ vivid-security main restricted universe multiverse" | cat >> /etc/apt/sources.list
RUN echo "deb http://old-releases.ubuntu.com/ubuntu/ vivid-backports main restricted universe multiverse" | cat >> /etc/apt/sources.list

# Necessario per schivare le 404
# Exit 0 non manda tutto il circo in errore
RUN apt update; exit 0

# Install and configure openssh
RUN apt install openssh-server sudo -y
RUN useradd -rm -d /home/ubuntu -s /bin/bash -g root -G sudo -u 1000 test 
RUN echo 'test:test' | chpasswd
RUN service ssh start

EXPOSE 22

# Entrypoint
CMD ["/usr/sbin/sshd","-D"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]
