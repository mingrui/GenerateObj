import os
import shlex
from __main__ import vtk, qt, ctk, slicer
import SampleData
from ROBEXBrainExtraction import ROBEXBrainExtractionLogic

class GenerateObj:
    def __init__(self, parent):
        parent.title = "Generate Obj Model"
        parent.categories = ["Surface Models"]
        parent.dependencies = []
        parent.contributors = ["Mingrui Jiang"]
        parent.helpText = """
        Run this script to generate .obj file models for specific nifti files inside a folder structure

        Make sure you install the ROBEX brain extraction module first
        """
        parent.acknowledgementText = """
        Thanks to youtube and the opensource community for teaching me the way of 3D Slicer scripting.
        """
        self.parent = parent

class GenerateObjWidget:
    def __init__(self, parent=None):
        if not parent:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlScene)
        else:
            self.parent = parent
        self.layout = self.parent.layout()
        if not parent:
            self.setup()
            self.parent.show()

    def setup(self):
        collapsibleButton = ctk.ctkCollapsibleButton()
        collapsibleButton.text = "Robex Brain Extraction"
        self.layout.addWidget(collapsibleButton)
        self.formLayout = qt.QFormLayout(collapsibleButton)
        self.formFrame = qt.QFrame(collapsibleButton)
        self.formFrame.setLayout(qt.QHBoxLayout())
        self.formLayout.addWidget(self.formFrame)

        # folder text field
        # will search under this folder and 1 level below this folder
        self.textfield = qt.QTextEdit()
        self.formLayout.addRow("folder", self.textfield)

        # input file name text field
        # will search for files matching this name
        self.brainfileTextfield = qt.QTextEdit()
        self.formLayout.addRow("input files", self.brainfileTextfield)

        button = qt.QPushButton("Generate brain.obj and brainmask.nii")
        button.connect("clicked(bool)", self.robexBrainExtractionButtonClicked)
        self.formLayout.addRow(button)

        # output file name
        # input file names and output file names will match line by line
        self.brainOutputTextfield = qt.QTextEdit()
        self.formLayout.addRow("output files", self.brainOutputTextfield)

        collapsibleButtonB = ctk.ctkCollapsibleButton()
        collapsibleButtonB.text = "Tumor Segmentation"
        self.layout.addWidget(collapsibleButtonB)
        self.formLayoutB = qt.QFormLayout(collapsibleButtonB)
        self.formFrameB = qt.QFrame(collapsibleButtonB)
        self.formFrameB.setLayout(qt.QHBoxLayout())
        self.formLayoutB.addWidget(self.formFrameB)

        self.textfieldB = qt.QTextEdit()
        self.formLayoutB.addRow("folder", self.textfieldB)

        self.segmentationfileTextfield = qt.QTextEdit()
        self.formLayoutB.addRow("input files", self.segmentationfileTextfield)

        buttonB = qt.QPushButton("Generate segmentation.obj")
        buttonB.connect("clicked(bool)", self.informationButtonClicked)
        self.formLayoutB.addRow(buttonB)

        self.segmentationOutputTextfield = qt.QTextEdit()
        self.formLayoutB.addRow("output files", self.segmentationOutputTextfield)

    def robexBrainExtractionButtonClicked(self):
        print "robex button clicked"
        text = self.textfield.toPlainText()
        folders = shlex.split(text)
        print folders
        fileName = self.brainfileTextfield.toPlainText()
        filenames = shlex.split(fileName)
        print filenames
        outputName = self.brainOutputTextfield.toPlainText()
        outputnames = shlex.split(outputName)
        print outputnames

        for folder in folders:
            subdirs = [x[0] for x in os.walk(folder)]
            for subdir in subdirs:
                for filename, outputname in zip(filenames, outputnames):
                    filepath = os.path.join(subdir, filename)
                    if not os.path.isfile(filepath):
                        continue
                    [success, loadedVolumeNode] = slicer.util.loadVolume(filepath, returnNode=True)
                    robexLogic = ROBEXBrainExtractionLogic()
                    outputNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode')
                    brainNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLScalarVolumeNode')
                    robexLogic.run(loadedVolumeNode, brainNode, outputNode)
                    #slicer.util.saveNode(brainNode, os.path.join(subdir, outputname+'.nii'))
                    slicer.util.saveNode(outputNode, os.path.join(subdir, outputname+'mask.nii'))

                    self.CreateSegmentation(outputNode, os.path.join(subdir, outputname+'.obj'))
        print "finish"

    def informationButtonClicked(self):
        print "segmentation button clicked"
        text = self.textfieldB.toPlainText()
        folders = shlex.split(text)
        print folders
        fileName = self.segmentationfileTextfield.toPlainText()
        filenames = shlex.split(fileName)
        print filenames
        outputName = self.segmentationOutputTextfield.toPlainText()
        outputnames = shlex.split(outputName)
        print outputnames

        for folder in folders:
            subdirs = [x[0] for x in os.walk(folder)]
            for subdir in subdirs:
                print(subdir)
                for filename, outputname in zip(filenames, outputnames):
                    filepath = os.path.join(subdir, filename)
                    if not os.path.isfile(filepath):
                        continue
                    [success, loadedVolumeNode] = slicer.util.loadVolume(filepath, returnNode=True)
                    sampleDataLogic = SampleData.SampleDataLogic()
                    masterVolumeNode = loadedVolumeNode
                    self.CreateSegmentation(masterVolumeNode, os.path.join(subdir, outputname))
        print 'finish'

    def CreateSegmentation(self, masterVolumeNode, outputObj):
        # Create segmentation
        segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
        segmentationNode.CreateDefaultDisplayNodes() # only needed for display
        segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(masterVolumeNode)
        addedSegmentID = segmentationNode.GetSegmentation().AddEmptySegment("segmentation")

        # Create segment editor to get access to effects
        segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
        segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
        segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
        segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
        segmentEditorWidget.setSegmentationNode(segmentationNode)
        segmentEditorWidget.setMasterVolumeNode(masterVolumeNode)

        # Thresholding
        segmentEditorWidget.setActiveEffectByName("Threshold")
        effect = segmentEditorWidget.activeEffect()
        effect.setParameter("MinimumThreshold","1")
        effect.setParameter("MaximumThreshold","999")
        effect.self().onApply()

        # Clean up
        segmentEditorWidget = None
        slicer.mrmlScene.RemoveNode(segmentEditorNode)

        # Make segmentation results visible in 3D
        segmentationNode.CreateClosedSurfaceRepresentation()

        # Make sure surface mesh cells are consistently oriented
        surfaceMesh = segmentationNode.GetClosedSurfaceRepresentation(addedSegmentID)
        normals = vtk.vtkPolyDataNormals()
        normals.AutoOrientNormalsOn()
        normals.ConsistencyOn()
        normals.SetInputData(surfaceMesh)
        normals.Update()
        surfaceMesh = normals.GetOutput()

        # Write to OBJ file
        writer = vtk.vtkOBJWriter()
        writer.SetInputData(surfaceMesh)
        writer.SetFileName(outputObj)
        writer.Update()
