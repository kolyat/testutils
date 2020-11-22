# reaper

Log parser and sorter

### Requirements

- Python 3.4 or higher
- Packages listed in ```requirements.txt```. Use

    ```bash
    pip3 install -r requirements.txt
    ```
    
### Purpose

The main purpose of this tool is time reconstruction of any event. Traces of
event are searched in several log files by given pattern. 

1. Reaper downloads log files from remote directory via SFTP
2. All downloaded files are parsed by given pattern (it can be a time of any
   system event, test data, etc.), results are stored in a neighbor directory;
3. Parsed log strings are combined together in a list, which is sorted in
   ascending order by timestamp (calculated in process);
4. Final results are stored in HTML file in working directory together with 
   raw and parsed log files.

### Usage

1. Open ```settings.py``` and set up options for remote connection, working
   directory path and others;
2. Run ```reaper.py``` with one argument - selection pattern. For example:
    ```bash
    reaper.py 11:53
    ```
    where ```11:53``` is the time of known system event;
3. Go to the working directory and see the results.

Exit codes:
* 0 - normal exit
* 1 - pattern for string parsing is not defined
* 2 - no logs are available after parsing
