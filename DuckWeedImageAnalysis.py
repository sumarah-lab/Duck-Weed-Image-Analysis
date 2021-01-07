import PySimpleGUI as sg
import random
import string
import cv2 as cv
from plantcv import plantcv as pcv
import numpy as np
import csv

def draw_rectangle(start=None, end=None):
	"""
	Displays selection rectangle on top of image file (requires the image to be redrawn each time)
	
	Parameters
	----------
	start : tuple
		X,Y coordinates of the starting point of the selection rectangle
	end : tuple
		X,Y coordinates of the ending point of the selection rectangle
	"""
	
	if start is not None and end is not None:
		graph.DrawImage(data=imgbytes, location=(0, 0))
		graph.draw_rectangle(start,end, line_color='white')

def draw_plot(x_start, y_start, x_end, y_end, reference_file, save_file):
	"""
		Utilizes plantcv (citation below) to count the green pixels (Chlorophyll) of wells containg plants in a 4x6 grid format of the selected tray.
		
		Outputs
		-------
		A csv file containing the green pixel count for each well containing plants within the grid 
		
		Parameters
		----------
		x_start : int
			Contains the x coordinate of the top left of the user selection
		y_start : int
			Contains the y coordinate of the top left of the user selection
		x_end : int
			Contains the x coordinate of the bottom right of the user selection
		y_end : int
			Contains the y coordinate of the bottom right of the user selection
		reference_file : str
			A txt file containing the names of each well of the tray
		save_file : str
			A csv file to output the green pixel count for each well of the tray
		
		Citation
		--------
		Fahlgren N, Feldman M, Gehan MA, Wilson MS, Shyu C, Bryant DW, Hill ST, McEntee CJ, Warnasooriya SN, Kumar I, Ficor T, Turnipseed S, Gilbert KB, Brutnell TP, Carrington JC, Mockler TC, Baxter I. (2015) A versatile phenotyping system and analytics platform reveals diverse temporal responses to water availability in Setaria. Molecular Plant 8: 1520-1535. http://doi.org/10.1016/j.molp.2015.06.005
		
		Website Link
		------------
		https://plantcv.readthedocs.io/en/stable/
	"""
	
	# Resize x,y values from the resized image to the initial raw image x,y coordinates for an accurate count on pixels
	x_start = x_start * img_width/dim[0]
	y_start = y_start * img_height/dim[1]
	x_end = x_end * img_width/dim[0]
	y_end = y_end * img_height/dim[1]
	
	# Crop raw image to selection window
	cropped = pcv.crop(img, x=int(x_start), y=int(y_start), h=int(y_end-y_start), w=int(x_end-x_start))
	
	# Debug code to display cropped image. Uncomment to see cropped window
	#cropbytes = cv.imencode('.png', cropped)[1].tobytes()
	#graph.DrawImage(data=cropbytes, location=(0, 0))
	
	
		
	# Utilize plantcv code to count green pixels within selection window
	# For further information see : https://plantcv.readthedocs.io/en/latest/multi-plant_tutorial/
	img1 = pcv.white_balance(img=cropped,roi=(0,0,50,50))
	a = pcv.rgb2gray_lab(rgb_img=img1, channel='a')
	img_binary = pcv.threshold.binary(gray_img=a, threshold=115, max_value=255, object_type='dark')
	fill_image = pcv.fill(bin_img=img_binary, size=80)
	dilated = pcv.dilate(gray_img=fill_image, ksize=2, i=1)
	id_objects, obj_hierarchy = pcv.find_objects(img=img1, mask=dilated)
	roi_contour, roi_hierarchy = pcv.roi.rectangle(img=img1, x=0, y=0, h=int(y_end-y_start), w=int(x_end-x_start))
	roi_objects, roi_obj_hierarchy, kept_mask, obj_area = pcv.roi_objects(img=img1, roi_contour=roi_contour, 
                                                                          roi_hierarchy=roi_hierarchy,
                                                                          object_contour=id_objects,
                                                                          obj_hierarchy=obj_hierarchy, 
                                                                          roi_type='partial')
	clusters_i, contours, hierarchies = pcv.cluster_contours(img=img1, roi_objects=roi_objects, 
                                                             roi_obj_hierarchy=roi_obj_hierarchy, 
                                                             nrow=4, ncol=6, show_grid=True)
	output_path, imgs, masks = pcv.cluster_contour_splitimg(img1, grouped_contour_indexes=clusters_i, contours=contours, hierarchy=hierarchies, file=filename,filenames=reference_file)
	
	# Save green pixel count for each well of the tray to a csv file using the reference file to name each well
	results = []
	for f in range(len(imgs)):  
		color_histogram = pcv.analyze_color(rgb_img=imgs[f], mask=kept_mask, hist_plot_type='rgb')
		
		# Access data stored out from analyze_color
		hue_circular_mean = pcv.outputs.observations['green_frequencies']['value']
		
		result = [output_path[f].split('_')[1],np.trapz(hue_circular_mean)]
		results.append(result)
		
	with open(save_file, "w", newline="") as fil:
		writer = csv.writer(fil)
		writer.writerows(results)
		sg.Popup('Finished Analysis! Please see the .csv file for results!')
	
