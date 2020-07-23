from my_randomizer import *
import copy
import math
import shutil
from gatelib import *

# the same folder where this program is stored
if getattr(sys, 'frozen', False):
    mainFolder = path.dirname(sys.executable) # EXE (executable) file
else:
	mainFolder = path.dirname(path.realpath(__file__)) # PY (source) file
sys.path.append(mainFolder)
outputFolder = path.join(mainFolder, "output")

"""
TODO:
- implement log file
- figure out how to do popups (if possible)
- organize GUI
- add credits button
- remove leftover print statements
"""

def main():
	vp_start_gui()

def randomize():
	global sourceRom
	global currSeed
	global seedString

	if not path.isfile(sourceRom.get()):
		return (False, "Invalid ROM input.")

	myRules = copy.copy(required_rules)
	optionalRulesetNum = 0
	for ruleset in optionalRulesetsList:
		if ruleset[1] == 1:
			for rule in optional_rulesets[ruleset[0]]:
				myRules.append(rule)
		optionalRulesetNum += 1

	numOfSeeds = int(numSeeds.get())
	numSeedsGenerated = 0
	for seedNum in range(numOfSeeds):
		if useSeed.get()=="1":
			seedString = seedInput.get()
			try:
				assert len(seedString) == 6
				assert verifySeed(seedString[:-5], [1]*len(optionalRulesetsList), 36)
			except:
				return (False, "Invalid seed.")
			decodedSeedVals = decodeSeed(seedString[:-5], [1]*len(optionalRulesetsList), 36)
			for i in range(len(optionalRulesetsList)):
				optionalRulesetsList[i] = (optionalRulesetsList[i][0], decodedSeedVals[i])
			currSeed = int(seedString, 36)
		else:
			varArray = []
			maxValueArray = []
			for ruleset in optionalRulesetsList:
				varArray.append(ruleset[1])
				maxValueArray.append(1)
			settingsSeed = encodeSeed(varArray, maxValueArray, 36)[0]
			maxVal = int("ZZZZZ", 36)
			genSeed = random.randint(0, maxVal)
			currSeed = (settingsSeed*(maxVal+1)) + genSeed
			seedString = str(dec_to_base(currSeed, 36)).upper().zfill(5+math.ceil(len(optional_rulesets.keys())/5.0))
		random.seed(currSeed)
		# initialize attributes
		for att in attributes:
			attributes[att].prepare()
		if not enforceRuleset(myRules):
			return (False, "No combination of values satisfies the given combination of rules.")

		for att in attributes:
			print(attributes[att].name+": "+str(attributes[att].value))

		generatedRom = generateRom()
		for att in attributes:
			attributes[att].resetToDefault()
		if generatedRom[0]:
			numSeedsGenerated += 1
		else:
			return generatedRom
	return (True, "Successfully generated "+str(numSeedsGenerated)+" seed"+("s." if numSeedsGenerated != 1 else "."))

def enforceRuleset(ruleset):
	ruleNum = 0
	while ruleNum < len(ruleset):
		if not ruleset[ruleNum].rulePasses():
			nextValueSet = False
			for att in attributes:
				if attributes[att].setToNextValue():
					nextValueSet = True
					break
			if not nextValueSet:
				return False
			ruleNum = 0
		else:
			ruleNum += 1
	return True

def generateRom():
	global sourceRom
	global seedString

	newRom = path.join(outputFolder, path.splitext(path.basename(sourceRom.get()))[0]+"-"+seedString+"."+rom_file_format)
	if not path.isdir(outputFolder):
		mkdir(outputFolder)
	shutil.copyfile(sourceRom.get(), newRom)
	try:
		file = open(newRom, "r+b")
		for att in attributes:
			for address in attributes[att].addresses:
				writeToAddress(file, address, attributes[att].value, attributes[att].number_of_bytes)
		file.close()
		print("Succesfully generated ROM with seed "+seedString)
		return (True, "ROM successfully generated.")
	except:
		print("Something went wrong. Deleting generated ROM.")
		file.close()
		remove(newRom)
		return (False, "Failed to generate ROM.")


#######
# GUI #
#######

#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# GUI module initially created by PAGE version 5.4
#  in conjunction with Tcl version 8.6
#    platform: Windows NT

