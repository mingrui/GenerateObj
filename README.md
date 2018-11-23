# GenerateObj
A 3D Slicer Module that 1. uses ROBEX brain extraction to generate mesh.obj;  2. tumor label mask to mesh.obj

A custom 3D Slicer module/extension for generating .obj file to be used in Unity 3D  

![alt text](https://cdn-images-1.medium.com/max/1000/1*LNTgrwKMiup_Nw44wnTRcw.png)

1. To install a custom module/extension, you have to copy your script to your 3dslicer module folder.  
2. To find where 3dslicer module folder is, start 3dslicer, click edit/settings/modules, under “Additional module paths”, you will see the module folders.  
3. Copy script to module folder.  
4. Restart 3dslicer, your new module script will be loaded.  
5. It is a good idea to open the python interactor to monitor command line print statements. Go to View/Python Interactor
In our case, our new module script is GenerateObj.py, to go Modules drop down: /Surface Models/ Generate Obj Model  
6. To generate .obj files from tumor segmentations, you need to input 3 text fields: 1. the folder path, searches for .nii files will be done under this folder recursively. 2. the tumor segmentation .nii file names. 3. output file names.  

For windows users, you have to change the file path delimiter from “\” to “/”

![alt text](https://cdn-images-1.medium.com/max/1000/1*cwGRfOsARrZSSr85uEia8A.png)

Click on Generate segmentation.obj  
The segmentation will be saved at the save folder as the nifti file.
