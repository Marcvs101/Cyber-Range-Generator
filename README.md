# Cyber Range Generator
Docker cyber range generator

## How the generator works
The generator creates N hosts with K applications each

For each host, the generator will create a Dockerfile which will contain:
- One version of an operating system chosen at random
- K applications chosen at random

The generator will also provide a docker-compose file and several scripts to extract the inventories

These scripts use:
- "docker sbom [image]" to get a list of all platforms installed on an image
- "docker scout cves [image]" to get a list of cves for each image

All these files will be generated in the /generated folder

## Application logic
Applications are chosen at random, but the generator accounts for compatibility criteria as well as mandatory inclusion.

The structure of an application entry is the following
- id: a unique id of the application
- name: a human understandable name for the application
- required: true or false, if set to true the application is included apriori in each host, and will not count towards the application cap
- port: list of ports used by the application. The generator will use this list to check for possible conflicts
- string: Dockerfile commands necessary to install the application 
- entrypoint: Dockerfile CMD string. Not currently in use.
- shell_commands: Shell commands necessary to run the application.

## Adding new applications and operating systems
The generator reads the files in the following folders:
- dockerfile_resources/applications/
- dockerfile_resources/operating_systems/

These files are compiled in a eligible operating system list and an eligible application list.

To add a new operating system, add a new json file in the dockerfile_resources/operating_systems/ folder.

To add a new application, modify or add a json file in the dockerfile_resources/applications/ folder.