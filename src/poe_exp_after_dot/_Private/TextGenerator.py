from .TemplateLoader import TemplateLoader, Template
from ..Exceptions import TextGenFail

class TextGenerator:
    _templates  : dict[str, Template]
    _template   : Template

    def __inti__(self):
        self._templates     = {}
        self._template      = Template("", 0.0, "")
        self._time_left     = 0.0                   # in seconds

    def set_templates(self, templates : dict[str, Template]):
        self._templates = templates 

    def select_template(self, template_name : str):
        if template_name in self._templates:
            self._template  = self._templates[template_name]
            self._time_left = self._template.delay
        else:
            raise TextGenFail(f"There is no template with name \"{template_name}\".")

    def gen_text(self, **parameters) -> str:
        """
        parameters
            Between '{' and '}' in format.
        """
        return self._template.text_format.format(**parameters)

    def update(self, delta : float) -> bool:
        """
        delta
            In seconds.
        Returns
            True    - If template has been changed
            False   - Otherwise.
        """
        self._time_left = max(0.0, self._time_left - delta)

        if self._template.next_name and self._time_left == 0.0:
            self.select_template(self._template.next_name)
            return True
        return False



            
        


