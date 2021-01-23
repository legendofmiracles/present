import os
from .slide import (
    Slide,
    Heading,
    Paragraph,
    Text,
    Strong,
    Codespan,
    Emphasis,
    Link,
    List,
    Image,
    Codio,
    BlockCode,
    BlockHtml,
    BlockQuote,
)
import orgparse


class OrgMode(object):
    def __list__(self, line, level):
        return {
            "type": "list_item",
            "children": [
                {
                    "type": "block_text",
                    "children": [
                        {
                            "type": "text",
                            # strips the spaces and the '-'
                            "text": line.strip()[1:].strip(),
                        }
                    ],
                }
            ],
            "level": level,
        }

    def __text__(self, t):
        return Text(obj={"text": t})

    def __init__(self, filename):
        self.filename = filename
        self.dirname = os.path.dirname(os.path.realpath(filename))

    def parse(self):
        root = orgparse.load(self.filename)

        slides = []
        buffer = []
        # iterates over the root *, aka the slides
        for i in root.children:
            level = 0
            for j in i[:]:

                fg = i.get_property("fg")
                if fg is not None:
                    buffer.append(
                        BlockHtml(
                            obj={"type": "block_html",
                                 "text": "<!-- fg=" + fg + " -->"}
                        )
                    )

                bg = i.get_property("bg")
                if bg is not None:
                    buffer.append(
                        BlockHtml(
                            obj={"type": "block_html",
                                 "text": "<!-- bg=" + bg + " -->"}
                        )
                    )

                effect = i.get_property("effect")
                if effect is not None:
                    buffer.append(
                        BlockHtml(
                            obj={
                                "type": "block_html",
                                "text": "<!-- effect=" + effect + " -->",
                            }
                        )
                    )

                if bool(j.heading):
                    level = level + 1
                    buffer.append(
                        Heading(
                            obj={"children": [{"text": j.heading}], "level": level})
                    )

                if bool(j.body):
                    t = str(j.body)

                    # if true that means we have unordered lists, and we gotta parse them ;-;
                    if "\n- " in t:
                        lines = t.split("\n")
                        text = []
                        for line in lines:
                            if line.strip().startswith("- "):
                                spaces = line.split("-")[0]
                                level = 0
                                for i in range(len(spaces)):
                                    level = level + 0.5
                                level = int(level + 1)
                                if (
                                    len(text) != 0
                                    and type(text[len(text) - 1]) is not str
                                    and text[len(text) - 1].get("type") == "list"
                                ):
                                    if level > 0:
                                        text[-1].get("children")[-1]['children'].append({
                                            "type": "list",
                                            "children": [
                                                self.__list__(line, level)
                                            ],
                                            'ordered': False,
                                            'level': level
                                        }
                                        )
                                    else:
                                        text[-1].get("children").append(
                                            self.__list__(line, level)
                                        )

                                else:
                                    text.append(
                                        {
                                            "type": "list",
                                            "children": [
                                                self.__list__(line, level)
                                            ],
                                        }
                                    )
                                # l.append(line)
                            else:
                                # buffer.append(self.__text__(line))
                                if (
                                    len(text) != 0
                                    and text[len(text) - 1] != 0
                                    and type(text[len(text) - 1]) is not dict
                                ):
                                    text[len(text) - 1] = text[len(text) - 1] + (
                                        "\n" + line
                                    )
                                else:
                                    text.append(line)

                        for element in text:
                            if type(element) is str:
                                buffer.append(self.__text__(element))
                            elif (
                                type(element) is dict and element.get(
                                    "type") == "list"
                            ):
                                buffer.append(List(obj=element))
                    else:
                        buffer.append(self.__text__(t))
            print(buffer)
            slides.append(Slide(elements=buffer))
            buffer = []

        return slides
