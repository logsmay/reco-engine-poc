The SKU recommendation algorithm is written in python, pandas and the web-api to query the skus is written through Flask.

Steps to execute:
- This code relies on Pandas & Flask. To execute the code, either we can install the packages available in requirements.txt or available virtual env with all the necessary packages.
- Execute the shell script. Make sure you the virtualenv activated & update the reco.cfg `data_input` with the source path of the input json data.

$> cd /go/to/reco-problem/directory
$> virtualenv -p /usr/bin/python2.7 venv
$> source venv/bin/activate
$> pip install -r requirements.txt
$> sh execute.sh

execute.sh in-turn executes run_server.py where the logic for recommendation is, and once the data is loaded into the pandas dataframe, it can be queried to display html/json response through any browser as there is micro webframework running in the background:

1. hostname:<port>/ will take you to a query dashboard to enter sku & reco suggestion counts.

2. hostname:<port>/<html/json>/<recommended-sku-count>/<sku-name>
localhost e.g.: 127.0.0.1:8081/html/10/sku-123

It will display the queried sku attributes, also it's respective recommended skus with the calculated alpha score, attribute match counts & matching attributes.

For further configurations, check reco.cfg 

Algorithm:
> Load json data {D} into the dataframe [DF]
> Match attribute_query(sku) in [DF] and create a attribute matching bool matrix [[sku1,sku2...][att-a,att-b...]]
> Calculate [attributeSumDF] = BooleanSum([sku(1..n)](att-a=True,att-b=False,att-c=True...))
> Generate geometric Series [GS] 1/(2^n) where n=0,1,2,3,... for series[att-a,att-b,att-c...]
> Calculate [geometricSumDF] = [GS] X sum([sku(1..n)](att-a=True, att-b=False, att-c=True))
> MemJoin [DF] X [attributeSumDF] X [geometricSumDF] order by attribSum & geometricSum limit with the input reco count (reco_num)
> Generate HTML/Json from the final data & feed it to webframework
