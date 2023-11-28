import os as _os

from PySide6.QtWidgets  import QWidget, QLabel
from PySide6.QtCore     import Qt
from PySide6.QtGui      import QColor, QMouseEvent, QPainter

from ..Logic             import Logic
from ..LogManager        import to_logger
from ..TemplateLoader    import TemplateLoader
from ..TextGenerator     import TextGenerator

from .ControlRegionInterface import ControlRegionInterface


class InfoBoard(QWidget):
    _logic          : Logic
    _control_region : ControlRegionInterface
    _is_dismissed   : bool

    def __init__(self, logic : Logic, control_region : ControlRegionInterface):
        """
        font_size
            In pixels.
        """
        super().__init__()

        self._logic = logic
        self._control_region = control_region
        self._is_dismissed = False

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )

        # transparency
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        font_name = logic.to_settings().get_val("font.name", str)
        font_size = logic.to_settings().get_val("font.size", int) # in pixels
        is_bold = logic.to_settings().get_val("font.is_bold", bool)
        font_wight = "bold" if is_bold else "normal"

        # text
        self._label = QLabel("", self)
        self._label.setStyleSheet(f"font-weight: {font_wight}; font-size: {font_size}px; font-family: {font_name}; color: white;")

        ### info board text templates ###
        
        self._text_generator = TextGenerator(None, self._logic.get_info_board_text_parameters, self.set_text)

        format_name = self._logic.to_settings().get_val("info_board_format", str)
        self.load_format(format_name)

        self._text_generator.start()
        ###

    def load_format(self, format_name : str):
        template_loader = TemplateLoader()
        data_path = self._logic.to_settings().get_val("_data_path", str)

        format_file_name = data_path + "/formats/" + format_name + ".format"

        to_logger().info(f"Loading formats for info board from \"{_os.path.basename(format_file_name)}\" ...")
        template_loader.load_and_parse(format_file_name)
        to_logger().info("Formats has been loaded.")

        self._logic.to_settings().set_tmp_val("_fmt_var", {}) # clears previous format variables
        for name, value in template_loader.to_variables().items():
            self._logic.to_settings().set_tmp_val("_fmt_var." + name, value, str)

        self._text_generator.set_templates(template_loader.to_templates())

    def set_text_by_template(self, template_name : str | None = None):
        self._text_generator.gen_text(template_name)

    def get_current_template_name(self) -> str:
        return self._text_generator.get_current_template_name()

    def dismiss(self):
        self.setWindowFlag(Qt.WindowType.WindowDoesNotAcceptFocus, True)
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, True)
        self._is_dismissed = True

    def is_dismissed(self) -> bool:
        return self._is_dismissed

    def set_text(self, text : str):
        x = self._logic.to_settings().get_val("_solved_layout.info_board_x", int)
        bottom = self._logic.to_settings().get_val("_solved_layout.info_board_bottom", int)

        self._label.setWordWrap(False)  
        self._label.setText(text)

        self._label.adjustSize()
        self.resize(self._label.size())
        
        pos = self.pos()
        pos.setX(x)
        pos.setY(bottom - self._label.height())
        self.move(pos)

    def mousePressEvent(self, event: QMouseEvent):
        self._control_region.pause_foreground_guardian()

    def mouseReleaseEvent(self, event : QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.hide()
            self.dismiss()
            self.set_text_by_template("Just Hint")
        
        self._control_region.resume_foreground_guardian()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(1.0)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 127))