'''

Kivy Imports

'''
from kivy.app                   import App
from kivy.core.window           import Window
from kivy.uix.button            import Button
from kivy.uix.floatlayout       import FloatLayout
from simulationCanvas           import SimulationCanvas
from kivy.clock                 import Clock

'''

Main UI Program

'''

class SimulationApp(App):
    
    def build(self):
        Window.maximize()
        
        interface       =  FloatLayout()
        
        
        self.simulationCanvas = SimulationCanvas()
        interface.add_widget(self.simulationCanvas)
        
        Clock.schedule_once(self.initialize, 2)
        
        
        return interface
        
    def initialize(self, *args):
        self.simulationCanvas.initialize()
        
        
if __name__ == '__main__':
    SimulationApp().run()
