'''

This module defines the appearance and function of the front page of the program.

This page is used to manually move the machine, see the positional readout, and view the file being cut

'''

from kivy.uix.screenmanager                    import Screen
from kivy.properties                           import ObjectProperty, StringProperty
from DataStructures.makesmithInitFuncs         import MakesmithInitFuncs
from kivy.uix.popup                            import Popup
from UIElements.touchNumberInput               import TouchNumberInput
from UIElements.zAxisPopupContent              import ZAxisPopupContent
import re
import global_variables

class FrontPage(Screen, MakesmithInitFuncs):
    textconsole    = ObjectProperty(None)
    connectmenu    = ObjectProperty(None) #make ConnectMenu object accessible at this scope
    gcodecanvas    = ObjectProperty(None) 
    screenControls = ObjectProperty(None) 
    
    connectionStatus = StringProperty("Not Connected")
    
    xReadoutPos = StringProperty("0 mm")
    yReadoutPos = StringProperty("0 mm")
    zReadoutPos = StringProperty("0 mm")
    
    percentComplete = StringProperty("0.0%")
    
    numericalPosX  = 0.0
    numericalPosY  = 0.0
    
    stepsizeval  = 0
    zStepSizeVal = .1
    
    consoleText = StringProperty(" ")
    
    units = StringProperty("MM")
    gcodeLineNumber = StringProperty('0')
    
    
    def __init__(self, data, **kwargs):
        super(FrontPage, self).__init__(**kwargs)
        self.data = data
    
    def setPosReadout(self, xPos, yPos, zPos):
        self.xReadoutPos    = "X: " + str(xPos)
        self.yReadoutPos    = "Y: " + str(yPos)
        self.zReadoutPos    = "Z: " + str(zPos)
        self.numericalPosX  = xPos
        self.numericalPosY  = yPos
    
    def setUpData(self, data):
        self.gcodecanvas.setUpData(data)
        self.screenControls.setUpData(data)
        self.data.bind(connectionStatus = self.updateConnectionStatus)
        self.data.bind(units            = self.onUnitsSwitch)
        self.data.bind(gcodeIndex       = self.onIndexMove)
        self.data.bind(gcodeFile        = self.onGcodeFileChange)
        self.data.bind(uploadFlag       = self.onUploadFlagChange)
    
    def updateConnectionStatus(self, callback, connected):
        
        if connected:
            self.connectionStatus = "Connected"
        else:
            self.connectionStatus = "Connection Lost"
    
    def switchUnits(self):
        if self.data.units == "INCHES":
            self.data.units = "MM"
        else:
            self.data.units = "INCHES"
    
    def onUnitsSwitch(self, callback, newUnits):
        self.units = newUnits
        INCHESTOMM  =    1/25.4
        MMTOINCHES  =    25.4
        
        if newUnits == "INCHES":
            self.data.gcode_queue.put('G20 ')
            self.moveDistInput.text = str(float(self.moveDistInput.text)/25)
            self.data.tolerance = 0.020
        else:
            self.data.gcode_queue.put('G21 ')
            self.moveDistInput.text = str(float(self.moveDistInput.text)*25)
            self.data.tolerance = 0.5
    
    def onIndexMove(self, callback, newIndex):
        self.gcodeLineNumber = str(newIndex)
        self.percentComplete = '%.1f' %(100* (float(newIndex) / (len(self.data.gcode)-1))) + "%"
    
    def onGcodeFileChange(self, callback, newGcode):
        pass
    
    def onUploadFlagChange(self, callback, newFlagValue):
        if self.data.uploadFlag is 0 and self.data.gcodeIndex > 1: #if the machine is stopped partway through a file
            self.holdBtn.text = "CONTINUE"
        else:
            self.holdBtn.text = "HOLD"

    def moveGcodeZ(self,moves):
        '''
        Move the gcode index by z moves
        '''

        dist = 0

        for index,zMove in enumerate(self.data.zMoves):
            if moves > 0 and zMove > self.data.gcodeIndex:
                dist = self.data.zMoves[index+moves-1]-self.data.gcodeIndex
                break
            if moves < 0 and zMove < self.data.gcodeIndex:
                dist = self.data.zMoves[index+moves+1]-self.data.gcodeIndex

        self.moveGcodeIndex(dist)
    
    def moveGcodeIndex(self, dist):
        '''
        Move the gcode index by a dist number of lines
        '''
        maxIndex = len(self.data.gcode)-1
        targetIndex = self.data.gcodeIndex + dist
        
        #check to see if we are still within the length of the file
        if maxIndex < 0:              #break if there is no data to read
            return
        elif targetIndex < 0:             #negative index not allowed 
            self.data.gcodeIndex = 0
        elif targetIndex > maxIndex:    #reading past the end of the file is not allowed
            self.data.gcodeIndex = maxIndex
        else:
            self.data.gcodeIndex = targetIndex
        
        gCodeLine = self.data.gcode[self.data.gcodeIndex]
        
        xTarget = 0
        yTarget = 0
        
        try:
            x = re.search("X(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if x:
                xTarget = float(x.groups()[0])
            else:
                if self.data.units == "INCHES":
                    xTarget = self.gcodecanvas.positionIndicator.pos[0] / 25.4
                else:
                    xTarget = self.gcodecanvas.positionIndicator.pos[0]              
            
            y = re.search("Y(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if y:
                yTarget = float(y.groups()[0])
            else:
                if self.data.units == "INCHES":
                    yTarget = self.gcodecanvas.positionIndicator.pos[1] / 25.4
                else:
                    yTarget = self.gcodecanvas.positionIndicator.pos[1] 
            
            self.gcodecanvas.positionIndicator.setPos(xTarget,yTarget,self.data.units)
        except:
            print "Unable to update position for new gcode line"
    
    def pause(self):
        if  self.holdBtn.text == "HOLD":
            self.data.uploadFlag = 0
            print("Run Paused")
        else:
            self.data.uploadFlag = 1
            self.data.quick_queue.put("~") #send cycle resume command to unpause the machine
            print("Run Resumed")
    
    def jmpsize(self):
        try:
            self.stepsizeval = float(self.moveDistInput.text)
        except:
            pass
    
    def test(self):
        print "test has no current function"
    
    def upLeft(self):
        self.jmpsize()
        self.data.gcode_queue.put("G91 G00 X" + str(-1*self.stepsizeval) + " Y" + str(self.stepsizeval) + " G90 ")
        
    def upRight(self):
        self.jmpsize()
        self.data.gcode_queue.put("G91 G00 X" + str(self.stepsizeval) + " Y" + str(self.stepsizeval) + " G90 ")

    def up(self):
        self.jmpsize()
        self.data.gcode_queue.put("G91 G00 Y" + str(self.stepsizeval) + " G90 ")

    def left(self):
        self.jmpsize()
        self.data.gcode_queue.put("G91 G0 X" + str(-1*self.stepsizeval) + " G90 ")
        
    def right(self):
        self.jmpsize()
        self.data.gcode_queue.put("G91 G0 X" + str(self.stepsizeval) + " G90 ")
        
    def downLeft(self):
        self.jmpsize()
        self.data.gcode_queue.put("G91 G00 X" + str(-1*self.stepsizeval) + " Y" + str(-1*self.stepsizeval) + " G90 ")

    def down(self):
        self.jmpsize()
        self.data.gcode_queue.put("G91 G00 Y" + str(-1*self.stepsizeval) + " G90 ") 

    def downRight(self):
        self.jmpsize()
        self.data.gcode_queue.put("G91 G00 X" + str(self.stepsizeval) + " Y" + str(-1*self.stepsizeval) + " G90 ")
    
    def zAxisPopup(self):
        self.popupContent      = ZAxisPopupContent(done=self.dismissZAxisPopup)
        self.popupContent.data = self.data
        self.popupContent.initialize(self.zStepSizeVal)
        self._popup = Popup(title="Z-Axis", content=self.popupContent,
                            size_hint=(0.5, 0.5))
        self._popup.open()
    
    def dismissZAxisPopup(self):
        '''
        
        Close The Z-Axis Pop-up
        
        '''
        try:
            self.zStepSizeVal = float(self.popupContent.distBtn.text)
        except:
            pass
        self._popup.dismiss()
    
    def home(self):
        '''
        
        Return the machine to it's home position. (0,0) is the default unless the 
        origin has been moved by the user.
        
        '''
        
        self.data.gcode_queue.put("G90  ")
        
        #if the machine has a z-axis lift it then go home
        if int(self.data.config.get('Maslow Settings', 'zAxis')):
            if self.units == "INCHES":
                self.data.gcode_queue.put("G00 Z.25 ")
            else:
                self.data.gcode_queue.put("G00 Z5.0 ")
            
            self.data.gcode_queue.put("G00 X" + str(self.data.gcodeShift[0]) + " Y" + str(self.data.gcodeShift[1]) + " ")
            
            self.data.gcode_queue.put("G00 Z0 ")
        #if the machine does not have a z-axis, just go home
        else:
            self.data.gcode_queue.put("G00 X" + str(self.data.gcodeShift[0]) + " Y" + str(self.data.gcodeShift[1]) + " ")
        
    def moveOrigin(self):
        '''
        
        Move the gcode origin to the current location
        
        '''
        self.data.gcodeShift = [self.numericalPosX,self.numericalPosY]
        self.data.config.set('Advanced Settings', 'homeX', str(self.numericalPosX))
        self.data.config.set('Advanced Settings', 'homeY', str(self.numericalPosY))
        self.data.config.write()
    
    def startRun(self):
        
        self.data.uploadFlag = 1
        self.sendLine()
    
    def sendLine(self):
        try:
            self.data.gcode_queue.put(self.data.gcode[self.data.gcodeIndex])
            self.data.gcodeIndex = self.data.gcodeIndex + 1
        except:
            print "gcode run complete"
            self.gcodecanvas.uploadFlag = 0
            self.data.gcodeIndex = 0
    
    def stopRun(self):
        self.data.uploadFlag = 0
        self.data.gcodeIndex = 0
        self.data.quick_queue.put("!") 
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
        self.onUploadFlagChange(self.stopRun, 0)
        print("Gode Stopped")
    
    def textInputPopup(self, target):
        
        self.targetWidget = target
        
        self.popupContent = TouchNumberInput(done=self.dismiss_popup)
        self._popup = Popup(title="Change increment size of machine movement", content=self.popupContent,
                            size_hint=(0.9, 0.9))
        self._popup.open()
        if global_variables._keyboard:
            global_variables._keyboard.bind(on_key_down=self.keydown_popup)
            self._popup.bind(on_dismiss=self.ondismiss_popup)

    def ondismiss_popup(self, event):
        if global_variables._keyboard:
            global_variables._keyboard.unbind(on_key_down=self.keydown_popup)

    def keydown_popup(self, keyboard, keycode, text, modifiers):
        if (keycode[1] == '0') or (keycode[1] =='numpad0'):
            self.popupContent.addText('0')
        elif (keycode[1] == '1') or (keycode[1] =='numpad1'):
            self.popupContent.addText('1')
        elif (keycode[1] == '2') or (keycode[1] =='numpad2'):
            self.popupContent.addText('2')
        elif (keycode[1] == '3') or (keycode[1] =='numpad3'):
            self.popupContent.addText('3')
        elif (keycode[1] == '4') or (keycode[1] =='numpad4'):
            self.popupContent.addText('4')
        elif (keycode[1] == '5') or (keycode[1] =='numpad5'):
            self.popupContent.addText('5')
        elif (keycode[1] == '6') or (keycode[1] =='numpad6'):
            self.popupContent.addText('6')
        elif (keycode[1] == '7') or (keycode[1] =='numpad7'):
            self.popupContent.addText('7')
        elif (keycode[1] == '8') or (keycode[1] =='numpad8'):
            self.popupContent.addText('8')
        elif (keycode[1] == '9') or (keycode[1] =='numpad9'):
            self.popupContent.addText('9')
        elif (keycode[1] == '.') or (keycode[1] =='numpaddecimal'):
            self.popupContent.addText('.')
        elif (keycode[1] == 'backspace'):
            self.popupContent.textInput.text = self.popupContent.textInput.text[:-1]         
        elif (keycode[1] == 'enter') or (keycode[1] =='numpadenter'):
            self.popupContent.done()
        elif (keycode[1] == 'escape'):     # abort entering a number, keep the old number
            self.popupContent.textInput.text = ''    # clear text so it isn't converted to a number
            self.popupContent.done()
        return True     # always swallow keypresses since this is a modal dialog
        
    def dismiss_popup(self):
        '''
        
        Close The Pop-up
        
        '''
        try:
            tempfloat = float(self.popupContent.textInput.text)
            self.targetWidget.text = str(tempfloat)  # Update displayed text using standard numeric format
        except:
            pass                                                             #If what was entered cannot be converted to a number, leave the value the same
        self._popup.dismiss()

    def gotoLinePopup(self):
        
        self.popupContent = TouchNumberInput(done=self.dismiss_gotoLinePopup)
        self._popup = Popup(title="Go to gcode line", content=self.popupContent,
                            size_hint=(0.9, 0.9))
        self._popup.open()
        if global_variables._keyboard:
            global_variables._keyboard.bind(on_key_down=self.keydown_popup)
            self._popup.bind(on_dismiss=self.ondismiss_popup)

    def dismiss_gotoLinePopup(self):
        '''
        
        Close The Pop-up
        
        '''
        try:
            line = int(float(self.popupContent.textInput.text))
            if line < 0:
                self.data.gcodeIndex = 0
            elif line > len(self.data.gcode):
                self.data.gcodeIndex = len(self.data.gcode)
            else:
                self.data.gcodeIndex = line
           
        except:
            pass                                                             #If what was entered cannot be converted to a number, leave the value the same
        self._popup.dismiss()
    
    def macro(self,index):
        '''
        Execute user defined macro
        '''
        self.data.gcode_queue.put(self.data.config.get('Maslow Settings', 'macro' + str(index))) 

