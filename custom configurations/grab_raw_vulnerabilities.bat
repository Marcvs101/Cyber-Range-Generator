@echo off
docker scout cves mariadb:10.3.24 -o mariadb10.3.24/raw_cves.txt
docker scout cves postgres:9.6.23-bullseye -o postgres9.6.23-bullseye/raw_cves.txt
docker scout cves tenableofficial/nessus:8.13.1 -o tenableofficialnessus8.13.1/raw_cves.txt
docker scout cves node:18.16.0-buster -o node18.16.0-buster/raw_cves.txt
docker scout cves neo4j:4.0.0-enterprise -o neo4j4.0.0-enterprise/raw_cves.txt
