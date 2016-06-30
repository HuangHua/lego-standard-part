#Author-huanghua
#Description-
import adsk.core, adsk.fusion, adsk.cam, traceback, json
from .packages import BuildingBlock as BB
import os

app = adsk.core.Application.get()
ui  = app.userInterface

def parseJson(filepath):
    jsonFile = open(filepath, "r")
    line = jsonFile.readline()
    content = ''
    while line:
        content += line
        line = jsonFile.readline()  
    jsonFile.close()
    return content
    
def run(context): 
    try:
        
        dataFolder = app.data.dataProjects[3].rootFolder.dataFolders.itemByName("standard_blocks")
        
        print("start batch creation")
        path = os.path.split(os.path.realpath(__file__))[0] + r'\assembly.json'
        content = parseJson(path)
        bbs = json.loads(content)
        for bb in bbs:
            doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType, True)
            doc.activate()
            obj = BB.BuildingBlock.as_buildingblock(bb)
            obj.build(False, dataFolder)
            app.activeDocument.saveAs(app.activeDocument.name, dataFolder, "building block" + app.activeDocument.name, "")
            app.activeDocument.close(True)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        print("batch creation finished")
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))