# testutils

Collection of examples and utilities for testing

### Contents

##### Examples

- ```load``` - basic scenario for load testing with [locust](https://locust.io/)
- ```pom``` - web UI tests using Page Object Model

##### Tools

- ```reaper``` - tool for log parsing and sorting
- ```ddtutils``` - auxiliary functions for data driven testing tool
- ```fileutils``` - create files with random data
- ```gqlutils``` - client for GraphQL API
- ```rndutils``` - random generators of strings and numbers

##### Common files

- ```pytest.ini``` - pytest settings
- ```settings.py``` - various framework settings

### Requirements

- Python 3.4 or higher
- Packages listed in ```requirements.txt```. Use

    ```bash
    pip3 install -r requirements.txt
    ```
    
- At least Chrome Selenium WebDriver
