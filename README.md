# Duck-Weed-Image-Analysis
About Duck Weed Image Analysis
Duck Weed Image Analysis is an open-source software for counting the green pixels of duck weed within a 24 well Corning® Costar® TC-Treated Multiple Well Plate. The goal of this python tool is to provide a easy-to-use GUI for performing duck weed growth analysis with no prior programming background. A layout reference file containing an ID for each well is required (see reference.txt for an example).

## How to Use
You may run the tool from the command line or simply download the .exe file if you are not comfortable running python programs from the command line. Keep in mind python .exe files take a while to load as it must compile the code before running. Once the program has opened up you input your image file, the reference file in .txt format, the desired output folder to save results, and the output data file name to save your results to. Proceed by clicking 'Analyze'. Keep in mind the picture of the tray must be taken with 4 rows and 6 columns. It is best to take the picture using the same camera and resolution for the course of your experiment.

The input image should now display on your screen. In order to make this program flexible enough to properly identify the tray grid pattern I included a selection step. Once the image is displayed click on the top left of the tray and drag until you meet the bottom right of the tray. Once you unclick, the analysis begins and an output file containing the green pixel count will be produced.

## How it Works
Duck Weed Image Analysis utilizes a python package called plantcv for image analysis. PlantCV is an imagine analysis software library containing multiple functions for assessing plant phenotypes. This tool mainly utilizes code from the multi-plant tutorial (https://plantcv.readthedocs.io/en/stable/multi-plant_tutorial/) in order to accurately divide the multiple well plate into separate images and assess their green pixel count.

## Citation
Fahlgren N, Feldman M, Gehan MA, Wilson MS, Shyu C, Bryant DW, Hill ST, McEntee CJ, Warnasooriya SN, Kumar I, Ficor T, Turnipseed S, Gilbert KB, Brutnell TP, Carrington JC, Mockler TC, Baxter I. (2015) A versatile phenotyping system and analytics platform reveals diverse temporal responses to water availability in Setaria. Molecular Plant 8: 1520-1535. http://doi.org/10.1016/j.molp.2015.06.005

## Issues
If the image of the tray is not in the correct layout the 4x6 grid will not assess each well correctly. Trays must be imaged with 4 rows and 6 columns. Ideally, there will be a framework upon which a camera will be set up to take a picture at the same distance from the tray each time. The selection rectangle must be correctly aligned around the perimeter of the tray.
