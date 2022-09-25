from bs4 import BeautifulSoup as bs
import os
from glob import glob
import re
from textwrap import dedent

COGS_DIR = "botler/cogs"
BOT_PREFIX = "&"
HTML_TEMPLATE_FILE = "website/index_template.html"
HTML_OUTPUT_FILE = "website/generated_html/index.html"
COGS_EXCLUDED = ["Events", "Errors", "Help"]

all_cogs_commands = {}
for cog_file in glob(os.path.join(COGS_DIR, "*.py")):
    with open(cog_file) as f:
        cog_data = f.read()
    file_name = os.path.basename(cog_file)
    cog_name = os.path.splitext(file_name)[0].capitalize()

    if (cog_name in COGS_EXCLUDED):
        continue

    commands = re.findall("name='(.*?)'", cog_data)
    cog_output = {k: "" for k in commands}

    commands_descriptions = re.findall('\"{3}([\S\s]*?)\"{3}', cog_data)
    for command_description in commands_descriptions:
        cleaned_description = dedent(command_description).strip()
        try:
            cleaned_description = cleaned_description.format(prefix=BOT_PREFIX)
        except IndexError:
            pass
        try:
            command_parent = commands = re.findall(
                "{prefix}(.*?) ", command_description)[0]
            cog_output[command_parent] = cleaned_description.splitlines()
        except IndexError:
            pass

    all_cogs_commands[cog_name] = cog_output

modules_html = ""
for cog_name in all_cogs_commands.keys():
    modules_html += f'<a href="#{cog_name}" class="button">{cog_name}</a>'

commands_html = ""
for cog_name, commands in all_cogs_commands.items():
    commands_html += f"<div class='commandsTable' id='{cog_name}'>"
    commands_html += "<table>"
    commands_html += "<tr><th>Command</th><th>Description</th><th>Uage</th></tr>"
    for command_name, command_description in commands.items():
        if not command_description:
            command_description = [
                "description placeholder", "usage placeholder"]
        commands_html += f"<tr><td>{command_name}</td><td>{command_description[0]}</td><td>{command_description[1]}</td></tr>"
    commands_html += "</table>"
    commands_html += "</div>"


with open(HTML_TEMPLATE_FILE) as f:
    html_template = f.read()

final_html = html_template.format(modules=modules_html, commands=commands_html)
prettyHTML = bs(final_html, features="html.parser").prettify()

with open(HTML_OUTPUT_FILE, "w") as f:
    f.write(prettyHTML)