import sys

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk
from tkinter.filedialog import askopenfilename

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root, sizeRatio
    root = tk.Tk()
    # 1.7 seems to be default scaling
    size = root.winfo_screenheight()
    sizeRatio = size/1440
    # root.tk.call('tk', 'scaling', 2.0*sizeRatio)
    set_Tk_var()
    top = TopLevel(root)
    init(root, top)
    root.mainloop()

w = None
def create_TopLevel(rt, *args, **kwargs):
    '''Starting point when module is imported by another module.
       Correct form of call: 'create_TopLevel(root, *args, **kwargs)' .'''
    global w, w_win, root
    #rt = root
    root = rt
    w = tk.Toplevel (root)
    set_Tk_var()
    top = TopLevel (w)
    init(w, top, *args, **kwargs)
    return (w, top)

def destroy_TopLevel():
    global w
    w.destroy()
    w = None

class TopLevel:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'
        self.style = ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use('winnative')
        self.style.configure('.',background=_bgcolor)
        self.style.configure('.',foreground=_fgcolor)
        self.style.configure('.',font="TkDefaultFont")
        self.style.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])

        top.geometry(str(int(1000*sizeRatio))+"x"+str(int(700*sizeRatio)))
        # top.minsize(120, 1)
        # top.maxsize(2564, 1421)
        top.resizable(0, 0)
        top.title(program_name)
        top.configure(background="#d9d9d9")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")

        self.style.map('TCheckbutton',background=
            [('selected', _bgcolor), ('active', _ana2color)])

        # Rom Input Label
        self.Label_RomInput = ttk.Label(top)
        self.Label_RomInput.place(x=35*sizeRatio, y=30*sizeRatio, height=35*sizeRatio, width=18*len(rom_name)*sizeRatio)
        self.Label_RomInput.configure(background="#d9d9d9")
        self.Label_RomInput.configure(foreground="#000000")
        self.Label_RomInput.configure(font="TkDefaultFont")
        self.Label_RomInput.configure(relief="flat")
        self.Label_RomInput.configure(anchor='w')
        self.Label_RomInput.configure(justify='left')
        self.Label_RomInput.configure(text=rom_name+''' ROM''')

        # Rom Input Entry
        self.Entry_RomInput = ttk.Entry(top)
        self.Entry_RomInput.place(x=400*sizeRatio, y=30*sizeRatio, height=35*sizeRatio, width=250*sizeRatio)
        self.Entry_RomInput.configure(state='readonly')
        self.Entry_RomInput.configure(textvariable=sourceRom)
        self.Entry_RomInput.configure(background="#000000")
        self.Entry_RomInput.configure(cursor="ibeam")

        # Rom Input Button
        self.Button_RomInput = ttk.Button(top)
        self.Button_RomInput.place(x=830*sizeRatio, y=27*sizeRatio, height=40*sizeRatio, width=120*sizeRatio)
        self.Button_RomInput.configure(command=setSourceRom)
        self.Button_RomInput.configure(takefocus="")
        self.Button_RomInput.configure(text='''Select ROM''')

        # Use Settings Radio Button
        self.style.map('TRadiobutton',background=
            [('selected', _bgcolor), ('active', _ana2color)])
        self.RadioButton_UseSettings = ttk.Radiobutton(top)
        self.RadioButton_UseSettings.place(x=35*sizeRatio, y=75*sizeRatio, height=35*sizeRatio, width=18*12*sizeRatio)
        self.RadioButton_UseSettings.configure(variable=useSeed)
        self.RadioButton_UseSettings.configure(value="0")
        self.RadioButton_UseSettings.configure(text='''Use Settings''')
        self.RadioButton_UseSettings.configure(compound='none')
        self.tooltip_font = "TkDefaultFont"
        self.RadioButton_UseSettings_tooltip = ToolTip(self.RadioButton_UseSettings, self.tooltip_font, '''Use the settings defined below to create a random seed.''')

        # Use Seed Radio Button
        self.RadioButton_UseSeed = ttk.Radiobutton(top)
        self.RadioButton_UseSeed.place(x=470*sizeRatio, y=75*sizeRatio, height=35*sizeRatio, width=18*8*sizeRatio)
        self.RadioButton_UseSeed.configure(variable=useSeed)
        self.RadioButton_UseSeed.configure(text='''Use Seed''')
        self.tooltip_font = "TkDefaultFont"
        self.RadioButton_UseSeed_tooltip = ToolTip(self.RadioButton_UseSeed, self.tooltip_font, '''Recreate a specific set of changes according to a 10-character seed.''')

        # Seed Input Entry
        self.Entry_SeedInput = ttk.Entry(top)
        self.Entry_SeedInput.place(x=600*sizeRatio, y=75*sizeRatio, height=35*sizeRatio, width=180*sizeRatio)
        self.Entry_SeedInput.configure(state='disabled')
        self.Entry_SeedInput.configure(textvariable=seedInput)
        self.Entry_SeedInput.configure(takefocus="")
        self.Entry_SeedInput.configure(cursor="ibeam")
        self.Entry_SeedInput.bind('<Key>',keepUpperCharsSeed)
        self.Entry_SeedInput.bind('<KeyRelease>',keepUpperCharsSeed)

        # self.menubar = tk.Menu(top,font="TkMenuFont",bg=_bgcolor,fg=_fgcolor)
        # top.configure(menu = self.menubar)

        # Frame
        self.TFrame1 = ttk.Frame(top)
        self.TFrame1.place(x=35*sizeRatio, y=120*sizeRatio, height=400*sizeRatio, width=930*sizeRatio)
        self.TFrame1.configure(relief='groove')
        self.TFrame1.configure(borderwidth="2")
        self.TFrame1.configure(relief="groove")

        # Ruleset Check Buttons
        self.CheckButtons = []
        self.CheckButtons_tooltips = []
        optRulesetNum = 0
        global optRulesetValues
        for key in optional_rulesets:
            self.CheckButtons.append(ttk.Checkbutton(self.TFrame1))
            self.CheckButtons[optRulesetNum].place(x=35*sizeRatio, y=150*sizeRatio+30*optRulesetNum, height=35*sizeRatio, width=18*len(key)*sizeRatio)
            self.CheckButtons[optRulesetNum].configure(variable=optRulesetValues[optRulesetNum])
            self.CheckButtons[optRulesetNum].configure(offvalue="0")
            self.CheckButtons[optRulesetNum].configure(onvalue="1")
            self.CheckButtons[optRulesetNum].configure(takefocus="")
            self.CheckButtons[optRulesetNum].configure(text=key)
            self.tooltip_font = "TkDefaultFont"
            self.CheckButtons_tooltips.append(ToolTip(self.CheckButtons[optRulesetNum], self.tooltip_font, '''PLACEHOLDER DESCRIPTION'''))
            optRulesetNum += 1

        # Number of Seeds Label
        self.Label_NumSeeds = ttk.Label(self.TFrame1)
        self.Label_NumSeeds.place(x=670*sizeRatio, y=222*sizeRatio, height=35*sizeRatio, width=180*sizeRatio)
        self.Label_NumSeeds.configure(background="#d9d9d9")
        self.Label_NumSeeds.configure(foreground="#000000")
        self.Label_NumSeeds.configure(font="TkDefaultFont")
        self.Label_NumSeeds.configure(relief="flat")
        self.Label_NumSeeds.configure(anchor='w')
        self.Label_NumSeeds.configure(justify='left')
        self.Label_NumSeeds.configure(text='''# of Seeds''')
        self.tooltip_font = "TkDefaultFont"
        self.Label_NumSeeds_tooltip = ToolTip(self.Label_NumSeeds, self.tooltip_font, '''How many seeds would you like to generate?''')

        # Number of Seeds Dropdown
        self.ComboBox_NumSeeds = ttk.Combobox(self.TFrame1)
        self.ComboBox_NumSeeds.place(x=670*sizeRatio, y=255*sizeRatio, height=35*sizeRatio, width=90*sizeRatio)
        self.value_list = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20',]
        self.ComboBox_NumSeeds.configure(values=self.value_list)
        self.ComboBox_NumSeeds.configure(state='readonly')
        self.ComboBox_NumSeeds.configure(textvariable=numSeeds)

        # Text Log Check Button
        self.CheckButton_GenerateTextLog = ttk.Checkbutton(top)
        self.CheckButton_GenerateTextLog.place(x=250*sizeRatio, y=600*sizeRatio, height=35*sizeRatio, width=18*17*sizeRatio)
        self.CheckButton_GenerateTextLog.configure(variable=generateAbilityLog)
        self.CheckButton_GenerateTextLog.configure(takefocus="")
        self.CheckButton_GenerateTextLog.configure(text='''Generate Text Log''')
        self.tooltip_font = "TkDefaultFont"
        self.CheckButton_GenerateTextLog_tooltip = ToolTip(self.CheckButton_GenerateTextLog, self.tooltip_font, '''Would you like to generate a text file that details what abilities are tied to each enemy/object in the created seed?''')

        # Create Rom Button
        self.Button_CreateRom = ttk.Button(top)
        self.Button_CreateRom.place(x=550*sizeRatio, y=600*sizeRatio, height=40*sizeRatio, width=144*sizeRatio)
        self.Button_CreateRom.configure(takefocus="")
        self.Button_CreateRom.configure(text='''Randomize!''')

        # Message
        self.Label_Message = ttk.Label(top)
        self.Label_Message.place(x=50*sizeRatio, y=525*sizeRatio, height=30*sizeRatio, width=900*sizeRatio)
        self.Label_Message.configure(background="#d9d9d9")
        self.Label_Message.configure(foreground="#000000")
        self.Label_Message.configure(font="TkDefaultFont")
        self.Label_Message.configure(relief="flat")
        self.Label_Message.configure(anchor='center')
        self.Label_Message.configure(justify='left')
        self.Label_Message.configure(textvariable=message)

        self.RadioButton_UseSettings.configure(command=self.prepareSettingsAndSeed)
        self.RadioButton_UseSeed.configure(command=self.prepareSettingsAndSeed)
        self.Button_CreateRom.configure(command=self.attemptRandomize)

    def prepareSettingsAndSeed(self, unused=None):
        if useSeed.get()=="1":
            self.Entry_SeedInput.configure(state="normal")
            self.Label_NumSeeds.configure(state="disabled")
            self.ComboBox_NumSeeds.configure(state="disabled")
            for button in self.CheckButtons:
                button.configure(state="disabled")
        else:
            self.Entry_SeedInput.configure(state="disabled")
            self.Label_NumSeeds.configure(state="normal")
            self.ComboBox_NumSeeds.configure(state="readonly")
            for button in self.CheckButtons:
                button.configure(state="normal")

    def attemptRandomize(self):
        global optionalRulesetsList
        global optRulesetValues

        optionalRulesetsList = [("", 0)] * len(optRulesetValues)
        keys = list(optional_rulesets.keys())
        for i in range(len(optRulesetValues)):
            optionalRulesetsList[i] = (keys[i], int(optRulesetValues[i].get()))
        results = randomize()
        message.set(results[1])
        self.Label_Message.configure(foreground="#0000FF" if results[0] else "#FF0000")

