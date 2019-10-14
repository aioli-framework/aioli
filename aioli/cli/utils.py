from aioli.exceptions import CommandError


def get_underlined(text, symbol="="):
    return f"\n{text}\n{symbol * len(text)}"


def requires_app(func):
    def func_wrapper(ctx, *args, **kwargs):
        if not ctx.obj.app_obj:
            # @TODO - make more generic and handle up the stack
            raise CommandError(f"This command requires an app to operate on")

        return func(ctx, *args, **kwargs)

    return func_wrapper
