Log analyzer Homework  
Consists of:  
log_analyzer.py - script  
README.md - readme  
Script to parse '.log' files with 2 options implemented
_____________________________________
--d 'path to the directory' - is used to parse all files in directory  
--f 'directory/filename' - is used to parse the single file
_____________________________________
Output is loaded into 'output.json'  
1 - quantity of requests by method  
2 - top 10 requests by duration  
3 - top 10 client errors by duration  
4 - top 10 server errors by duration  