# ======================================================
# Support code for Balloon Help (also called tooltips).
# Found the original code at:
# http://code.activestate.com/recipes/576688-tooltip-for-tkinter/
# Modified by Rozen to remove Tkinter import statements and to receive
# the font as an argument.
# ======================================================

from time import time, localtime, strftime

class ToolTip(tk.Toplevel):
    """
    Provides a ToolTip widget for Tkinter.
    To apply a ToolTip to any Tkinter widget, simply pass the widget to the
    ToolTip constructor
    """
    def __init__(self, wdgt, tooltip_font, msg=None, msgFunc=None,
                 delay=0.5, follow=True):
        """
        Initialize the ToolTip

        Arguments:
          wdgt: The widget this ToolTip is assigned to
          tooltip_font: Font to be used
          msg:  A static string message assigned to the ToolTip
          msgFunc: A function that retrieves a string to use as the ToolTip text
          delay:   The delay in seconds before the ToolTip appears(may be float)
          follow:  If True, the ToolTip follows motion, otherwise hides
        """
        self.wdgt = wdgt
        # The parent of the ToolTip is the parent of the ToolTips widget
        self.parent = self.wdgt.master
        # Initalise the Toplevel
        tk.Toplevel.__init__(self, self.parent, bg='black', padx=1, pady=1)
        # Hide initially
        self.withdraw()
        # The ToolTip Toplevel should have no frame or title bar
        self.overrideredirect(True)

        # The msgVar will contain the text displayed by the ToolTip
        self.msgVar = tk.StringVar()
        if msg is None:
            self.msgVar.set('No message provided')
        else:
            self.msgVar.set(msg)
        self.msgFunc = msgFunc
        self.delay = delay
        self.follow = follow
        self.visible = 0
        self.lastMotion = 0
        # The text of the ToolTip is displayed in a Message widget
        tk.Message(self, textvariable=self.msgVar, bg='#FFFFDD',
                font=tooltip_font,
                aspect=1000).grid()

        # Add bindings to the widget.  This will NOT override
        # bindings that the widget already has
        self.wdgt.bind('<Enter>', self.spawn, '+')
        self.wdgt.bind('<Leave>', self.hide, '+')
        self.wdgt.bind('<Motion>', self.move, '+')

    def spawn(self, event=None):
        """
        Spawn the ToolTip.  This simply makes the ToolTip eligible for display.
        Usually this is caused by entering the widget

        Arguments:
          event: The event that called this funciton
        """
        self.visible = 1
        # The after function takes a time argument in milliseconds
        self.after(int(self.delay * 1000), self.show)

    def show(self):
        """
        Displays the ToolTip if the time delay has been long enough
        """
        if self.visible == 1 and time() - self.lastMotion > self.delay:
            self.visible = 2
        if self.visible == 2:
            self.deiconify()

    def move(self, event):
        """
        Processes motion within the widget.
        Arguments:
          event: The event that called this function
        """
        self.lastMotion = time()
        # If the follow flag is not set, motion within the
        # widget will make the ToolTip disappear
        #
        if self.follow is False:
            self.withdraw()
            self.visible = 1

        # Offset the ToolTip 10x10 pixes southwest of the pointer
        self.geometry('+%i+%i' % (event.x_root+20, event.y_root-10))
        try:
            # Try to call the message function.  Will not change
            # the message if the message function is None or
            # the message function fails
            self.msgVar.set(self.msgFunc())
        except:
            pass
        self.after(int(self.delay * 1000), self.show)

    def hide(self, event=None):
        """
        Hides the ToolTip.  Usually this is caused by leaving the widget
        Arguments:
          event: The event that called this function
        """
        self.visible = 0
        self.withdraw()

    def update(self, msg):
        """
        Updates the Tooltip with a new message. Added by Rozen
        """
        self.msgVar.set(msg)

