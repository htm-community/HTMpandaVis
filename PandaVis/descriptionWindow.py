import PySimpleGUI as sg

class cDescriptionWindow:
    def __init__(self, winPos):

        txt=[""]

        layout = [[sg.Multiline(default_text=txt, size=(35, 20), key="multiline")]]

        self.window = sg.Window('Description', keep_on_top=True, location=winPos).Layout(layout)

    def updateText(self, txt):
        self.txt = txt
        self.window["multiline"].update(txt)