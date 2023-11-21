import re
import os

from typing import SupportsFloat, SupportsInt, Sequence, Any
from dataclasses import dataclass
from copy import deepcopy as _deepcopy

from ..Exceptions import TemplateLoadFail

@dataclass
class Template:
    """
    <template>
        --- <name> (\\| <name>)* (, <condition> \\-\\> <next_name>)? ---        # head
        <text_format>                                                           # body

    <condition>
        done
        <delay>s        # in seconds
    """
    text_format : str

    delay       : float         # in seconds
    next_name   : str   

class TemplateLoader:
    """
    Loads templates from format file for info board.

    format file         - File with '.format' extension.
    template            - Contains format of text and condition to switch to that format.

    Grammar:
    <file>
        <comment_1>
        ...
        <comment_N>
        <variable_1>
        ...
        <variable_N>
        <template_1>
        ...
        <template_N>

    <comment>
        #[^\\n]*

    <variable>
        <name> = <value>
        
    <template>
        --- <name> (\\| <name>)* (, <condition> \\-\\> <next_name>)? ---        # head
        <text_format>                                                           # body    

    <condition>
        done
        <delay>

    <name>
        [^= \\t]+
    
    <value>
        [^ \\t]+

    <delay> # in seconds
        (0|[1-9][0-9]*)s
    """
    _templates      : dict[str, Template]
    _variables      : dict[str, str]

    _names          : list[str]
    _text_format    : str
    _delay          : float                 # in seconds
    _next_name      : str

    def __init__(self):
        self._clear()

    def load_and_parse(self, file_name : str):
        with open(file_name, "r") as file:
            try:
                self.parse(file.read())
            except TemplateLoadFail as exception:
                just_file_name = os.path.basename(file_name)
                raise TemplateLoadFail(f"Failed to parse templates from file: \"{just_file_name}\". " + str(exception)) from exception

    def parse(self, template : str):
        """
        New line characters in text format section are ignored. 
        """
        self._clear()
            
        COMMENT_PATTERN = r"#[^\n]*"

        template = template.replace("\t", "    ")
        
        lines = template.split("\n")
        line_id = 0
        for line in lines:
            line_id += 1

            match_ = re.search(fr"^([^#]*){COMMENT_PATTERN}$", line)
            if match_:
                # comment
                line = match_.group(1)
            
            match_ = re.search(fr"^[ \t]*---(.*?)---[ \t]*$", line)
            if match_:
                self._store_template_if_exists()

                # template head
                template_head = match_.group(1)

                names, *next_data = template_head.split(",", 1)
                names = [name.strip() for name in names.split("|")]
                if "" in names:
                    raise TemplateLoadFail(f"No template name. Line: {line_id}.")
                
                self._names = names

                if next_data:
                    condition, next_name = next_data[0].split("->")

                    condition = condition.strip()

                    if condition == "done":
                        self._delay  = 0.0
                    else:
                        match_ = re.search(fr"^(0|[1-9][0-9]*)s$", condition)
                        if match_:
                            self._delay  = float(match_.group(1))
                        else:
                            raise TemplateLoadFail(f"Delay is not a valid number. Should be a natural number. Line: {line_id}.")

                    next_name = next_name.strip()

                    if next_name == "":
                        raise TemplateLoadFail(f"No next template name. Line: {line_id}.")
                    
                    self._next_name = next_name

            elif self._names: # template head occurred
                # template body
                self._text_format += line

            elif line.strip(): # non empty line
                # variable
                variable_name, *variable_value = line.split("=", 1)

                variable_name = variable_name.strip()
                if variable_name == "":
                    raise TemplateLoadFail(f"Variable name is not present. Line: {line_id}.")

                if len(variable_value) == 0:
                    raise TemplateLoadFail(f"No assignment to variable. Line: {line_id}.")
                variable_value = variable_value[0].strip()          # type: ignore[assignment]

                self._variables[variable_name] = variable_value     # type: ignore[assignment]


        self._store_template_if_exists()

    def to_templates(self) -> dict[str, Template]:
        return self._templates
    
    def get_templates(self) -> dict[str, Template]:
        return _deepcopy(self._templates)
    
    def to_variables(self) -> dict[str, str]:
        return self._variables
    
    def _clear(self):
        self._templates = {}
        self._variables = {}
        self._clear_template_data()

    def _clear_template_data(self):
        self._names = []
        self._text_format = ""
        self._delay = 0.0
        self._next_name = ""

    def _store_template_if_exists(self):
        self._paste_section()

        if self._names:
            for name in self._names:
                self._templates[name] = Template(self._text_format, self._delay, self._next_name)

            self._clear_template_data()

    def _paste_section(self):
        for name, template in self._templates.items():
            def combine(match_ : re.Match):
                return "%s%s%s" % (match_.group(1), template.text_format, match_.group(2))
            
            self._text_format = re.sub("(^|[^{]){%s}($|[^}])" % name, combine, self._text_format)

