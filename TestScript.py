#Author-Tim Booher
#Description-My test script to draw an pocket hole

import adsk.core, traceback

def find_xy(length, width, height):
    myList = sorted([length, width, height])
    x = myList[2]
    y = myList[1]
    return x,y

def make_hole(sketch, num, extrudes, TargetBody, root, offset, myPlane, myDist):
        distance = adsk.core.ValueInput.createByReal(myDist)
        prof = sketch.profiles.item(num) # findProfile(sk, cir2, rect2)
        
        extrudeInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        extent_distance = adsk.fusion.DistanceExtentDefinition.create(distance)
        offset_distance = adsk.core.ValueInput.createByReal(offset)
        start_from = adsk.fusion.FromEntityStartDefinition.create(myPlane, offset_distance)
        extrudeInput.setOneSideExtent(extent_distance, adsk.fusion.ExtentDirections.NegativeExtentDirection)
        extrudeInput.startExtent = start_from
        extrude2 = extrudes.add(extrudeInput)

        # extrude2 = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ToolBody = extrude2.bodies.item(0)
        ToolBody.name = 'pocket hole ' + str(num)

        ToolBodies = adsk.core.ObjectCollection.create()
        ToolBodies.add(ToolBody)
        # CombineCutInput = root.features.combineFeatures.createInput(TargetBody, ToolBody )
         
        CombineCutFeats = root.features.combineFeatures
        CombineCutInput = CombineCutFeats.createInput(TargetBody, ToolBodies)
        CombineCutInput.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
        CombineCutFeats.add(CombineCutInput)

def draw_holes(root, sk, face, myPlane, x, y, ph_radius, daStart, daStop):
    c1 = sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(3*x/8,-y/2,0),ph_radius)
    c2 = sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(-3*x/8,-y/2,0),ph_radius)
    # time to do the extraction
    extrudes = root.features.extrudeFeatures
    make_hole(sk, 0, extrudes, face.body, root, daStart, myPlane, daStop)
    make_hole(sk, 1, extrudes, face.body, root, daStart, myPlane, daStop)
    # now clean up so we can reference items 1 and 0 in the sketch!
    c1.deleteMe()
    c2.deleteMe()

def run(context):
    ui = None
    try:
        #################################################################
        # critical parameter
        #################################################################
        offset = 0.12 # in cm
        #################################################################
        app = adsk.core.Application.get()
        design = app.activeProduct
        ui  = app.userInterface
        root = adsk.fusion.Component.cast(design.rootComponent)
        ui.messageBox('Select a face and an edge')
        edge = ui.selectEntity('Select the edge to create a sketch', 'Edges').entity
        face = ui.selectEntity('Select the correct face', 'PlanarFaces').entity
       
        constructionPlaneInput = root.constructionPlanes.createInput()
        ang = adsk.core.ValueInput.createByReal(-75.0)
        constructionPlaneInput.setByAngle( edge, ang, face )
        myPlane = root.constructionPlanes.add( constructionPlaneInput )
        myPlane.name = 'Pocket Construction Plane'

        # make sure we can see text output
        textPalette = ui.palettes.itemById('TextCommands')
        if not textPalette.isVisible: textPalette.isVisible = True
        textPalette.writeText("offset parameter: " + str(offset))
        
        # comp = design.activeComponent
        box = face.boundingBox
        length = box.maxPoint.x - box.minPoint.x # 1.9
        width = box.maxPoint.y - box.minPoint.y # 0
        height = box.maxPoint.z - box.minPoint.z # 16
        # ui.messageBox('the length is ' + str(edge.length))
        # ui.messageBox('the bb is ' + str(length) + ' long and ' + str(width) + ' wide and ' + str(height) + ' tall')

        # need to get the orientation. the longest parameter is the x, shortest y
        x,y = find_xy(length, width, height)

        # now we want to draw two circles
        sk = root.sketches.add(myPlane)
        sk.name = 'pocket sketch'
        draw_holes(root, sk, face, myPlane, x, y, 0.4/2, -offset, 1.2) # 1.2 since the 'tip' is 12 mm long
        draw_holes(root, sk, face, myPlane, x, y, 0.95/2, -1*(offset + 1.2), 5) # 5 is just a big number
        
        
        # now cut the bodies
        
        textPalette.writeText('howdy')


    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
