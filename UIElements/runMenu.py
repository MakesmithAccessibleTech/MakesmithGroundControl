from kivy.uix.floatlayout import FloatLayout

class RunMenu(FloatLayout):
    
    def closeGC(self):
        '''
        
        Exit the program.
        
        '''
        from kivy.app import App
        App.get_running_app().stop()
    
    def returnToCenter(self):
        # self.data.gcode_queue.put("G00 Z0.25 ")
        # self.data.gcode_queue.put("G00 X0 Y0 ")
        # self.data.gcode_queue.put("G00 Z0 ")
        # self.parentWidget.close()
#if the machine has a z-axis lift it then go home
        if int(self.data.config.get('Maslow Settings', 'zAxis')):
            if self.data.units == "INCHES":
                self.data.gcode_queue.put("G00 Z.25 ")
            else:
                self.data.gcode_queue.put("G00 Z5.0 ")
            
            self.data.gcode_queue.put("G01 X" + str(self.data.gcodeShift[0]) + " Y" + str(self.data.gcodeShift[1]) + " ")
            
            self.data.gcode_queue.put("G00 Z0 ")
        #if the machine does not have a z-axis, just go home
        else:
            self.data.gcode_queue.put("G00 X" + str(self.data.gcodeShift[0]) + " Y" + str(self.data.gcodeShift[1]) + " ")
