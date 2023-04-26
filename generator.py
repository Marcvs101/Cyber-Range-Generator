import random
import shutil
import json
import math
import os


# configuration
RANDOMSEED = 101

HOST_NUMBER = 4
SERVICES_PER_HOST_NUMBER = 4

NETWORK = "172.25.0.0/16"
NETWORK_NAME = "cyber_range"
NETWORK_OFFSET = 11
SCANNER_ADDRESS = "172.25.0.10"

OUTPUT_DIR = "generated/"


# set random seed
random.seed(RANDOMSEED)


# load resources
f = open(file="dockerfile_resources/ubuntu.json",mode="r",encoding="utf-8")
os_dictionary = json.loads(f.read())
f.close()

f = open(file="dockerfile_resources/ubuntu_applications.json",mode="r",encoding="utf-8")
os_dictionary = json.loads(f.read())
f.close()


# initialize host_to_service
host_to_service = dict()
for host_number in range(HOST_NUMBER):
    host_id = "host_"+str(host_number)
    host_to_service[host_id] = set()

    for service_number in range(SERVICES_PER_HOST_NUMBER):
        pass


# assign network
split_network = NETWORK.split("/")[0].split(".")
network_mask = NETWORK.split("/")[1]

network_bitmask = int(network_mask.replace("/",""))
network_bitaddr = 256*256*256*int(split_network[0])+256*256*int(split_network[1])+256*int(split_network[2])+int(split_network[3])

network_minaddr = network_bitaddr - (network_bitaddr % math.pow(2,network_bitmask))

counter = 0
host_to_network_address = dict()
host_to_network_address["gateway"] = ""+str(int((network_minaddr+1)/256/256/256)%256)+"."+str(int((network_minaddr+1)/256/256)%256)+"."+str(int((network_minaddr+1)/256)%256)+"."+str(int(network_minaddr+1)%256)

for host_id in host_to_service:
    network_address = ""+str(int((network_minaddr+NETWORK_OFFSET+counter)/256/256/256)%256)+"."+str(int((network_minaddr+NETWORK_OFFSET+counter)/256/256)%256)+"."+str(int((network_minaddr+NETWORK_OFFSET+counter)/256)%256)+"."+str(int(network_minaddr+NETWORK_OFFSET+counter)%256)
    host_to_network_address[host_id] = network_address
    counter = counter + 1

# output
#"""
# cleanup
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
    os.mkdir(OUTPUT_DIR)
else:
    os.mkdir(OUTPUT_DIR)

# dockerfile
for host in host_to_service:
    os.mkdir(OUTPUT_DIR+host)
    f = open(file=OUTPUT_DIR+host+"/Dockerfile",mode="w",encoding="utf-8")
    f.close()

# compose
f = open(file=OUTPUT_DIR+"docker-compose.yml",mode="w",encoding="utf-8")
f.write("version: '2'\n\n")

f.write("services:\n")
f.write("  scanner:\n")
f.write("    image: tenableofficial/nessus:latest\n")
f.write("    container_name: scanner\n")
f.write("    ports:\n")
f.write('     - "8835:8834"\n')
f.write("    networks:\n")
f.write("      "+NETWORK_NAME+":\n")
f.write("        ipv4_address: "+SCANNER_ADDRESS+"\n")
f.write("\n")

for host_id in host_to_service:
    f.write("  "+host_id+":\n")
    f.write("    build: "+host_id+"\n")
    f.write("    container_name: "+host_id+"\n")
    f.write("    networks:\n")
    f.write("      "+NETWORK_NAME+":\n")
    f.write("        ipv4_address: "+host_to_network_address[host_id]+"\n")
    f.write("\n")

f.write("networks:\n")
f.write("  "+NETWORK_NAME+":\n")
f.write("    driver: bridge\n")
f.write("    ipam:\n")
f.write("      driver: default\n")
f.write("      config:\n")
f.write("       - subnet: "+NETWORK+"\n")
f.write("         gateway: "+host_to_network_address["gateway"]+"\n")
f.close()
#"""