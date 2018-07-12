# testutils

Collection of examples and utilities for testing

### Contents

##### Examples

- ```load_test``` - scenario for load testing with **locust**
- ```test_ui``` - UI tests with **seleniumbase**

##### Tools

- ```reaper``` - tool for log parsing and sorting
- ```ddtutils``` - auxiliary functions for data driven testing tool
- ```gqlutils``` - client for GraphQL API
- ```rndutils``` - random generators of strings and numbers

##### Common files

- ```settings.py``` - various framework settings
- ```run.py``` - test launcher, contains test plans and options
- ```run.sh``` - shell script as an alternative for python virtualenv 
                 activation and test run

### Requirements

- Python 3.4 or higher
- Packages listed in ```requirements.txt```. Use

    ```bash
    pip3 install -r requirements.txt
    ```
    
- At least Chrome Selenium WebDriver
