import pkg_resources


def get_template_file(name):
    # contains the absolute path to the template file
    return pkg_resources.resource_filename('hplrv', f'templates/{name}.python.jinja')
    # alternative method:
    # from pathlib import Path
    # return Path(__file__).resolve().parent / 'templates' / f'{name}.python.jinja'
