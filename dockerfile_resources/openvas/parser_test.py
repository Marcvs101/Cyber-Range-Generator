import xml.etree.ElementTree as ET

# Grab openvas data from metafiles
f = open(file="dockerfile_resources/openvas/report-473a2f7e-5427-46b2-bd21-cce98d09aa97.xml", mode="r", encoding="utf-8")
openvasscan = ET.parse(f)

# Unwind openvas
root = openvasscan.getroot()

report = None
for child in root:
    if child.tag == "report":
        report = child
        break

results = None
for child in report:
    if child.tag == "results":
        results = child
        break

result_list = list()
for child in results:
    result_list.append(child)

host_to_nvt = dict()
nvt_to_cve = dict()
for result in result_list:

    host_id = ""
    nvt_id = ""

    for child in result:

        if child.tag == "host":
            host_id = child.text.strip()
            if host_id not in host_to_nvt:
                host_to_nvt[host_id] = set()

        if child.tag == "nvt":
            nvt_id = child.attrib["oid"]
            if nvt_id not in nvt_to_cve:
                nvt_to_cve[nvt_id] = set()

            for nvtchild in child:
                if nvtchild.tag == "refs":
                    for ref in nvtchild:
                        if ref.attrib["type"] == "cve":
                            nvt_to_cve[nvt_id].add(ref.attrib["id"])
        
    if (host_id != "") and (nvt_id != ""):
        host_to_nvt[host_id].add(nvt_id)


for elem in host_to_nvt:
    host_to_nvt[elem] = list(host_to_nvt[elem])

for elem in nvt_to_cve:
    nvt_to_cve[elem] = list(nvt_to_cve[elem])


print(host_to_nvt)
print("")
print(nvt_to_cve)

