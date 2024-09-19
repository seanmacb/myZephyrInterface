import sys
import os
sys.path.append("/Users/sean/Desktop/Repos/ts_planning_tool/")
sys.path.append("/Users/sean/Desktop/Repos/ts_planning_tool/python/lsst/ts/planning/tool/")
import cli as zcli
import zephyr_interface as zint
import tests
import numpy as np
import pandas as pd
import time
import requests
from requests.auth import HTTPBasicAuth
import warnings
import asyncio
from optparse import OptionParser
# Settings the warnings to be ignored - this is prevalent with the numpydatetime64 object
warnings.filterwarnings('ignore') 
base_web_link = "https://s3df.slac.stanford.edu/data/rubin/lsstcam"
base_weekly = "w_2024_35"

export_vars = ["ZEPHYR_TOKEN","JIRA_API_TOKEN","JIRA_USERNAME"]

with open('credentials.txt','r') as f:
    for variables in export_vars:
        line = f.readline()[:-1]
        os.environ[variables] = line

headers = {'Content-Type': 'application/json','Accept': 'application/json'}
auth = HTTPBasicAuth("seanmacb@umich.edu", os.environ["JIRA_API_TOKEN"])
zepint = zint.ZephyrInterface(jira_api_token=os.environ["JIRA_API_TOKEN"],jira_username=os.environ["JIRA_USERNAME"])
zepint.zephyr_api_token = os.environ["ZEPHYR_TOKEN"]

test_cases_arr = []
for k in range(13):
    test_cases_arr.append("BLOCK-R{}".format(66+k))
test_cases_arr.append("BLOCK-R95")

def formatter(execu):
    e_num = execu['key'][6:]
    date = np.datetime64(execu['actualEndDate'])
    step_config_parse = zepint.parse(execu["testCase"])

    name_url = zepint.jira_base_url+"user?accountId="+execu["executedById"]
    name_response = requests.get(name_url,headers=headers,auth=auth)
    shifter = name_response.json()["displayName"]
    
    step_config = (step_config_parse)
    E2V_seq = execu["customFields"]["E2V sequencer config"]
    ITL_seq = execu["customFields"]["ITL sequencer config"]
    Corner_seq = execu["customFields"]["Corner sequencer config"]
    CCS_distrib = execu["customFields"]["CCS Distribution"] # Not yet implemented
    comments = execu["comment"]
    hv = execu["customFields"]["HV on?"]
    status = (zepint.parse(execu["testExecutionStatus"]))
    weekly_dist = base_weekly if execu["customFields"]["Pipeline weekly distribution"]==None else execu["customFields"]["Pipeline weekly distribution"]

    if type(comments)!=type(None):
        comments = comments.replace("<br>",", ")
    
    return {"Run #":e_num,"Date":date,"Shifter":shifter,
            "step/config":step_config,"E2V Sequencer file":E2V_seq,
            "ITL Sequencer File":ITL_seq,"Corner Sequencer File":Corner_seq,
            "CCS Distribution":CCS_distrib,"HV on?":hv,"Zephyr Comments":comments,"Status":status,
            "Web report":"{}/{}/{}/".format(base_web_link,e_num,weekly_dist),"User comments":""}

parser = OptionParser()
parser.add_option("--date","-d",dest='cutoff_date',default="2024-01-01")
options,args = parser.parse_args()
cutoff_date = np.datetime64(options.cutoff_date)

first = False
for block in test_cases_arr:
    print("Starting {}  . . . ".format(block), end=" ")
    a = asyncio.run(zepint.list_test_executions(block,max_results=10000))
    if len(a['values'])!=0:
        for execution in a['values']:
            if (asyncio.run(zepint.parse(execution["testExecutionStatus"])))['name'] != "Not Executed" and np.datetime64(execution['actualEndDate'].split("T")[0])>cutoff_date:
                result = formatter(execution)
                result["Status"] = asyncio.run(result["Status"])['name']
                # result["Shifter"] = await result["Shifter"]
                result["step/config"] = asyncio.run(result["step/config"])["name"].split(" ")[-1] 
                if not first:
                    myDF = pd.DataFrame(columns=list(result.keys()))
                    first=True
                myDF.loc[len(myDF.index)] =list(result.values())
    print("Finished")
myDF.sort_values("Date",ascending=False).to_csv("{}/ZephyrRecords.csv".format(os.getcwd()),header=True,index=False)
print("Finished, .csv contains {} entries".format(len(myDF)))