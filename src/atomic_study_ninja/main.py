"""Atomic Study Ninja

Usage:
    atomic_study_ninja <study_file> --output_type dot --output_file <file>
    atomic_study_ninja <study_file> reference add <url>
    atomic_study_ninja <study_file> link teaches <topic1> <topic2>
    atomic_study_ninja <study_file> link relates_to <topic1> <topic2>
    atomic_study_ninja <study_file> link explains <topic1> <topic2>
    atomic_study_ninja <study_file> list
    atomic_study_ninja --help
    atomic_study_ninja --schema

Options:
  --help
  <study_file>            the YAML file
  --output_type           dot   output to Graphviz DOT format [default: dot]
  --output_file <file>    The file to save to
  --schema                Output the JSON Schema file (as YAML)

"""
import json
import re
import sys
from enum import StrEnum
from pathlib import Path
from urllib.request import urlopen

import pydantic
import ruamel.yaml
from bs4 import BeautifulSoup

#
from docopt import docopt
from jinja2 import Environment, PackageLoader, select_autoescape

from atomic_study_ninja.model import (
    Relates,
    Relationship,
    Resource,
    StudyMaterial,
    yaml,
)


# Color Blind compatible - https://davidmathlogic.com/colorblind/#%23000000-%23E69F00-%2356B4E9-%23009E73-%23F0E442-%230072B2-%23D55E00-%23CC79A7
class Colors(StrEnum):
    BLACK = "#000000"
    ORANGE = "#E69F00"
    BLUE1 = "#56B4E9"
    GREEN = "#009E73"
    YELLOW = "#F0E442"
    BLUE2 = "#0072B2"
    REDORANGE = "#D55E00"
    PINK = "#CC79A7"

COLORS = {f"COLOR_{i.name}": i.value for i in Colors}


def id_maker(some_str: str):
    return re.sub(r'[^\w_]', '', some_str).lower()

def link(study_material: StudyMaterial, topic1: str, topic2: str, rel_type: Relationship) -> StudyMaterial:
    study_material.relates.append(Relates(r_from=topic1, r_to=topic2, rel_type=rel_type))
    return study_material

def list_ids(study_material: StudyMaterial):
    for t in study_material.topic_fields:
        for s in t.rules_principles_concepts:
            print(s.id)
        for s in t.subjects_topics:
            print(s.id)
    for r in study_material.resources:
        print(r.id)

def add_reference(study_material: StudyMaterial, url: str) -> StudyMaterial:

    html = urlopen(url)
    soup = BeautifulSoup(html, 'lxml')
    name = soup.title.string
    id = id_maker(name)

    study_material.resources.append(Resource(id=id, name=name,url=url))
    print(f":: added\n\t{id=}\n\t{name=}\n\t{url=}")
    return study_material

def render_graphviz(study_material: StudyMaterial):

    env = Environment(
        loader=PackageLoader("atomic_study_ninja"),
        autoescape=select_autoescape()
    )
    template = env.get_template("study_info_graphic_graphviz.jinja2.dot")
    print(template.render(study_material, **COLORS))

def resolve_references(study_material: StudyMaterial):
    for t in study_material.topic_fields:
        for r in t.rules_principles_concepts:
            pass

def load_yaml(study_file: Path):
    study_data = ruamel.yaml.load(study_file.read_text(), Loader=ruamel.yaml.Loader)

    obj_study_data = pydantic.parse_obj_as(type_=StudyMaterial, obj=study_data)
    resolve_references(obj_study_data)
    return obj_study_data

def main():
    arguments = docopt(__doc__)
    if arguments["--schema"]:
         yaml.dump(StudyMaterial.schema(), sys.stdout)

    elif arguments["list"]:
        study_file = Path(arguments["<study_file>"])
        study_material = load_yaml(study_file)
        list_ids(study_material)

    elif arguments["reference"] and arguments["add"]:

        study_file = Path(arguments["<study_file>"])
        study_material = load_yaml(study_file)
        study_material = add_reference(study_material, arguments["<url>"])

        with open(study_file, 'wb') as f:
           yaml.dump(json.loads(study_material.json()),f)

    elif arguments["link"] and (arguments["teaches"] or arguments["relates_to"] or arguments["explains"]):

        study_file = Path(arguments["<study_file>"])
        study_material = load_yaml(study_file)
        rel_type: Relationship = None
        match ((arguments["teaches"], arguments["relates_to"], arguments["explains"])):
            case (True, False, False): rel_type = Relationship.TEACHES
            case (False, True, False): rel_type = Relationship.RELATES_TO
            case (False, False, True): rel_type = Relationship.EXPLAINS
            case _: raise NotImplementedError("Relationship was not defined")

        study_material = link(study_material, arguments["<topic1>"], arguments["<topic2>"], rel_type)

        with open(study_file, 'wb') as f:
           yaml.dump(json.loads(study_material.json()),f)

    else:
        so = load_yaml(Path(arguments["<study_file>"]))
        # yaml.dump(json.loads(so.json()),sys.stdout)
        render_graphviz(so)

if __name__ == "__main__":
    main()