def image_analysis(input_image, reference_file, save_file):
	"""
	Displays the image and waits for the user to select a rectangle around the tray.
	
	Parameters
	----------
	input_image : str
		The name of the image file in png format
	reference_file : str
		The name of the reference file in txt format
	save_file: : str
		The desired name to save the resulting csv file
	"""
	
	global layout_image
	global graph
	global imgbytes
	global img
	global img_width
	global img_height 
	global dim
	global filename
	
	# Grab window size to display the image of the appropriate height/width
	win_width, win_height = sg.Window.get_screen_size()
	
	# Leave a 100 pixel gap for text and button
	print(int(np.round(win_height*0.15)))
	win_height = win_height - int(np.round(win_height*0.15)) #100
	win_ratio = win_width/(win_height)

	# Set layout to contain the image as a pysimplegui graph, followed by text
	layout_image = [
		[
			sg.Graph(
				canvas_size=(win_width, win_height),
				graph_bottom_left=(0, win_height),
				graph_top_right=(win_width, 0),
				key="graph",
				enable_events=True,
				drag_submits=True,
				change_submits=True
			)
		],[
			sg.Text("", key="info", size=(80,1),font=("Helvetica", 20))
		],[
			sg.Button('Perform another Analysis?',font=("Helvetica",20)), sg.Exit()
		]
	]

	# Need keyboard events to be recorded
	window = sg.Window("rect on image",return_keyboard_events=True).Layout(layout_image)
	window.Finalize()
	window.Maximize()

	graph = window.Element("graph")
	
	# Read the image into plantcv for analysis
	img, path, filename = pcv.readimage(filename=input_image, mode='rgb')

	# Resize img to specific window size
	img_width = img.shape[1]
	img_height = img.shape[0]
	img_ratio = img_width/img_height

	# Resize image according to window dimensions
	if (win_ratio > img_ratio):
		dim = (int(img_width * (win_height/img_height)), win_height)
		resized = cv.resize(img, dim, interpolation = cv.INTER_AREA)
		print('first')
	else:
		dim = (win_width, int(img_height*(win_width/img_width)))
		print(dim)
		resized = cv.resize(img, dim, interpolation = cv.INTER_AREA)

	# Convert cv2 image code to imen code for displaying using graph.DrawImage
	imgbytes = cv.imencode('.png', resized)[1].tobytes()
	graph.DrawImage(data=imgbytes, location=(0, 0))

	# Set dragging to false until user left clicks
	dragging = False
	start_point, end_point = None, None

	while True:
		# Timeout needs to be higher otherwise selection rectangle slows everything down
		event, values = window.read(timeout=100)
		
		info  = window.Element("info")
		info.Update(value="Please select the tray.")
		
		
		if event == 'Perform another Analysis?':
			window.Close()
			main()
		
		
		print(event)
		if event is None:
			break # exit

		# Wait for user input in graph (left click)
		if event == "graph":
			x,y = values["graph"]
			
			if not dragging:
				start_point = (x,y)
				dragging = True
			# When dragging stops record end point
			else:
				end_point = (x,y)
			
			# Ccontinuously draw rectangle for selection window
			draw_rectangle(start=start_point, end=end_point)
		
		# Wait for user to stop clicking left mouse
		elif event.endswith('+UP'):
			end_point = (x,y)
			dragging = False
			
			# Draw final selection window
			draw_rectangle(start=start_point, end=end_point)
			
			# Calculate green pixels using PlantCV
			draw_plot(start_point[0], start_point[1], end_point[0], end_point[1], reference_file, save_file)
			
	window.close()
	
def main():
	"""
	Displays GUI window for inputting required files.
	
	Input Image : Desired png file to undergo green pixel analysis
	Reference File : Contains the names of the columns and rows in txt format.
		Starts to bottom and then left to right.
	Output Folder : Folder to save the resulting csv file
	Output Data File Name : The desired name of the csv file.
	"""
	
	layout = [[sg.Text('Plant Image Analysis')],
              [sg.Text('Input Image', size=(18, 1)), sg.InputText(), sg.FileBrowse()],
              [sg.Text('Reference File', size=(18, 1)), sg.InputText(), sg.FilesBrowse()],
              [sg.Text('Output Folder', size=(18,1)), sg.InputText(), sg.FolderBrowse()],
              [sg.Text('Output Data File Name', size=(18, 1)), sg.InputText()],
              [sg.Button('Analyze'), sg.Exit()]]
			  
	
	# Display window and wait for user input
	window = sg.Window('Plant Image Analysis', layout)
	while True:
		event, values = window.Read()
		
		if event is None or event == 'Exit':
			break
		if event == 'Analyze':
			# Grab the input files from the from the input file window
			input_image, reference_file, save_folder, save_file_tag = values[0], values[1], values[2], values[3]
			if not (save_file_tag.endswith('.csv')):
				save_file_tag = (save_file_tag + ".csv")
			save_file_path = (save_folder + "/" + save_file_tag)
			if not (reference_file.endswith('.txt')):
				sg.Popup('Please input a txt file!')
			elif not (input_image.endswith('.png')):
				sg.Popup('Please input a png file!')
			else:
					# Close file input window and open the image analysis window 
					window.Close()
					image_analysis(input_image, reference_file, save_file_path)

main()	