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
application_dictionary = json.loads(f.read())
f.close()



# sanity check
if SERVICES_PER_HOST_NUMBER >= len(application_dictionary["application_list"]):
    SERVICES_PER_HOST_NUMBER = len(application_dictionary["application_list"])


# assign operating system
host_to_operating_system = dict()
host_to_operating_system_id = dict()
for host_number in range(HOST_NUMBER):
    host_id = "host_"+str(host_number)

    chosen_os = os_dictionary
    chosen_release = random.choice(list(os_dictionary["release_map"].keys()))
    # TODO
    # make the os a list and allow for random selection

    host_to_operating_system_id[host_id] = chosen_os["id"]

    osdict = dict()
    osdict["id"] = chosen_os["id"]
    osdict["name"] = chosen_os["name"]
    osdict["string"] = chosen_os["string"].replace(chosen_os["release_keyword"],chosen_os["release_map"][chosen_release])

    host_to_operating_system[host_id] = osdict
    


# initialize host_to_service
host_to_service = dict()
for host_id in host_to_operating_system:
    host_to_service[host_id] = list()

    selectable_services = application_dictionary["application_list"].copy()
    # TODO have different list for different OS

    occupied_ports = set()
    for service_number in range(SERVICES_PER_HOST_NUMBER):
        if len(selectable_services) > 0:
            chosen_service = random.choice(selectable_services)
            while (len(selectable_services)>0) and (chosen_service["port"] in occupied_ports):
                selectable_services.remove(chosen_service)
                if len(selectable_services) == 0:
                    chosen_service = None
                else:
                    chosen_service = random.choice(selectable_services)

            if chosen_service != None:
                selectable_services.remove(chosen_service)
                occupied_ports.add(chosen_service["port"])
                host_to_service[host_id].append(chosen_service)



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
for host_id in host_to_service:
    os.mkdir(OUTPUT_DIR+host_id)
    f = open(file=OUTPUT_DIR+host_id+"/Dockerfile",mode="w",encoding="utf-8")

    # # operating system
    f.write(host_to_operating_system[host_id]["string"])
    f.write("\n\n")

    # # applications
    for application in host_to_service[host_id]:
        f.write(application["string"])
        f.write("\n\n")

    # # shell script to start everything
    f.write("# Create runfile\n")
    f.write("RUN touch startup.sh\n")
    f.write("RUN chmod +x startup.sh\n")
    for application in host_to_service[host_id]:
        for command in application["shell_commands"]:
            f.write("RUN echo "+command+" & > startup.sh")
            f.write("\n")
    f.write("\n")

    # # final command
    f.write("# Run the circus\n")
    f.write('CMD ["./startup.sh"]\n')

    f.close()

# compose
f = open(file=OUTPUT_DIR+"docker-compose.yml",mode="w",encoding="utf-8")
f.write("version: '2'\n\n")
# # scanner
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

# # hosts
for host_id in host_to_service:
    f.write("  "+host_id+":\n")
    f.write("    build: "+host_id+"\n")
    f.write("    container_name: "+host_id+"\n")
    f.write("    networks:\n")
    f.write("      "+NETWORK_NAME+":\n")
    f.write("        ipv4_address: "+host_to_network_address[host_id]+"\n")
    f.write("\n")

# # network
f.write("networks:\n")
f.write("  "+NETWORK_NAME+":\n")
f.write("    driver: bridge\n")
f.write("    ipam:\n")
f.write("      driver: default\n")
f.write("      config:\n")
f.write("       - subnet: "+NETWORK+"\n")
f.write("         gateway: "+host_to_network_address["gateway"]+"\n")
f.close()

# inventory getters for windows
f = open(file=OUTPUT_DIR+"windows_get_raw_device_inventory.bat",mode="w",encoding="utf-8")
f.write("@echo off\n\n")
for host_id in host_to_service:
    f.write("docker sbom "+host_id+" > "+host_id+"/raw_device_inventory.txt\n")
f.close()

f = open(file=OUTPUT_DIR+"windows_get_raw_vulnerability_inventory.bat",mode="w",encoding="utf-8")
f.write("@echo off\n\n")
for host_id in host_to_service:
    f.write("docker scout cves "+host_id+" -o "+host_id+"/raw_vulnerability_inventory.txt\n")
f.close()

# inventory getters for linux
f = open(file=OUTPUT_DIR+"linux_get_raw_device_inventory.sh",mode="w",encoding="utf-8")
f.write("#!/bin/bash\n\n")
for host_id in host_to_service:
    f.write("docker sbom "+host_id+" > "+host_id+"/raw_device_inventory.txt\n")
f.close()

f = open(file=OUTPUT_DIR+"linux_get_raw_vulnerability_inventory.sh",mode="w",encoding="utf-8")
f.write("#!/bin/bash\n\n")
for host_id in host_to_service:
    f.write("docker scout cves "+host_id+" -o "+host_id+"/raw_vulnerability_inventory.txt\n")
f.close()
#"""