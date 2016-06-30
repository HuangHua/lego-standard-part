#Author-huanghua
#Description-

import adsk.core, adsk.fusion
from . import config as conf

class BuildingBlock:
    def __init__(self):
        # add user parameters
        self._addUserParams()
        self._isFlat = conf.defaultIsFlat
        self._workingComp = None

    #properties
    @property
    def workingComponent(self):
        return self._workingComp
    @workingComponent.setter
    def workingComponent(self, value):
        self._workingComp = value
        
    @property
    def wCount(self):
        return self._pwc.value
    @wCount.setter
    def wCount(self, value):
        self._pwc.value = value
    
    @property
    def hCount(self):
        return self._phc.value
    @hCount.setter
    def hCount(self, value):
        self._phc.value = value
        
    @property
    def lCount(self):
        return self._plc.value
    @lCount.setter
    def lCount(self, value):
        self._plc.value = value

    @property
    def isFlat(self):
        return self._isFlat
    @isFlat.setter
    def isFlat(self, value):
        self._isFlat = value
        
    @property
    def heightUnit(self):
        return self._phu.value
    @heightUnit.setter
    def heightUnit(self, value):
        self._phu.value = value    
    
    @property
    def lengthUnit(self):
        return self._plu.value
    @lengthUnit.setter
    def lengthUnit(self, value):
        self._plu.value = value    
            
    @property
    def plateThickness(self):
        return self._ptk.value
    @plateThickness.setter
    def plateThickness(self, value):
        self._ptk.value = value  
        
    def _rootComponent(self):
        app = adsk.core.Application.get()
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        return design.rootComponent
        
    @classmethod
    def _userParams(cls):
        app = adsk.core.Application.get()
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        return design.userParameters
        
    @classmethod
    def _unitMgr(cls):
        app = adsk.core.Application.get()
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        return design.unitsManager
    
    def _createNewComponent(self):
        allOccs = self._rootComponent().occurrences
        newOcc = allOccs.addNewComponent(adsk.core.Matrix3D.create())
        return newOcc.component
        
    def _makeRectPattern(self, feat, dist1, dist2, count1, count2, dirEnt1, dirEnt2):
        c1 = self._unitMgr().evaluateExpression(count1, '')
        c2 = self._unitMgr().evaluateExpression(count2, '')
        if c1 <= 0 and c2 <= 0:
            return
        entities = adsk.core.ObjectCollection.create()
        entities.add(feat)
        inputDist1 = adsk.core.ValueInput.createByString(dist1)
        inputDist2 = adsk.core.ValueInput.createByString(dist2)
        countInput1 = adsk.core.ValueInput.createByString(count1)
        countInput2 = adsk.core.ValueInput.createByString(count2)
        patternInput = self.workingComponent.features.rectangularPatternFeatures.createInput(
            entities, dirEnt1, countInput1, inputDist1, adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
        if c2 > 0:
            patternInput.directionTwoEntity = dirEnt2
            patternInput.distanceTwo = inputDist2
            patternInput.quantityTwo = countInput2
        self.workingComponent.features.rectangularPatternFeatures.add(patternInput)
    
    def _makeExtrude(self, profile, booleanType, strHeight):
        if strHeight == '' or profile is None:
            return None
        extrudes = self.workingComponent.features.extrudeFeatures
        extInput = extrudes.createInput(profile, booleanType)
        extDistInput = adsk.core.ValueInput.createByString(strHeight)
        extInput.setDistanceExtent(False, extDistInput)
        return extrudes.add(extInput)
    
    def _makeShell(self, targetFace, insideThickness):
        shellFeats = self.workingComponent.features.shellFeatures
        faceCol = adsk.core.ObjectCollection.create()
        faceCol.add(targetFace)
        shellInput = shellFeats.createInput(faceCol)
        shellInput.insideThickness = adsk.core.ValueInput.createByString(insideThickness)
        shellFeats.add(shellInput)
    
    def _makeFillet(self, edges, radius, tangent):
        edgeCol = adsk.core.ObjectCollection.create()
        for edge in edges:
            edgeCol.add(edge)
        radiusInput = adsk.core.ValueInput.createByReal(radius)
        fillets = self.workingComponent.features.filletFeatures
        filletInput = fillets.createInput()
        filletInput.addConstantRadiusEdgeSet(edgeCol, radiusInput, tangent)
        self.workingComponent.features.filletFeatures.add(filletInput)
    
    def _addCircle(self, sketch, x, y, strX, strY, radius):
        if sketch is None or radius <= 0 or strX == '' or strY == '':
            return

        center = adsk.core.Point3D.create(x, y, 0)
        circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(center, radius)
        
#        app = adsk.core.Application.get()
#        ui  = app.userInterface
#        ui.messageBox(str(x)+'='+strX)
#        ui.messageBox(str(y)+'='+strY)
        
        # add dimension
        sketchDims = sketch.sketchDimensions
#        rDim = sketchDims.addRadialDimension(circle, adsk.core.Point3D.create(x, y+r+0.05, 0))
#        rDim.parameter.expression = strRadius
        
        dim1 = sketchDims.addDistanceDimension(sketch.originPoint, circle.centerSketchPoint, 1, adsk.core.Point3D.create(-0.05, 0, 0))
        dim1.parameter.expression = strX
        dim2 = sketchDims.addDistanceDimension(sketch.originPoint, circle.centerSketchPoint, 2, adsk.core.Point3D.create(0, -0.05, 0))
        dim2.parameter.expression = strY
        
        return circle
        
    def _addRectangle(self, sketch, plc, pwc, plu):
        if sketch is None:
            return
        # create rectangle
        point1 = adsk.core.Point3D.create(0, 0, 0)
        point2 = adsk.core.Point3D.create(plc.value*plu.value, pwc.value*plu.value, 0)
        rectLines = sketch.sketchCurves.sketchLines.addTwoPointRectangle(point1, point2)
        
        # define for short
        ln1, ln2, ln3, ln4 = rectLines[0], rectLines[1], rectLines[2], rectLines[3]
        p1, p2, p3, p4 = ln1.startSketchPoint.geometry, ln1.endSketchPoint.geometry, ln2.endSketchPoint.geometry, ln3.endSketchPoint.geometry
        
        # add constranit
        geomConstraint = sketch.geometricConstraints
        geomConstraint.addCoincident(ln1.startSketchPoint, sketch.originPoint)
        geomConstraint.addHorizontal(ln1)
        geomConstraint.addHorizontal(ln3)
        geomConstraint.addVertical(ln2)
        geomConstraint.addVertical(ln4)
        
        # add dimension
        sketchDims = sketch.sketchDimensions        
        dimOffset = 0.05
        lDim1 = sketchDims.addOffsetDimension(ln1, ln3, adsk.core.Point3D.create((p1.x+p4.x)/2-dimOffset, (p1.y+p4.y)/2, (p1.z+p4.z)/2))
        lDim2 = sketchDims.addOffsetDimension(ln2, ln4, adsk.core.Point3D.create((p1.x+p2.x)/2, (p1.y+p2.y)/2-dimOffset, (p1.z+p2.z)/2))
        lDim1.parameter.expression = self._pwc.name + '*' + self._plu.name
        lDim2.parameter.expression = self._plc.name + '*' + self._plu.name

        return rectLines
    
    def __validateInput(self):
        app = adsk.core.Application.get()
        ui = app.userInterface
        if self.lCount <= 0 or self.wCount <= 0 or self.hCount <= 0:
            ui.messageBox('invalid count parameters')
            return False
        if self.lengthUnit <= 0 or self.heightUnit <= 0 or self.plateThickness <= 0:
            ui.messageBox('invalid length parameters')
            return False
        return True
    
    def __prepareComponent(self, needNewComp):
        app = adsk.core.Application.get()
        if needNewComp:
            self.workingComponent = self._createNewComponent()
        else:
            self.workingComponent = self._rootComponent()
            
        if self.workingComponent is None:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox('New component failed to create', 'New Component Failed')
            return False
        return True
        
    def _addUserParams(self):
        userParams = self._userParams()
        valInput = adsk.core.ValueInput
        self._pwc = userParams.add('WC', valInput.createByReal(conf.defaultWCount), '', 'count in width direction')
        self._plc = userParams.add('LC', valInput.createByReal(conf.defaultLCount), '', 'count in length direction')
        self._phc = userParams.add('HC', valInput.createByReal(conf.defaultHCount), '', 'count in height direction')
        self._phu = userParams.add('HU', valInput.createByReal(conf.defaultHeightUnit), 'cm', 'height')
        self._plu = userParams.add('LU', valInput.createByReal(conf.defaultLengthUnit), 'cm', 'length')
        self._ptk = userParams.add('TIK', valInput.createByReal(conf.defaultPlateThickness), 'cm', 'thickness')
        
    def build(self, needNewComp=True, dataFolder=None):

        if not self.__validateInput():
            return
            
        if not self.__prepareComponent(needNewComp):
            return
            
        # set component name to the style of L*W*H
        compName = str(int(self.lCount)) + 'x' + str(int(self.wCount)) + 'x' + str(int(self.hCount))+ ('_flat' if self.isFlat else '')
        if needNewComp:
            self.workingComponent.name = compName
        
        # Create a new sketch on XY plane
        xyPlane = self.workingComponent.xYConstructionPlane
        sketch = self.workingComponent.sketches.add(xyPlane)

        # Create a rectangle
        length = self.lCount*self.lengthUnit
        strLen = self._plc.name + '*' + self._plu.name
        width = self.wCount*self.lengthUnit
        strWidth = self._pwc.name + '*' + self._plu.name
        rectLines = self._addRectangle(sketch, self._plc, self._pwc, self._plu)
        
        # Create the base plate per input
        strHeight = self._phc.name + '*' + self._phu.name
        baseExt = self._makeExtrude(sketch.profiles[0], adsk.fusion.FeatureOperations.NewBodyFeatureOperation, strHeight)

        # Some important parameter for generating below features
        radius = (self.lengthUnit-2*self.plateThickness)/2.0
        strRadius = '(' + self._plu.name+'-2*'+self._ptk.name+')/2.0'
        offset = self.plateThickness + radius
        strOffset = '('+self._ptk.name + '+' + strRadius+')'
        
        # calc distance
        if self.lCount > 1:
            dist1 = (length - 2*offset)/(self.lCount-1)
            strDist1 = '('+strLen+'-2*'+strOffset+')/('+self._plc.name+'-1)'
        else:
            dist1 = (length - 2*offset)/self.lCount
            strDist1 = '('+strLen+'-2*'+strOffset+')/'+self._plc.name
        if self.wCount > 1:
            dist2 = (width - 2*offset)/(self.wCount-1)
            strDist2 = '('+strWidth+'-2*'+strOffset+')/('+self._pwc.name+'-1)'
        else:
            dist2 = (width - 2*offset)/self.wCount
            strDist2 = '('+strWidth+'-2*'+strOffset+')/'+self._pwc.name

        if not self.isFlat:
            # Create a circle
            self._addCircle(sketch, offset, offset, strOffset, strOffset, radius)  
            # Create the bump extrude
            strHeight = '-' + self._phu.name + '/2.0'
            bumpExt = self._makeExtrude(sketch.profiles[1], adsk.fusion.FeatureOperations.JoinFeatureOperation, strHeight)
            # Pattern bump
            self._makeRectPattern(bumpExt, strDist1, strDist2, self._plc.name, self._pwc.name, rectLines[0], rectLines[3])
        
        # create shell
        tempH = 0
        for face in baseExt.faces:
            if face.centroid.z > tempH:
                tempH = face.centroid.z
                targetFace = face # select the top face of the base extrude feature
        self._makeShell(targetFace, self._ptk.name)
        
        # create another two circles for making next extrude
        cx, cy = strOffset, strOffset
        center = adsk.core.Point3D.create(offset, offset, 0)
        ptTemp = adsk.core.Point3D.create(center.x+(dist1 if self.lCount > 1 else 0), 
                                          center.y+(dist2 if self.wCount > 1 else 0), 0)
        strTempX, strTempY = cx, cy
        if self.lCount > 1: 
            strTempX = cx+'+'+strDist1
        if self.wCount > 1: 
            strTempY = cy+'+'+strDist2

        radius = ptTemp.distanceTo(center)/2.0-radius
        
        x, y = (center.x+ptTemp.x)/2.0, (center.y+ptTemp.y)/2.0
        strX = '('+cx+'+'+strTempX+')/2.0'
        strY = '('+cy+'+'+strTempY+')/2.0'

        #deltaX, deltaY = '('+cx+'-'+strTempX+')', '('+cy+'-'+strTempY+')'
        # there's bug for unit calculation when using functions like sqrt()
        # e.g. aa = 10cm, bb = sqrt(aa*aa) cm cannot be evaluated
        #strRadius = 'sqrt('+deltaX+'*'+deltaX+'+'+deltaY+'*'+deltaY+')/2.0-'+strRadius
        circle2 = self._addCircle(sketch, x, y, strX, strY, radius)
        circle3 = self._addCircle(sketch, x, y, strX, strY, radius-self._ptk.value/2.0)

        if circle2 or circle3:
            # extrude
            strHeight = self._phc.name + '*' + self._phu.name
            ext2 = self._makeExtrude(sketch.profiles[1], adsk.fusion.FeatureOperations.JoinFeatureOperation, strHeight)
            # pattern ext2
            self._makeRectPattern(ext2, strDist1, strDist2, self._plc.name+'-1', self._pwc.name+'-1', rectLines[0], rectLines[3])

        # fillet all edges
        self._makeFillet(self.workingComponent.bRepBodies.item(0).edges, 0.002, True) # 0.002cm
        
        app = adsk.core.Application.get()
        app.activeDocument.name = compName
            
    @staticmethod
    def as_buildingblock(dct, needNewComp = True):
        if 'lCount' in dct and 'wCount' in dct and 'hCount' in dct and 'heightUnit' in dct \
            and 'lengthUnit' in dct and 'plateThickness' in dct and 'isFlat' in dct:
            bb = BuildingBlock()
            bb.lCount = dct['lCount']
            bb.wCount = dct['wCount']
            bb.hCount = dct['hCount']
            bb.heightUnit = dct['heightUnit']
            bb.lengthUnit = dct['lengthUnit']
            bb.plateThickness = dct['plateThickness']
            bb.isFlat = dct['isFlat']
            return bb
        return dct
         
    def toJson(self):
        return {"lCount":self._lCount, "wCount":self._wCount, "hCount":self._hCount, \
                "heightUnit":self._heightUnit, "lengthUnit":self._lengthUnit, \
                "plateThickness":self._plateThickness,"isFlat":self._isFlat}