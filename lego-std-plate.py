#Author-huanghua
#Description-
import adsk.core, adsk.fusion, adsk.cam, traceback
from .packages import BB_UI as UI

app = adsk.core.Application.get()
ui  = app.userInterface

def run(context): 
    try:
        UI.run(context)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        UI.stop(context)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))