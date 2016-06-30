import adsk.core, adsk.fusion, adsk.cam, traceback
from . import BuildingBlock as BB
from . import config as conf

# global set of event handlers to keep them referenced for the duration of the command
handlers = []
app = adsk.core.Application.get()
ui  = app.userInterface
commandId = 'BuildingBricksCmd'
workspaceToUse = 'FusionSolidEnvironment'
panelToUse = 'SolidCreatePanel'

# Some utility functions
def commandDefinitionById(id):

    if not id:
        ui.messageBox('commandDefinition id is not specified')
        return None
    commandDefinitions_ = ui.commandDefinitions
    commandDefinition_ = commandDefinitions_.itemById(id)
    return commandDefinition_

def getPanelById(panelId):
    workspaces_ = ui.workspaces
    modelingWorkspace_ = workspaces_.itemById(workspaceToUse)
    toolbarPanels_ = modelingWorkspace_.toolbarPanels
    toolbarPanel_ = toolbarPanels_.itemById(panelId) 
    return toolbarPanel_
    
def addCommandToPanel(commandId, commandName, commandDescription, commandResources, onCommandCreated):   
    commandDefinitions_ = ui.commandDefinitions
    
    toolbarControlsPanel_ = getPanelById(panelToUse).controls
    toolbarControlPanel_ = toolbarControlsPanel_.itemById(commandId)
    if not toolbarControlPanel_:
        commandDefinitionPanel_ = commandDefinitions_.itemById(commandId)
        if not commandDefinitionPanel_:
            commandDefinitionPanel_ = commandDefinitions_.addButtonDefinition(commandId, commandName, commandDescription, commandResources)
        
        commandDefinitionPanel_.commandCreated.add(onCommandCreated)
    
        adsk.core.NamedValues.create()
    
        # Keep the handler referenced beyond this function
        handlers.append(onCommandCreated)
        toolbarControlPanel_ = toolbarControlsPanel_.addCommand(commandDefinitionPanel_, '')
        toolbarControlPanel_.isVisible = True 

class BuildingBlockCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            command = args.firingEvent.sender
            inputs = command.commandInputs
            plate = BB.BuildingBlock()
            for input in inputs:
                if input.id == 'wCount':
                    plate.wCount = int(input.value)
                elif  input.id == 'lCount':
                    plate.lCount = int(input.value)
                elif  input.id == 'hCount':
                    plate.hCount = int(input.value)
                elif input.id == 'isFlat':
                    plate.isFlat = input.value
                elif input.id == 'heightUnit':
                    plate.heightUnit = input.value
                elif input.id == 'lengthUnit':
                    plate.lengthUnit = input.value
                elif input.id == 'plateThickness':
                    plate.plateThickness = input.value

            plate.build(True);
            args.isValidResult = True
            
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                
class BuildingBlockCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
    
class BuildingBlockCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):    
    def __init__(self):
        super().__init__()        
    def notify(self, args):
        try:
            cmd = args.command
            onExecute = BuildingBlockCommandExecuteHandler()
            cmd.execute.add(onExecute)
            onExecutePreview = BuildingBlockCommandExecuteHandler()
            cmd.executePreview.add(onExecutePreview)
            # keep the handler referenced beyond this function
            handlers.append(onExecute)
            handlers.append(onExecutePreview)

            #define the inputs
            inputs = cmd.commandInputs
            inputs.addIntegerSpinnerCommandInput('lCount', 'Length Count', 1, 1000, 1, conf.defaultLCount)
            inputs.addIntegerSpinnerCommandInput('wCount', 'Width Count', 1, 1000, 1, conf.defaultWCount)
            inputs.addIntegerSpinnerCommandInput('hCount', 'Height Count', 1, 1000, 1, conf.defaultHCount)
            inputs.addBoolValueInput('isFlat', 'Flat', True, '', conf.defaultIsFlat)
            
            initHeightUnit = adsk.core.ValueInput.createByReal(conf.defaultHeightUnit)
            inputs.addValueInput('heightUnit', 'Height Unit', 'mm', initHeightUnit)

            initLengthUnit = adsk.core.ValueInput.createByReal(conf.defaultLengthUnit)
            inputs.addValueInput('lengthUnit', 'Length Unit', 'mm', initLengthUnit)

            initThickness = adsk.core.ValueInput.createByReal(conf.defaultPlateThickness)
            inputs.addValueInput('plateThickness', 'Thickness', 'mm', initThickness)
            
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def destroyObject(uiObj, objToDelete):
    if uiObj and objToDelete:
        if objToDelete.isValid:
            objToDelete.deleteMe()
        else:
            uiObj.messageBox('objToDelete is not a valid object') 

def commandControlByIdForPanel(id):
    global workspaceToUse
    global panelToUse
    if not id:
        ui.messageBox('commandControl id is not specified')
        return None
    workspaces_ = ui.workspaces
    modelingWorkspace_ = workspaces_.itemById(workspaceToUse)
    toolbarPanels_ = modelingWorkspace_.toolbarPanels
    toolbarPanel_ = toolbarPanels_.itemById(panelToUse)
    toolbarControls_ = toolbarPanel_.controls
    toolbarControl_ = toolbarControls_.itemById(id)
    return toolbarControl_
    
def run(context):

    # command properties
    commandName = 'Building Block'
    commandDescription = 'Create LEGO style building blocks'
    commandResources = './resources'

    # add the new command under "SolidCreate" panel
    addCommandToPanel(commandId, commandName, commandDescription, commandResources, BuildingBlockCommandCreatedHandler())
    # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
    adsk.autoTerminate(False)
    
def stop(context):
    objArray = []
    commandControl_ = commandControlByIdForPanel(commandId)
    if commandControl_:
        objArray.append(commandControl_)

    commandDefinition_ = commandDefinitionById(commandId)
    if commandDefinition_:
        objArray.append(commandDefinition_)

    for obj in objArray:
        destroyObject(ui, obj)
