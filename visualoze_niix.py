import vtk
import itk

from vtkmodules.vtkCommonCore import vtkCommand

filepath = "./human_body.nii"
colors = vtk.vtkNamedColors()

ITK = True
VTK = True

class IPWCallback:
    def __init__(self, plane):
        self.plane = plane

    def __call__(self, caller, ev):
        rep = caller.GetRepresentation()
        rep.GetPlane(self.plane)

# Read File
if VTK:
    if ".nii" in filepath:
        reader = vtk.vtkNIFTIImageReader()
        reader.SetFileName(filepath)
        reader.Update()
        # vtk_image = reader.GetOutput()
        # vtk_image
        
        # print(f"File: {('OK' if vtk_image is not None else 'NOT OK')}")
if ITK:
    if ".nii" in filepath:
        itk_image = itk.imread(filepath)
        print(f"File: {('OK' if itk_image is not None else 'NOT OK')}")

        # Applying filter
        itk_median_image = itk.median_image_filter(itk_image, radius=2)

        vtk_image = itk.vtk_image_from_image(itk_median_image)
        vtk_image.ComputeBounds()
        print(f"Filter: {('OK' if vtk_image is not None else 'NOT OK')}")
    
# VTK Image Data to VTK Poly Data
marching_cubes = vtk.vtkMarchingCubes()
marching_cubes.SetInputData(vtk_image)
marching_cubes.SetValue(0, 100)
marching_cubes.Update()
print(f"VTK Poly Data: {('OK' if marching_cubes.GetOutput() is not None else 'NOT OK')}")

# Applying VTK cotour filter
confilter = vtk.vtkPolyDataConnectivityFilter()
confilter.SetInputData(marching_cubes.GetOutput())
confilter.SetExtractionModeToLargestRegion()
confilter.Update()
print(f"VTK filter: {('OK' if confilter.GetOutput() is not None else 'NOT OK')}")

# clipper
plane = vtk.vtkPlane()
clipper = vtk.vtkClipPolyData()
clipper.SetClipFunction(plane)
clipper.SetInputConnection(confilter.GetOutputPort())

# Visualization pipeline
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(clipper.GetOutputPort())
actor = vtk.vtkActor()
actor.SetMapper(mapper)

renderer = vtk.vtkRenderer()
ren_win = vtk.vtkRenderWindow()
ren_win.AddRenderer(renderer)

renderer.AddActor(actor)
renderer.SetBackground(colors.GetColor3d('SlateGray'))

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(ren_win)


rep = vtk.vtkImplicitPlaneRepresentation()
rep.SetPlaceFactor(1.25)
rep.PlaceWidget(actor.GetBounds()) # reader.GetOutput().
rep.SetNormal(plane.GetNormal())


ipw_callback = IPWCallback(plane)
plane_widget = vtk.vtkImplicitPlaneWidget2()
plane_widget.SetInteractor(iren)
plane_widget.SetRepresentation(rep)
plane_widget.AddObserver(vtkCommand.InteractionEvent, ipw_callback)
plane_widget.On()

renderer.GetActiveCamera().Azimuth(-60)
renderer.GetActiveCamera().Elevation(30)
renderer.GetActiveCamera().Zoom(0.75)
renderer.ResetCamera()
iren.Initialize()
ren_win.Render()
iren.Start()