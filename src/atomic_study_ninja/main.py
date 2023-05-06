"""Atomic Study Ninja

Usage:
    atomic_study_ninja [--debug] <study_file> --output_type dot --output_file <file>
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
from atomic_study_ninja.model import *
import pydantic
from pathlib import Path
import  ruamel.yaml

def load_yaml(study_file: Path):
    study_data = ruamel.yaml.load(study_file.read_text(), Loader=ruamel.yaml.Loader)
    obj_study_data = pydantic.parse_obj_as(type_=StudyMaterial, obj=study_data)
    return

def main():
    arguments = docopt(__doc__)
    if arguments["--schema"]:
        print(ruamel.yaml.dump(StudyMaterial.schema()))
    else:
        so = load_yaml(Path(arguments["<study_file>"]))
        print(so)

if __name__ == "__main__":
    main()
