#
# Milestone3.py - This is the Python code template used to 
# setup the structure for Milestone 3. In this milestone, you need
# to demonstrate the capability to productively display a message
# in Morse code utilizing the Red and Blue LEDs. The message should
# change between SOS and OK when the button is pressed using a state
# machine.
#
# This code works with the test circuit that was built for module 5.
#
# ------------------------------------------------------------------
# Change History
# ------------------------------------------------------------------
# Version   |   Description
# ------------------------------------------------------------------
#    1          Initial Development
# ------------------------------------------------------------------

##
## Imports required to handle our Button, and our LED devices
##
from gpiozero import Button, LED

##
## Imports required to allow us to build a fully functional state machine
##
from statemachine import StateMachine, State

##
## Import required to allow us to pause for a specified length of time
##
from time import sleep

##
## These are the packages that we need to pull in so that we can work
## with the GPIO interface on the Raspberry Pi board and work with
## the 16x2 LCD display
##
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

from threading import Thread

##
## DEBUG flag - boolean value to indicate whether or not to print 
## status messages on the console of the program
## 
DEBUG = True


##
## ManagedDisplay - Class intended to manage the 16x2 
## Display
##
class ManagedDisplay():
    ##
    ## Class Initialization method to setup the display
    ##
    def __init__(self):
        ##
        ## Setup the six GPIO lines to communicate with the display.
        ## This leverages the digitalio class to handle digital 
        ## outputs on the GPIO lines. There is also an analogous
        ## class for analog IO.
        ##
        ## You need to make sure that the port mappings match the
        ## physical wiring of the display interface to the
        ## GPIO interface.
        ##
        ## compatible with all versions of RPI as of Jan. 2019
        ##
        self.lcd_rs = digitalio.DigitalInOut(board.D17)
        self.lcd_en = digitalio.DigitalInOut(board.D27)
        self.lcd_d4 = digitalio.DigitalInOut(board.D5)
        self.lcd_d5 = digitalio.DigitalInOut(board.D6)
        self.lcd_d6 = digitalio.DigitalInOut(board.D13)
        self.lcd_d7 = digitalio.DigitalInOut(board.D26)

        # Modify this if you have a different sized character LCD
        self.lcd_columns = 16
        self.lcd_rows = 2

        # Initialise the lcd class
        self.lcd = characterlcd.Character_LCD_Mono(
            self.lcd_rs, self.lcd_en,
            self.lcd_d4, self.lcd_d5,
            self.lcd_d6, self.lcd_d7,
            self.lcd_columns, self.lcd_rows
        )

        # wipe LCD screen before we start
        self.lcd.clear()

    ##
    ## cleanupDisplay - Method used to cleanup the digitalIO lines that
    ## are used to run the display.
    ##
    def cleanupDisplay(self):
        # Clear the LCD first - otherwise we won't be able to update it.
        self.lcd.clear()
        self.lcd_rs.deinit()
        self.lcd_en.deinit()
        self.lcd_d4.deinit()
        self.lcd_d5.deinit()
        self.lcd_d6.deinit()
        self.lcd_d7.deinit()

    ##
    ## clear - Convenience method used to clear the display
    ##
    def clear(self):
        self.lcd.clear()

    ##
    ## updateScreen - Convenience method used to update the message.
    ##
    def updateScreen(self, message):
        self.lcd.clear()
        self.lcd.message = message

    ## End class ManagedDisplay definition


