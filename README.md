# SML_Neo4j_Code
The code for the neo4j graph database for the statistical machine learning (CSE 575) class.

# Using the code
There are a few steps that must be done before the code can be run. This is to add libraries for Neo4j and the program to run the database
  on localhost

1. Download Neo4j at https://neo4j.com/download/ under "For Individuals." The software is not massive, and should install fairly quickly.
    Once the software is installed, run the program. This will bring up a small window with a database location and the status. Database
    location tells the program where to store the data on the hard drive and should not need to be edited. Click 'start' and wait for the 
    status indicator to turn green. The URL should read "http://127.0.0.1:7474/". Make sure that any firewalls have exceptions set for this
    program and its local ports, 7474 and 7687. All database queries will go through these ports and may be interrupted by firewall.
   
2. Install the Neo4j library for the project on your computer. This is easily done by going to the python command line and typing
    "pip install neo4j-driver." Python should automatically locate and add the library.
    
The program should now be executable on the device.

On the bottom of Parser.py, the main function is defined with several variables that may be adjusted depending on execution preferences.

1. jsonFile should be the file location of the json file to be parsed and fed into the database. The json parser is specifically tuned to 
     the format of Open Academic Graph files found at https://www.openacademic.ai/oag/. The software was tested on these, and it is 
     recommended any user try a smaller dataset, such as mag_papers_166.txt found in mag_papers_8.zip, before attempting one of the larger
     sets.
     
2. mark should be set to the string marking which will be placed on marked nodes. This is entirely for visual purposes, and will not have
     any effect on execution
     
3. Below are the settings indicating which nodes to mark. Users can either comment out lines under B and enter in the names of
     the nodes to be marked manually (using author name) OR comment out lines under A and enter an integer for numberOfNodesToMark to 
     randomly select that many nodes from the set of all nodes.
