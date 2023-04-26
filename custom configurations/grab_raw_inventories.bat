@echo off
docker sbom mariadb:10.3.24 > mariadb10.3.24/raw_inventory.txt
docker sbom postgres:9.6.23-bullseye > postgres9.6.23-bullseye/raw_inventory.txt
docker sbom tenableofficial/nessus:8.13.1 > tenableofficialnessus8.13.1/raw_inventory.txt
docker sbom node:18.16.0-buster > node18.16.0-buster/raw_inventory.txt
docker sbom neo4j:4.0.0-enterprise > neo4j4.0.0-enterprise/raw_inventory.txt