##
## CWMachine - This is our StateMachine implementation class.
## The purpose of this state machine is to send a message in
## morse code, blinking the red light for a dot, and the blue light
## for a dash.
##
## A dot should be displayed for 500ms.
## A dash should be displayed for 1500ms.
## There should be a pause of 250ms between dots/dashes.
## There should be a pause of 750ms between letters.
## There should be a pause of 3000ms between words.
##
class CWMachine(StateMachine):
    "A state machine designed to display Morse code messages"

    ##
    ## State definitions
    ##
    off = State(initial=True)
    dot = State()
    dash = State()
    dotDashPause = State()
    letterPause = State()
    wordPause = State()

    ##
    ## Event definitions
    ##
    doDot = off.to(dot) | dot.to(off)
    doDash = off.to(dash) | dash.to(off)
    doDDP = off.to(dotDashPause) | dotDashPause.to(off) | dot.to(dotDashPause) | dash.to(dotDashPause)
    doLP = off.to(letterPause) | letterPause.to(off)
    doWP = off.to(wordPause) | wordPause.to(off)

    ##
    ## Hardware components
    ##
    redLight = LED(18)
    blueLight = LED(23)
    screen = ManagedDisplay()
    message1 = 'SOS'
    message2 = 'OK'
    activeMessage = message1
    endTransmission = False

    ##
    ## Morse dictionary
    ##
    morseDict = {
        'S': '...',
        'O': '---',
        'K': '-.-'
    }

    ##
    ## on_enter handlers
    ##
    def on_enter_dot(self):
        # Red LED ON for 500ms, then OFF
        self.redLight.on()
        sleep(0.5)
        self.redLight.off()
        if DEBUG: print("* dot (500ms)")
        # auto‐exit dot → off
        self.doDot()

    def on_enter_dash(self):
        # Blue LED ON for 1500ms, then OFF
        self.blueLight.on()
        sleep(1.5)
        self.blueLight.off()
        if DEBUG: print("* dash (1500ms)")
        # auto‐exit dash → off
        self.doDash()

    def on_enter_dotDashPause(self):
        # Pause between symbols: 250ms
        sleep(0.25)
        if DEBUG: print("* pause symbol (250ms)")
        # auto‐exit pause → off
        self.doDDP()

    def on_enter_letterPause(self):
        # Pause between letters: 750ms
        sleep(0.75)
        if DEBUG: print("* pause letter (750ms)")
        # auto‐exit pause → off
        self.doLP()

    def on_enter_wordPause(self):
        # Pause between words: 3000ms
        sleep(3.0)
        if DEBUG: print("* pause word (3000ms)")
        # auto‐exit pause → off
        self.doWP()

    ##
    ## toggleMessage - switch activeMessage between SOS and OK
    ##
    def toggleMessage(self):
        self.activeMessage = (
            self.message2
            if self.activeMessage == self.message1
            else self.message1
        )
        if DEBUG: print(f"* Toggled message to: {self.activeMessage}")

    ##
    ## processButton - invoked on button press
    ##
    def processButton(self):
        self.toggleMessage()

    ##
    ## run - starts the transmit thread
    ##
    def run(self):
        Thread(target=self.transmit, daemon=True).start()

    ##
    ## transmit - main loop to send Morse code indefinitely
    ##
    def transmit(self):
        while not self.endTransmission:
            # update display with current message
            self.screen.updateScreen(f"Sending:\n{self.activeMessage}")

            for word in self.activeMessage.split():
                for char in word:
                    code = self.morseDict.get(char, '')
                    for i, sym in enumerate(code):
                        if sym == '.':
                            self.doDot()
                        else:
                            self.doDash()
                        # symbol pause if more symbols remain
                        if i < len(code) - 1:
                            self.doDDP()
                    # letter pause
                    self.doLP()
                # word pause
                self.doWP()

        # cleanup when done
        self.screen.cleanupDisplay()


##
## Main execution
##
if __name__ == '__main__':
    cwMachine = CWMachine()
    # set up button on GPIO24 to toggle message
    greenButton = Button(24)
    greenButton.when_pressed = cwMachine.processButton

    cwMachine.run()

    try:
        # keep main thread alive
        while True:
            if DEBUG: print("Killing time in a loop...")
            sleep(20)
    except KeyboardInterrupt:
        print("Cleaning up. Exiting...")
        cwMachine.endTransmission = True
        sleep(1)
