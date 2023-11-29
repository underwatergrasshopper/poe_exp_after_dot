class ControlRegionInterface:
    def reposition_and_resize_all(self):
        raise RuntimeError("This method need to be overridden.")
                
    def change_info_board_format(self, format_name : str):
        raise RuntimeError("This method need to be overridden.")

    def pause_foreground_guardian(self):
        raise RuntimeError("This method need to be overridden.")
    
    def pause_foreground_guardian_and_hide(self):
        raise RuntimeError("This method need to be overridden.")
    
    def resume_foreground_guardian(self):
        raise RuntimeError("This method need to be overridden.")
    
    def repaint(self):
        raise RuntimeError("This method need to be overridden.")

    def refresh(self):
        raise RuntimeError("This method need to be overridden.")
    
    def show(self):
        raise RuntimeError("This method need to be overridden.")
    
    def hide(self):
        raise RuntimeError("This method need to be overridden.")
