'''
  * ***************************************************************
  *      Program: MATSim Network Generator
  *      Type: Python
  *      Author: David Velasco Garcia @davidvelascogarcia
  * ***************************************************************
'''

# Libraries
import os
os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = pow(2,40).__str__()

import cv2
import datetime
from dxfwrite import DXFEngine as dxf
from halo import Halo
import platform


class MATSimNetGenerator:

    # Function: Constructor
    def __init__(self):

        # Build Halo spinner
        self.systemResponse = Halo(spinner='dots')

    # Function: getSystemPlatform
    def getSystemPlatform(self):

        # Get system configuration
        print("\nDetecting system and release version ...\n")
        systemPlatform = platform.system()
        systemRelease = platform.release()

        print("**************************************************************************")
        print("Configuration detected:")
        print("**************************************************************************")
        print("\nPlatform:")
        print(systemPlatform)
        print("Release:")
        print(systemRelease)

        return systemPlatform, systemRelease

    # Function: getRootFiles
    def getRootFiles(self):

        # Build list files array
        files = []

        # Get list files but not file manager program
        for file in os.listdir("."):

            if str(file) == "matsimNetGenerator.py":

                systemResponseMessage = "\n[INFO] Skipping matsimNetGenerator.py file ...\n"
                self.systemResponse.text_color = "yellow"
                self.systemResponse.warn(systemResponseMessage)

            elif ".jpg" in str(file) or ".png" in str(file) or ".bmp" in str(file) or ".tiff" in str(file) or ".jpeg" in str(file):

                systemResponseMessage = "\n[INFO] File founded: " + str(file) + ".\n"
                self.systemResponse.text_color = "blue"
                self.systemResponse.info(systemResponseMessage)

                files.append(file)

        systemResponseMessage = "\n[INFO] " + str(len(files)) + " files founded.\n"
        self.systemResponse.text_color = "green"
        self.systemResponse.succeed(systemResponseMessage)

        return files

    # Function: getFileParameters
    def getFileParameters(self, file):

        fileSplit = file.split(".")
        extension = fileSplit[int(len(fileSplit)) - 1]

        # If is not a file and it´s a dir len no change
        if len(file) == len(extension):

            # Set as name
            fileName = extension

            # Set file extension as void
            fileExtension = ""

        else:
            # Set as name the file original name removing extension
            fileName = file.replace("." + str(extension), "")

            # Set file extension split
            fileExtension = extension

        return fileName, fileExtension

    # Function: buildFileDir
    def buildFileDir(self, fileName):

        try:
            # Get dir path
            dirPath = "./" + str(fileName)

            # Create dir
            os.mkdir(str(dirPath))

        except:
            systemResponseMessage = "\n[ERROR] Error building " + str(fileName) + " file dir.\n"
            self.systemResponse.text_color = "red"
            self.systemResponse.fail(systemResponseMessage)

    # Function: getCannyEdges
    def getCannyEdges(self, dataToSolve):

        # Convert data to solve to greyscale
        dataToSolve = cv2.cvtColor(dataToSolve, cv2.COLOR_BGR2GRAY)

        # Reduce noise
        # dataToSolve = cv2.GaussianBlur(dataToSolve, (5, 5), 1.4)

        # Detect edges
        dataSolved = cv2.Canny(dataToSolve, 100, 200)

        return dataSolved

    # Function: getContours
    def getContours(self, dataSolved):

        # Get initial image size
        dataHeight, dataWidth = dataSolved.shape

        # Find contours
        ret, thresh = cv2.threshold(dataSolved, 40, 255, 0)
        im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)

        # Chain approximation: CHAIN_APPROX_NONE (all points connect 2to2, FULL detail), CHAIN_APPROX_SIMPLE (compress contours), CHAIN_APPROX_TC89_L1 (heuristic simple very lineal), CHAIN_APPROX_TC89_KCOS  (heuristic simple 2)
        # Retrieval mode: RETR_EXTERNAL (extremal contours),  RETR_LIST (all without relation), RETR_CCOMP (all relation two levels), RETR_TREE (all reconstruct and relation FULL)

        return dataHeight, dataWidth, contours

    # Function: saveDataSolved
    def saveDataSolved(self, fileName, fileExtension, dataSolved):

        # Get save path
        savePath = "./" + str(fileName) + "/" + str(fileName) + "Processed." + str(fileExtension)

        # Save data solved into file
        cv2.imwrite(savePath, dataSolved)

    # Function: svgVectorization
    def svgVectorization(self, fileName, dataWidth, dataHeight, contours):

        try:
            self.systemResponse.text = "Building SVG file ..."
            self.systemResponse.text_color = "blue"
            self.systemResponse.start()

            # Get output paths
            dirPath = "./" + str(fileName)
            fileName = str(fileName) + ".svg"
            savePath = dirPath + "/" + fileName

            # Build SVG file
            file = open(str(savePath), "w+")

            # Prepare SVG header
            header = '<svg width="' + str(dataWidth) + '" height="' + str(dataHeight) + '" xmlns="http://www.w3.org/2000/svg">'

            # Write header
            file.write(header)

            # Write contours
            for contour in contours:

                # Write connection
                file.write('<path d="M')

                # For each contour get points
                for i in range(len(contour)):

                    # Get point coordinates
                    x, y = contour[i][0]

                    # Prepare point connection
                    point = str(x) + " " + str(y) + " "

                    # Write point
                    file.write(point)

                # Write line colour
                file.write('" style="stroke:blue"/>')

            # Write SVG file ends
            file.write("</svg>")

            # Close file
            file.close()

            self.systemResponse.stop()

            systemResponseMessage = "\n[INFO] " + str(fileName) + " file generated correctly.\n"
            self.systemResponse.text_color = "green"
            self.systemResponse.succeed(systemResponseMessage)

        except:
            systemResponseMessage = "\n[ERROR] Error generating " + str(fileName) + " SVG file.\n"
            self.systemResponse.text_color = "red"
            self.systemResponse.fail(systemResponseMessage)

    # Function: dxfVectorization
    def dxfVectorization(self, fileName, contours):

        try:
            self.systemResponse.text = "Building DXF file ..."
            self.systemResponse.text_color = "blue"
            self.systemResponse.start()

            # Get output paths
            dirPath = "./" + str(fileName)
            fileName = str(fileName) + ".dxf"
            savePath = dirPath + "/" + fileName

            # Build DXF file
            file = dxf.drawing(str(savePath))

            # Add layer
            file.add_layer('LINES')

            # Write contours
            for contour in contours:

                # Unset contour as first time to set at starter point
                firstTime = 0

                # For each contour get points
                for i in range(len(contour)):

                    if int(firstTime) == 0:
                        # Get point coordinates
                        x, y = contour[i][0]

                        # Set as initial point
                        initialX = x
                        initialY = y

                        # Ends first time
                        firstTime = 1

                    else:
                        # Get point coordinates
                        x, y = contour[i][0]
                        finalX = x
                        finalY = y

                        # Draw line in layer
                        file.add(dxf.line((int(initialX), int(initialY)), (int(finalX), int(finalY)), color=7, layer='LINES'))

                        # Set final point to be new initial point
                        initialX = finalX
                        initialY = finalY

            # Close and save file
            file.save()

            self.systemResponse.stop()

            systemResponseMessage = "\n[INFO] " + str(fileName) + " file generated correctly.\n"
            self.systemResponse.text_color = "green"
            self.systemResponse.succeed(systemResponseMessage)

        except:
            systemResponseMessage = "\n[ERROR] Error generating " + str(fileName) + " DXF file.\n"
            self.systemResponse.text_color = "red"
            self.systemResponse.fail(systemResponseMessage)

    # Function: netGenerator
    def netGenerator(self, fileName, contours):

        try:
            self.systemResponse.text = "Building XML file ..."
            self.systemResponse.text_color = "blue"
            self.systemResponse.start()

            # Get output paths
            dirPath = "./" + str(fileName)
            fileName = "network.xml"
            savePath = dirPath + "/" + fileName

            # Build XML file
            file = open(str(savePath), "w+")

            # Prepare XML header
            header = '<?xml version="1.0" encoding="utf-8"?>' + '\n' + '<!DOCTYPE network SYSTEM "http://www.matsim.org/files/dtd/network_v1.dtd">\n\n'
            header = header + '<network name="' + str(fileName) + '">\n'

            # Write header
            file.write(header)

            # Prepare id variables
            id_node = 1
            id_connection = 1

            # Prepare links vector
            links = []

            # Write nodes
            file.write('<nodes>\n')

            for contour in contours:

                # Unset contour as first time to set at starter point
                firstTime = 0

                # For each contour get points
                for i in range(len(contour)):

                    if int(firstTime) == 0:
                        # Get point coordinates
                        x, y = contour[i][0]

                        # Set as initial point
                        initialX = x
                        initialY = y

                        # Ends first time
                        firstTime = 1

                    else:
                        # Get point coordinates
                        x, y = contour[i][0]
                        finalX = x
                        finalY = y

                        # Set final point to be new initial point
                        initialX = finalX
                        initialY = finalY

                        # Prepare link message
                        link_message = '<link id="' + str(id_connection) + '" from="' + str(id_node - 1) + '" to="' + str(id_node) + '" length="10000.00" capacity="36000" freespeed="27.78" permlanes="1"/>\n'
                        links.append(str(link_message))

                    # Write node
                    node_message = '<node id="' + str(id_node) + '" x="' + str(x) + '" y="' + str(y) + '"/>\n'
                    file.write(node_message)

                    # Increase id variables
                    id_node = id_node + 1
                    id_connection = id_connection + 1

            # Write nodes file ends
            file.write('</nodes>\n')

            # Write connection header
            file.write('<links capperiod="01:00:00">\n')

            # Write each link
            for connection in links:
                file.write(str(connection))

            # Write end links and network
            file.write('</links>\n')
            file.write('</network>\n')

            # Close file
            file.close()

            self.systemResponse.stop()

            systemResponseMessage = "\n[INFO] " + str(fileName) + " file generated correctly.\n"
            self.systemResponse.text_color = "green"
            self.systemResponse.succeed(systemResponseMessage)

        except:
            systemResponseMessage = "\n[ERROR] Error generating " + str(fileName) + " XML file.\n"
            self.systemResponse.text_color = "red"
            self.systemResponse.fail(systemResponseMessage)

    # Function: processRequests
    def processRequests(self, files):

        print("\n**************************************************************************")
        print("Processing request:")
        print("**************************************************************************\n")

        try:
            # Get initial time
            initialTime = datetime.datetime.now()

            # Prepare variable to count files processed
            numProcessed = 0

            # For each file process
            for file in files:

                # Increase numProcessed
                numProcessed = numProcessed + 1

                systemResponseMessage = "\n[INFO] Processing " + str(file) + ": " + str(numProcessed) + "/" + str(len(files))
                self.systemResponse.text_color = "blue"
                self.systemResponse.info(systemResponseMessage)

                # Extract file name and extension
                fileName, fileExtension = self.getFileParameters(file)

                # Build file dir
                self.buildFileDir(fileName)

                # Get data to solve
                dataToSolve = cv2.imread(str(file))

                # Get edges
                dataSolved = self.getCannyEdges(dataToSolve)

                # Get contours
                dataHeight, dataWidth, contours = self.getContours(dataSolved)

                # Save data solved into file
                self.saveDataSolved( fileName, fileExtension, dataSolved)

                # Vectorize data solved into SVG file
                self.svgVectorization(fileName, dataWidth, dataHeight, contours)

                # Vectorize data solved into DXF file
                self.dxfVectorization(fileName, contours)

                # Generate MATSim network into XML file
                self.netGenerator(fileName, contours)

            systemResponseMessage = "\n[INFO] Request done correctly.\n"
            self.systemResponse.text_color = "green"
            self.systemResponse.succeed(systemResponseMessage)

            # Get end time
            endTime = datetime.datetime.now()

            # Compute elapsed time
            elapsedTime = endTime - initialTime

            systemResponseMessage = "\n[INFO] Elapsed time: " + str(elapsedTime) + ".\n"
            self.systemResponse.text_color = "blue"
            self.systemResponse.info(systemResponseMessage)

        except:
            systemResponseMessage = "\n[ERROR] Error, processing request.\n"
            self.systemResponse.text_color = "red"
            self.systemResponse.fail(systemResponseMessage)


# Function: main
def main():

    print("**************************************************************************")
    print("**************************************************************************")
    print("                   Program: MATSim Network Generator                      ")
    print("                     Author: David Velasco Garcia                         ")
    print("                             @davidvelascogarcia                          ")
    print("**************************************************************************")
    print("**************************************************************************")

    print("\nLoading MATSim Network Generator engine ...\n")

    # Build matsimNetGenerator object
    matsimNetGenerator = MATSimNetGenerator()

    # Get system platform
    systemPlatform, systemRelease = matsimNetGenerator.getSystemPlatform()

    # Get root files
    files = matsimNetGenerator.getRootFiles()

    # Process input requests
    matsimNetGenerator.processRequests(files)

    print("**************************************************************************")
    print("Program finished")
    print("**************************************************************************")
    print("\nmatsimNetGenerator program finished correctly.\n")

    userExit = input()


if __name__ == "__main__":

    # Call main function
    main()