# ===========================================================
#                   End of Class ToolTip
# ===========================================================

def set_Tk_var():
    global sourceRom
    sourceRom = tk.StringVar()
    global optRulesetValues
    optRulesetValues = []
    for i in range(len(optional_rulesets.keys())):
        optRulesetValues.append(tk.StringVar())
    global numSeeds
    numSeeds = tk.StringVar()
    global useSeed
    useSeed = tk.StringVar()
    global seedInput
    seedInput = tk.StringVar()
    global generateAbilityLog
    generateAbilityLog = tk.StringVar()
    global message
    message = tk.StringVar()
    message.set('')
    initVars()

def initVars():
    numSeeds.set("1")
    useSeed.set("0")
    generateAbilityLog.set("1")
    for val in optRulesetValues:
        val.set("0")
    message.set("Welcome to the Amazing Mirror Randomizer! Move your mouse over a label to learn more about it.")

def setSourceRom():
    global sourceRom
    sourceRom.set(askopenfilename(filetypes=[("ROM files", "*."+rom_file_format)]))

def keepUpperCharsSeed(unused):
    global seedInput
    seedInput.set(''.join(ch.upper() for ch in seedInput.get() if ch.isalpha() or ch.isdigit()))
    seedInput.set(seedInput.get()[:(5+math.ceil(len(optional_rulesets.keys())/5.0))])

def init(top, gui, *args, **kwargs):
    global w, top_level, root
    w = gui
    top_level = top
    root = top

def destroy_window(endProg=False):
    # Function which closes the window.
    global top_level
    top_level.destroy()
    top_level = None
    if endProg:
        sys.exit()

if __name__ == '__main__':
	main()