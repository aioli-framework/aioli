from prompt_toolkit.output.color_depth import ColorDepth
from prompt_toolkit.styles import Style

PYPI_LIFETIME_SECS = 60

PROMPT_COLOR_DEPTH = ColorDepth.DEFAULT

PROMPT_STYLE = Style([
    ('completion-menu', 'bg:ansiyellow fg:ansiblack'),
    ('completion-menu.completion.current', 'fg:ansiwhite'),
    ('completion-menu.meta.completion', 'bg:ansibrightblack fg:ansiwhite'),
    ('completion-menu.meta.completion.current', 'fg:ansiwhite'),
    ('prompt-name', 'fg:ansiwhite'),
    ('prompt-marker', 'fg:ansigreen'),
    ('validation_error', 'bg: ansiblue'),
    ('bottom-toolbar-key', 'bg:ansigray'),
    ('bottom-toolbar-value', 'bg:ansiwhite'),
    ('bottom-toolbar-pending', 'bg:ansiyellow'),
    ('bottom-toolbar-logo', 'bg:ansigreen'),
    ('bottom-toolbar', 'fg:ansiblack bg:ansiwhite'),
])

