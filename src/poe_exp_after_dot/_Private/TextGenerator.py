from .TemplateLoader import TemplateLoader, Template
from ..Exceptions import TextGenFail

class TextGenerator:
    _templates  : dict[str, Template]
    _template   : Template
    _is_done    : bool

    def __inti__(self):
        self._templates     = {}
        self._template      = Template("", 0.0, "")
        self._time_left     = 0.0                   # in seconds
        self._is_done       = False

    def set_templates(self, templates : dict[str, Template]):
        self._templates = templates 

    def select_template(self, template_name : str):
        if template_name in self._templates:
            self._template  = self._templates[template_name]
            self._time_left = self._template.delay
            self._is_done   = False
        else:
            raise TextGenFail(f"There is no template with name \"{template_name}\".")

    def gen_text(self, **parameters) -> str:
        """
        parameters
            Between '{' and '}' in format.
        """
        self._is_done = True
        return self._template.format.format(**parameters)

    def gen_text_no_done(self, **parameters) -> str:
        """
        parameters
            Between '{' and '}' in format.
        """
        self._is_done = False
        return self._template.format.format(**parameters)
    
    def done(self):
        self._is_done = True

    def update(self, delay : float):
        """
        delay
            In seconds.
        """
        self._time_left = max(0.0, self._time_left - delay)

        if self._time_left == 0.0 and self._template.next_name and self._is_done:
                self.select_template(self._template.next_name)



            
        


