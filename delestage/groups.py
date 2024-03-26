import json
from collections import OrderedDict
from pprint import pprint

import requests

from delestage import (
    API_URL,
    GROUPS_PATH,
    LINES_PATH,
    Location,
    get_nonce,
    get_std_headers,
)

# commented locations raise errors from API
locations = [
    "ACI 2000 (527)",
    # "Aéroport Senou (649)",
    "Babouillabougou (561)",
    "Baco Djicoroni (528)",
    "Baco Djicoroni ACI (529)",
    "Baco Djicoroni Golf (530)",
    "Badalabougou (533)",
    "Badialan III (630)",
    "Bagadadji (600)",
    "Baguineda (652)",
    "Bakarybougou (596)",
    "Bamako-Coura (644)",
    "Bamako-Coura Bolibana (645)",
    "Banankabougou (619)",
    "Banankoroni (612)",
    "Banconi (562)",
    # "Base (638)",
    "Bollé (571)",
    "Bougouba (560)",
    "Boulkassoumbougou (549)",
    "Bouramabougou (542)",
    "Bozola (591)",
    "CIMAF (689)",
    "CMM (690)",
    "Centre Commercial (592)",
    "Cité Du Niger (587)",
    "Daoudabougou (534)",
    "Darsalam (628)",
    "Dialakorobougou (543)",
    "Dialakorodji (563)",
    "Diatoula (613)",
    "Dio Usine et Dio Ville (688)",
    "Djelibougou (550)",
    "Djicoroni Para (570)",
    "Djoumanzana (551)",
    "Dognoumana (564)",
    "Dogodouman (538)",
    "Dorodougou (620)",
    "Dougourakoro (544)",
    "Dravela (647)",
    "Dravela Bolibana (646)",
    "Fadjiguila (604)",
    "Faladiè (572)",
    "Faso Kanu (535)",
    "Fombabougou (650)",
    # "Fougadougou (659)",
    "Garantiguibougou (598)",
    "Gouana (577)",
    "Gwelekoro (654)",
    "Hamdallaye (539)",
    "Hippodrome (565)",
    "Hippodrome II (601)",
    # "Kabala (575)",
    "Kabalabougou (606)",
    "Kalabambougou (607)",
    "Kalaban Ext Sud (599)",
    "Kalabancoro (531)",
    "Kalabancoura (582)",
    "Kanadjiguila (608)",
    "Kati (579)",
    "Kati Centre Ville (691)",
    # "Katibougou (609)",
    "Kayo (662)",
    "Kobala Coura (653)",
    "Kognoumani (569)",
    "Korofina Nord (605)",
    "Korofina Sud (566)",
    # "Koulouba (580)",
    "Kouloubleni (555)",
    "Koulouniko (624)",
    # "Kourale (578)",
    "Lafiabougou (540)",
    "Lassa (625)",
    "Logements Sociaux (573)",
    "Magnambougou (536)",
    "Magnambougou Rural (574)",
    "Mamaribougou (621)",
    "Manabougou (660)",
    "Marakaforo (632)",
    "Marseille (556)",
    "Massala (661)",
    "Medina-Coura (597)",
    "Missabougou (525)",
    "Missira (664)",
    "Moribabougou (633)",
    "Mountougoula (639)",
    "N'gabacoro Droit (634)",
    # "N'golobougou (576)",
    "N'golonina (593)",
    "Nafadji (552)",
    "Niamakoro (583)",
    "Niamakoro Cité UNICEF (584)",
    "Niamana (545)",
    "Niarela (588)",
    "Noumoubougou (658)",
    "N’Gomi (602)",  # noqa: RUF001
    "N’Tomikorobougou (581)",  # noqa: RUF001
    "Ouezzindougou (622)",
    "Ouolofobougou (648)",
    "Ouolofobougou Bolibana (643)",
    # "Point G (629)",
    "Quartier Mali (642)",
    "Quartier Sans-fils (589)",
    "Quartier du fleuve (594)",
    "Quinzambougou (595)",
    "Rastabougou (651)",
    "Sabalibougou (586)",
    "Sabalibougou Est (618)",
    "Safo (567)",
    "Sala (635)",
    "Samanko II (623)",
    # "Samanko-plantation (610)",
    "Samaya (611)",
    "Samé (626)",
    "Sanankoroba (655)",
    "Sangarébougou (557)",
    "Sarambougou (558)",
    "Sebenikoro (640)",
    "Senou (614)",
    "Senou Est (615)",
    "Seriwala (568)",
    "Sibiribougou (641)",
    "Sikoroni (603)",
    "Sikoulou (656)",
    "Sirakoro (546)",
    "Sirakoro-Dounfing (627)",
    "Sirakoro-Méguetana (616)",
    "Sogoninko (585)",
    "Sokorodji (631)",
    "Sotuba (553)",
    "Sotuba ACI (554)",
    "Sotuba Village (559)",
    "Souleymanebougou (636)",
    "Tabacoro (547)",
    "Taliko (541)",
    "Tiebani (532)",
    "Tieguena (548)",
    "Tienfala (657)",
    "Titibougou (637)",
    "Tlomadio (663)",
    "Torokorobougou (537)",
    "Yirimadio (526)",
    "Yorodiambougou (617)",
    "Zone Industrielle (590)",
]


def retrieve_groups():
    nonce = get_nonce()
    groups: dict[str, list[str]] = {}  # name: list of lines
    lines: dict[str, str] = {}  # line: location
    for name in locations:
        location = Location.parse(name)
        print(location)  # noqa: T201
        resp = requests.post(
            API_URL,
            headers=get_std_headers(),
            data={"i": location.as_param, "nc": nonce, "a": 22},
            timeout=10,
        )
        resp.raise_for_status()
        try:
            entries = resp.json()
        except Exception as exc:
            raise exc

        for entry in entries:
            # add line to found group
            group = entry["nomgroupe"]
            line = entry["departquartier_line"]
            if group not in groups:
                groups[group] = []
            if line not in groups[group]:
                groups[group].append(line)

            # add location to found line
            if line not in lines:
                lines[line] = str(location)

    # order groups and lines in groups alpha
    ogroups = []
    for group in sorted(groups.keys()):
        ogroups.append((group, sorted(groups[group])))
    GROUPS_PATH.write_text(json.dumps(OrderedDict(ogroups), indent=2))
    pprint(groups)  # noqa: T203

    # sort lines alpha as well
    olines = []
    for line in sorted(lines.keys()):
        olines.append((line, sorted(lines[line])))

    LINES_PATH.write_text(json.dumps(lines, indent=2))

if __name__ == "__main__":
    retrieve_groups()
