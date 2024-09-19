This script fetches all of the relevant data from the EO Run 7 test plan and formats it for insertion to the confluence database
Requirements
    - The [ts_planning_tool](https://github.com/lsst-ts/ts_planning_tool/tree/develop) package, which allows you to use the Zephyr Scale API
    - A text file named credentials.txt that contains the following three lines at the top of the file:
        - ZEPHYR_TOKEN: A token for the Zephyr Scale API
        - JIRA_API_TOKEN: A token for the JIRA api
        - JIRA_USERNAME: Your jira username, which is usually your email (ex. seanmacb@umich.edu)
    - Due to sub-shells, you also have to define these environment variables directly within the cli.py file

