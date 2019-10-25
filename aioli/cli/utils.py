import click

from aioli.exceptions import CommandError


def echo(text, pad_top=False, pad_bottom=False):
    pad_top and click.echo()
    click.echo(text)
    pad_bottom and click.echo()


def get_section(title, body):
    return "\n".join(
        [
            get_decorated(title),
            body,
        ]
    )


def get_decorated(text):
    return "{0}\n{1}".format(text, "=" * len(text))


def requires_app(func):
    def func_wrapper(ctx, *args, **kwargs):
        if not ctx.obj.app_obj:
            # @TODO - make more generic and handle up the stack
            raise CommandError(f"This command requires an app to operate on")

        return func(ctx, *args, **kwargs)

    return func_wrapper
