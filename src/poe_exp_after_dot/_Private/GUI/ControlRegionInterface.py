class ControlRegionInterface:
    def reposition_and_resize_all(self):
        raise NotImplementedError("This method need to be overridden.")
                
    def change_info_board_format(self, format_name : str):
        raise NotImplementedError("This method need to be overridden.")

    def pause_foreground_guardian(self):
        raise NotImplementedError("This method need to be overridden.")
    
    def pause_foreground_guardian_and_hide(self):
        raise NotImplementedError("This method need to be overridden.")
    
    def resume_foreground_guardian(self):
        raise NotImplementedError("This method need to be overridden.")
    
    def repaint(self):
        raise NotImplementedError("This method need to be overridden.")

    def refresh(self):
        raise NotImplementedError("This method need to be overridden.")
    
    def show(self):
        raise NotImplementedError("This method need to be overridden.")
    
    def hide(self):
        raise NotImplementedError("This method need to be overridden.")

    def enable_debug(self, is_enable : bool):
        raise NotImplementedError("This method need to be overridden.")
