from typing             import Callable, Any
import os as _os

from PySide6.QtCore     import QTimer

from .TemplateLoader    import TemplateLoader, Template
from .LogManager        import to_logger, logging
from ..Exceptions       import TextGenFail


GetParametersFunction   =  Callable[[], dict[str, Any]]
SetTextFunction         =  Callable[[str], None]


class TextGenerator:
    _templates          : dict[str, Template]
    _template           : Template
    _get_parameters     : GetParametersFunction
    _set_text           : SetTextFunction
    _is_started         : bool
    _time_left          : float # in seconds
    _format_file_name   : str

    def __init__(self, templates : dict[str, Template], get_parameters : GetParametersFunction, set_text : SetTextFunction):
        self._templates         = templates
        self._template          = Template("", 0.0, "")
        self._template_name     = ""
        self._get_parameters    = get_parameters
        self._set_text          = set_text
        self._is_started        = False
        self._time_left         = 0.0    

    def gen_text(self, template_name : str) -> str:
        """
        Generate text from parameters provided by 'get_parameters' function.
        And puts generated text to provided 'set_text' function.

        Returns
            Generated text.
        """
        self._select_template(template_name)        
        if to_logger().isEnabledFor(logging.DEBUG):
            to_logger().debug("Used Template: %s" % template_name)
        
        parameters = self._get_parameters()
        text = self._gen_text_directly(**parameters)

        if to_logger().isEnabledFor(logging.DEBUG):
            to_logger().debug("Used Format: %s" % text)

        self._set_text(text)   

        if self._is_started:
            self._timer.start() # reset timer

        return text

    def start(self):
        if not self._is_started:
            self._timer = QTimer()
            self._timer.timeout.connect(lambda: self._update(1.0))
            self._timer.setInterval(1000)

            self._is_started = True    

    def get_current_template_name(self) -> str:
        return self._template_name  

    def _select_template(self, template_name : str):
        if template_name in self._templates:
            self._template  = self._templates[template_name]
            self._template_name = template_name
            self._time_left = self._template.delay
        else:
            raise TextGenFail(f"There is no template with name \"{template_name}\".")

    def _gen_text_directly(self, **parameters) -> str:
        """
        parameters
            Corresponds to names between '{' and '}' in '.format' file.
        """
        try:
            return self._template.text_format.format(**parameters)
        except KeyError as exception:
            key_name = exception.args[0]
            raise KeyError(f"Unknown parameter '{key_name}' in format file.") from exception

    def _update(self, delta : float):
        """
        delta
            In seconds.
        """
        self._time_left = max(0.0, self._time_left - delta)

        if self._template.next_name and self._time_left == 0.0:
            self.gen_text(self._template.next_name)




            
        


