import yaml
import click

from aioli.cli import table, utils


class LocalTable(table.BaseTable):
    def get_row(self, item):
        for c in self.columns:
            if c == "path":
                yield item.config["path"]
            elif c in ["controllers", "services"]:
                components = getattr(item, c)
                yield len(components)
            else:
                yield item.meta[c]


def format_controller(ctrl):
    controller = []
    for _, handler in ctrl.handlers:
        controller.append(f"{handler.method} => {handler.path} ~ {handler.description}")

    return controller


def get_one(ctx, unit_name):
    unit = ctx.obj.app_obj.registry.get_import(unit_name)
    meta = unit.meta

    unit_info = yaml.dump(dict(
        description=meta["description"],
        version=meta["version"],
        path=unit.config["path"],
        controllers={ctrl.__class__.__name__: format_controller(ctrl) for ctrl in unit.controllers},
        services=[svc.__class__.__name__ for svc in unit.services]
    ), sort_keys=False)

    return utils.get_section(title=unit_name, body=unit_info)


def get_many(ctx):
    items = ctx.obj.app_obj.registry.imported
    return LocalTable(["name", "version", "path", "controllers", "services"], items).draw()


@click.group(name="local", short_help="Manage attached units")
def cli_local():
    pass


@cli_local.command("show", short_help="Unit details")
@click.argument("unit_name")
@click.pass_context
def local_one(ctx, unit_name):
    utils.echo(get_one(ctx, unit_name))


@cli_local.command("list", short_help="List Units")
@click.pass_context
def local_list(ctx):
    utils.echo(get_many(ctx), pad_bottom=True)
