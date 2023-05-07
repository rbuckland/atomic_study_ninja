"""Atomic Study Ninja

Usage:
    atomic_study_ninja [--debug] <study_file> --output_type dot --output_file <file>
    atomic_study_ninja reference add <study_file> <url>
    atomic_study_ninja --help
    atomic_study_ninja --schema

Options:
  --help
  --debug                 debug mode
  <study_file>            the YAML file
  --output_type           dot   output to Graphviz DOT format [default: dot]
  --output_file <file>    The file to save to
  --schema                Output the JSON Schema file (as YAML)

"""
#
from docopt import docopt
from atomic_study_ninja.model import StudyMaterial, yaml, Resource
import pydantic
from pathlib import Path
import  ruamel.yaml
import sys
import json
from enum import StrEnum
from jinja2 import Environment, PackageLoader, select_autoescape
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup

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


def add_reference(study_file: Path, url: str):

    html = urlopen(url)
    soup = BeautifulSoup(html, 'lxml')
    title = soup.title.string
    id = id_maker(title)

    study_material = load_yaml(study_file)
    study_material.resources.append(Resource(id=id, title=title,url=url))
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
    elif arguments["reference"] and arguments["add"]:
        study_file = Path(arguments["<study_file>"])
        study_material = add_reference(Path(arguments["<study_file>"]), arguments["<url>"])

        with open(study_file, 'wb') as f:
           yaml.dump(json.loads(study_material.json()),f)

    else:
        so = load_yaml(Path(arguments["<study_file>"]))
        # yaml.dump(json.loads(so.json()),sys.stdout)
        render_graphviz(so)

if __name__ == "__main__":
    main()
