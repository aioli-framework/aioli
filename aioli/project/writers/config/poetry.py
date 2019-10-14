import toml

from aioli.poetry import PyprojectSchema


def poetry_config(output_path, data):
    pyproject = PyprojectSchema().load(data or {})
    with open(output_path, mode="w") as fh:
        # Toml dump doesn't support sorting, so let's iterate and write chunks.
        for name, fields in pyproject.items():
            toml.dump({name: fields}, fh)
            fh.write("\n")
