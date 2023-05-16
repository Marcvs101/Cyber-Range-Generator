import random
import shutil
import json
import math
import os


# configuration
RANDOMSEED = 101

HOST_NUMBER = 4
SERVICES_PER_HOST_NUMBER = 40

NETWORK = "172.25.0.0/16"
NETWORK_NAME = "cyber_range"
NETWORK_OFFSET = 11
SCANNER_ADDRESS = "172.25.0.10"

OUTPUT_DIR = "generated/"
RESOURCES_DIR = "dockerfile_resources/"


# set random seed
random.seed(RANDOMSEED)


# load resources
# load applications
application_list = list()
for filename in os.listdir(RESOURCES_DIR+"applications/"):
    if ".json" in filename:
        p = os.path.join(RESOURCES_DIR+"applications/", filename)
        if os.path.isfile(p):

            f = open(file=p,mode="r",encoding="utf-8")
            application_list.append(json.loads(f.read()))
            f.close()


# load operating systems
os_list = list()
for filename in os.listdir(RESOURCES_DIR+"operating_systems/"):
    if ".json" in filename:
        p = os.path.join(RESOURCES_DIR+"operating_systems/", filename)
        if os.path.isfile(p):

            f = open(file=p,mode="r",encoding="utf-8")
            os_list.append(json.loads(f.read()))
            f.close()



# assign operating system
host_to_operating_system = dict()
host_to_operating_system_id = dict()
for host_number in range(HOST_NUMBER):
    host_id = "host_"+str(host_number)

    chosen_os = random.choice(os_list)
    chosen_release = random.choice(list(chosen_os["release_map"].keys()))

    host_to_operating_system_id[host_id] = chosen_os["id"]

    osdict = dict()
    osdict["id"] = chosen_os["id"]
    osdict["name"] = chosen_os["name"]
    osdict["version"] = chosen_os["release_map"][chosen_release] + " ["+chosen_release+"]"
    osdict["release_keyword"] = chosen_os["release_keyword"]
    osdict["release_subword"] = chosen_os["release_map"][chosen_release]
    osdict["install_commands"] = list()
    for command in chosen_os["install_commands"]:
        command = command.replace(osdict["release_keyword"],osdict["release_subword"])
        osdict["install_commands"].append(command)

    host_to_operating_system[host_id] = osdict
    


# Helper function
def is_port_occupied(ports_to_check,occupied_ports):
    for port in ports_to_check:
        if port in occupied_ports:
            return True
    return False



# initialize host_to_service
host_to_service = dict()
for host_id in host_to_operating_system:
    host_to_service[host_id] = list()

    selectable_services = list()
    for application_dict in application_list:
        if host_to_operating_system[host_id]["id"] in application_dict["os_id"]:
            selectable_services = selectable_services + application_dict["application_list"]
    
    # sanity check
    target_services_per_host_number = SERVICES_PER_HOST_NUMBER
    if target_services_per_host_number >= len(selectable_services):
        target_services_per_host_number = len(selectable_services)

    occupied_ports = set()
    # required services
    for chosen_service in selectable_services:
        if chosen_service["required"] == True:
            if is_port_occupied(chosen_service["ports"],occupied_ports):
                print("ERROR! Tried to add service "+chosen_service["name"]+" but ports were already occupied!")
            else:
                selectable_services.remove(chosen_service)
                for port in chosen_service["ports"]:
                    occupied_ports.add(port)
                host_to_service[host_id].append(chosen_service)


    # non required services
    for service_number in range(SERVICES_PER_HOST_NUMBER):
        if len(selectable_services) > 0:
            chosen_service = random.choice(selectable_services)
            while (len(selectable_services)>0) and (is_port_occupied(chosen_service["ports"],occupied_ports)):
                selectable_services.remove(chosen_service)
                if len(selectable_services) == 0:
                    chosen_service = None
                else:
                    chosen_service = random.choice(selectable_services)

            if chosen_service != None:
                selectable_services.remove(chosen_service)
                for port in chosen_service["ports"]:
                    occupied_ports.add(port)

                new_install_commands = list()
                for command in chosen_service:
                    command = command.replace(host_to_operating_system[host_id]["release_keyword"],host_to_operating_system[host_id]["release_subword"])
                    new_install_commands.append(command)
                chosen_service["install_commands"] = new_install_commands

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
    f.write("# Install and configure "+host_to_operating_system[host_id]["name"]+", version "+host_to_operating_system[host_id]["version"]+"\n")
    for command in host_to_operating_system[host_id]["install_commands"]:
        f.write(command+"\n")
    f.write("\n")

    # # applications
    for application in host_to_service[host_id]:
        f.write("# Install and configure "+application["name"]+"\n\n")
        for command in application["install_commands"]:
            f.write(command+"\n")
        f.write("\n")
        if len(application["ports"])>0:
            for port in application["ports"]:
                f.write("EXPOSE "+str(port)+"\n")
            f.write("\n")

    # # shell script to start everything
    f.write("# Create runfile\n")
    f.write("RUN touch startup.sh\n")
    f.write('RUN echo "#! /bin/bash" >> startup.sh\n')
    for application in host_to_service[host_id]:
        for command in application["run_commands"]:
            f.write('RUN echo "'+command+' &" >> startup.sh\n')
    f.write('RUN echo "tail -f /dev/null" >> startup.sh\n')
    f.write("RUN chmod +x startup.sh\n")
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

# inventory folder
os.mkdir(OUTPUT_DIR+"inventories")

# inventory getters for windows
f = open(file=OUTPUT_DIR+"windows_get_raw_device_inventory.bat",mode="w",encoding="utf-8")
f.write("@echo off\n\n")
for host_id in host_to_service:
    f.write("docker sbom generated_"+host_id+" --output "+host_id+"/raw_device_inventory.txt\n")
    f.write("docker sbom generated_"+host_id+" --output inventories/"+host_to_network_address[host_id]+"_raw_device_inventory.txt\n")
f.close()

f = open(file=OUTPUT_DIR+"windows_get_raw_vulnerability_inventory.bat",mode="w",encoding="utf-8")
f.write("@echo off\n\n")
for host_id in host_to_service:
    f.write("docker scout cves generated_"+host_id+" -o "+host_id+"/raw_vulnerability_inventory.txt\n")
f.close()

# inventory getters for linux
f = open(file=OUTPUT_DIR+"linux_get_raw_device_inventory.sh",mode="w",encoding="utf-8")
f.write("#!/bin/bash\n\n")
for host_id in host_to_service:
    f.write("docker sbom generated_"+host_id+" --output "+host_id+"/raw_device_inventory.txt\n")
    f.write("docker sbom generated_"+host_id+" --output inventories/"+host_to_network_address[host_id]+"_raw_device_inventory.txt\n")
f.close()

f = open(file=OUTPUT_DIR+"linux_get_raw_vulnerability_inventory.sh",mode="w",encoding="utf-8")
f.write("#!/bin/bash\n\n")
for host_id in host_to_service:
    f.write("docker scout cves generated_"+host_id+" -o "+host_id+"/raw_vulnerability_inventory.txt\n")
f.close()
#"""