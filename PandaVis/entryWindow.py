import PySimpleGUI as sg
import json
import os

class cEntryWindow:
    def __init__(self):
        sg.ChangeLookAndFeel('NeutralBlue')#NeutralBlue
        
        self.command = "None"

        try:
            with open('guiValues.ini', 'r') as file:
                self.defaults = json.loads(file.read())
        except:
            # guiValues doesn't exist, probably is this the first time run
            with open('guiDefaults.ini', 'r') as file:
                self.defaults = json.loads(file.read())
                
        self.databaseFilePath = self.getDefault("databaseFileLocation")
        logoPath = os.path.join('..','images','HTMpandaVis.png')
        
        imageColumn = [[sg.Image(filename=logoPath)]]

        # find all txt files in layouts folder
        dashLayouts = () # tuple
        for file in os.listdir(os.path.join(os.getcwd(),"dashVis","layouts")):
            if file.endswith(".txt"):
                dashLayouts += (file.replace('.txt',''),)

        defaultDashLayout = self.getDefault("defaultDashLayout")
         
        layout = [[sg.Column(imageColumn, justification='center')],
                  [sg.Text('Database file location:'), sg.Text(size=(15,1))],
                  [sg.In(default_text=self.databaseFilePath,key='-databaseFilePath-') ,sg.FileBrowse(file_types=(("SQLite3 database", "*.db"),))],
                  [sg.Button('Run pandaVis 3D explorer',size=(25,5),key='-run3Dexplorer-')],
                  [sg.Button('Run dash visualisation in web browser',size=(25,5),key='-runDash-'), sg.InputCombo(dashLayouts, default_value=defaultDashLayout, size=(20, 1),key='-dashLayout-')],
                  [sg.Button('Exit')]
                  ]

        self.window = sg.Window('HTMpandaVis', keep_on_top=True).Layout(layout)

        self.dashLayout = None


    def Show(self):
        while True:  # Event Loop
            event, values = self.window.read()
            
            if event == sg.WIN_CLOSED or event == 'Exit':
                self.command = "terminate"
            else:
                self.databaseFilePath = values['-databaseFilePath-']
                self.defaults["defaultDashLayout"] = values['-dashLayout-']
                self.dashLayout = values['-dashLayout-']
                self.command = event

            break

        self.Close()

    def getDefault(self, key):
        try:
            return self.defaults[key]
        except KeyError as e:
            print("Can't load default value:" + str(e))
            return False

    def Close(self):

        # retrieve defaults
        self.defaults["databaseFileLocation"] = self.databaseFilePath
        self.SaveDefaults()

        self.window.close()

    def SaveDefaults(self):

        try:
            with open('guiValues.ini', 'w') as file:
                file.write(json.dumps(self.defaults))
        except:
            self.defaults = {}
            print("Wasn't able to save defaults into file guiValues.ini !!")

