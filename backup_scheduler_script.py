from subprocess import call
import json
import datetime
from datetime import datetime,timedelta
import time

suggested_data_to_dump = {}
list_suggested_data_to_dump = []
for _ in range(5):
	
	with open("monitor/glucose.json") as f:
		data = json.load(f)
		f.close()

	
	
	
	##For the very first time get the time of 5 minutes ago from now and set it to the first glucose data
	#if _==0:
	#	call("date -Ins -s $(date -Ins -d '-5 minute')", shell=True)
	#	data[0]["date"]=int(time.time())*1000
	#	print(data[0])
	#	print(data[0]["date"])
	#	with open("monitor/glucose.json", "w") as dump_first_glucose:
	#		json.dump(data[0], dump_first_glucose, indent=4)
	#		dump_first_glucose.close()	
	#	#print(data_to_prepend["date"])	
		
       
	call(["openaps", "report", "invoke", "enact/suggested.json"])


	#read the output in suggested.json and append it to list_suggested_data_to_dump list. Basically we are trying to get all the suggest	    ed data and dump make a list lf that and then dump it to all_suggested.json file		
	with open("enact/suggested.json") as read_suggested:
		loaded_suggested_data = json.load(read_suggested)
		list_suggested_data_to_dump.append(loaded_suggested_data)
		read_suggested.close()
		
	#print(suggested_data_to_dump)
	#write the list_suggested_data_to_dump into all_suggested.json file
	with open("enact/all_suggested.json", "w") as dump_suggested:
		json.dump(list_suggested_data_to_dump, dump_suggested, indent=4)
		dump_suggested.close()	


		
	data_to_prepend = data[0].copy()
	current_time = data_to_prepend["display_time"]
	mytime = datetime.strptime(current_time,"%Y-%m-%dT%H:%M:%S-07:00")
	dt = timedelta(minutes = 5)
	mytime += dt

	make_time_str = str(mytime).split(' ')
	new_time_str = make_time_str[0]+"T"+make_time_str[1]+"-07:00"

	data_to_prepend["display_time"] = new_time_str
	data_to_prepend["dateString"] = new_time_str

	current_time = data_to_prepend["system_time"]
	mytime = datetime.strptime(current_time,"%Y-%m-%dT%H:%M:%S-07:00")
	dt = timedelta(minutes = 5)
	mytime += dt

	make_time_str = str(mytime).split(' ')
	new_time_str = make_time_str[0]+"T"+make_time_str[1]+"-07:00"

	data_to_prepend["system_time"] =  new_time_str

	data_to_prepend["glucose"] = int(data_to_prepend["glucose"])-5
	
	data_to_prepend["date"]+= 300000
	call("date -Ins -s $(date -Ins -d '+5 minute')", shell=True)	
	data.insert(0, data_to_prepend)
	

	with open('monitor/glucose.json', 'w') as outfile:
		json.dump(data, outfile, indent=4)
		outfile.close()
