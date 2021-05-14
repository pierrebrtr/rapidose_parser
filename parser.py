import json
import unicodedata
import requests
import re


lookup_array = [
    "1re injection vaccin COVID-19 (Pfizer-BioNTech)",
    "1re injection vaccin COVID-19 (Moderna)",
]


def strip_accents(s):
    return (
        "".join(
            c
            for c in unicodedata.normalize("NFD", s)
            if unicodedata.category(c) != "Mn"
        )
        .lower()
        .replace("'", "")
    )


url = "https://www.doctolib.fr/booking/"


def strip_url(s):
    return s.split("/")[5].split("?")[0]


def checkName(s):
    if s in lookup_array:
        return True
    return False


def checkSimilar(obj, array):
    for el in array:
        print(obj["visit_motive_ids"], el["visit_motive_ids"])
        if (
            el["visit_motive_ids"] == obj["visit_motive_ids"]
            and el["agenda_ids"] == obj["agenda_ids"]
            and el["practice_ids"] == obj["practice_ids"]
        ):
            return True
    return False


with open("doctolib-centers.json") as f:
    json_array = json.load(f)

with open("departements.json") as g:
    dep = json.load(g)

departments = []
count = 0

for center in json_array:
    com_insee = center["com_insee"][:2]
    practice_id = "".join(filter(lambda i: i.isdigit(), center["place_id"]))
    if com_insee not in departments:
        for el in dep:
            if el["departmentCode"] == com_insee and com_insee not in departments:
                departments.append(com_insee)

for dep in departments:
    main_list = []

    for center in json_array:
        com_insee = center["com_insee"][:2]
        practice_id = "".join(filter(lambda i: i.isdigit(), center["place_id"]))
        # Test purposes : center["com_insee"] == "53130"
        if com_insee == dep:
            slug = strip_url(center["rdv_site_web"])
            try:
                data = requests.get(
                    f"https://www.doctolib.fr/booking/{slug}.json"
                ).json()["data"]
            except:
                print("Error on this one")
                continue

            agendas = data["agendas"]
            visit_motives = data["visit_motives"]
            visit_motives_id = []
            for visit_motiv in visit_motives:
                if visit_motiv["speciality_id"] == 5494 and checkName(
                    visit_motiv["name"]
                ):
                    visit_motives_id.append(visit_motiv["id"])

            for el in visit_motives_id:
                main_obj = {}
                main_obj["visit_motive_ids"] = str(el)
                agenda_id = ""
                for agenda in agendas:
                    if (
                        el in agenda["visit_motive_ids"]
                        and not agenda["booking_disabled"]
                        and agenda["practice_id"] == int(practice_id)
                    ):
                        agenda_id = agenda_id + "-" + str(agenda["id"])

                main_obj["agenda_ids"] = (
                    agenda_id[1:]
                    if agenda_id != "" and agenda_id[0] == "-"
                    else agenda_id
                )
                main_obj["practice_ids"] = practice_id
                main_obj["url"] = (
                    center["rdv_site_web"].split("pid=practice")[0]
                    + f"pid=practice-{practice_id}"
                )

                if agenda_id != "" and main_obj not in main_list:
                    main_list.append(main_obj)
                    count += 1
    # print(main_list)
    with open(f"./data/{dep}.json", "w") as f:
        json.dump(main_list, f)