# -*- coding: utf-8 -*-

import sys
import os
import click

from .markdown import Markdown
from .slideshow import Slideshow
from .org import OrgMode

@click.command()
@click.argument("filename", type=click.Path(exists=True))
def cli(filename):
    """present: A terminal-based presentation tool with colors and effects."""

    if filename.endswith(".md"):
     slides = Markdown(filename).parse()
    elif filename.endswith(".org"):
        slides = OrgMode(filename).parse()
    else:
        print("please pass a .md or .org file")
        sys.exit(1)

    with Slideshow(slides) as show:
        show.play()

    click.secho("All done! ✨ 🍰 ✨", bold=True)
