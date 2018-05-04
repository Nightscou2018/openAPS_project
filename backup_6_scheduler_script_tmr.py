from subprocess import call
import json
import datetime
#from datetime import datetime,timedelta
import time
import os
from matplotlib import pyplot as plt


#Input to the algo_bw.js. algo_bw.js format all the info and send to glucosym server. An algorithm is running in glucosym server that calculated next glucose and send the value back.
algo_input_list = {"index":0,"BGTarget":130,"sens":45,"deltat_v":20,"dia":4,"dt":5.0,"time":6000,"bioavail":6.0,"Vg":253.0,"IRss":1.3,"events":{"bolus":[{ "amt": 0.0, "start":250}],"basal":[{ "amt":0, "start":50,"length":30}],"carb":[{"amt":0.0,"start":0,"length":0},{"amt":0.0,"start":0,"length":0}]}}

#write the algo_input_list to a file named algo_input.json so that algo_bw.js can read the input from that file
with open("../glucosym/closed_loop_algorithm_samples/algo_input.json", "w") as write_algo_input_init:
	json.dump(algo_input_list, write_algo_input_init, indent=4)
	write_algo_input_init.close()

suggested_data_to_dump = {}
list_suggested_data_to_dump = []
list_suggested_data_to_dump_1 = []
list_suggested_data_to_dump_2 = []


iteration_num = 30;

#record the time 5 minutes ago, we need this time to attach with the recent glucose value
#time_5_minutes_back = ((time.time())*1000)-3000


for _ in range(iteration_num+1):
	
######################update glucose value inside myopenaps#######################################################
	with open("monitor/glucose.json") as f:
		data = json.load(f)
		f.close()

	
	
	data_to_prepend = data[0].copy()

	
	read_glucose_from_glucosym = open("../glucosym/closed_loop_algorithm_samples/glucose_output_algo_bw.txt", "r")
	loaded_glucose = read_glucose_from_glucosym.read()
	
	
	data_to_prepend["glucose"] = loaded_glucose
	
	time_glucose = int(time.time())*1000
	
	data_to_prepend["date"] = time_glucose

	
	data.insert(0, data_to_prepend)
	

	with open('monitor/glucose.json', 'w') as outfile:
		json.dump(data, outfile, indent=4)
		outfile.close()


#######################update glucose value inside myopenaps_1#######################################################
	os.chdir("../myopenaps_1")
	
	with open("monitor/glucose.json") as f_1:
		data_1 = json.load(f_1)
		f_1.close()

	
	
	data_to_prepend_1 = data_1[0].copy()

	
	read_glucose_from_glucosym_1 = open("../glucosym/closed_loop_algorithm_samples/glucose_output_algo_bw.txt", "r")
	loaded_glucose_1 = read_glucose_from_glucosym_1.read()


	# Inject fault. Make glucose value 0	
	if _ >5:
		data_to_prepend_1["glucose"] = 0

	else:
		data_to_prepend_1["glucose"] = loaded_glucose_1
	
	data_to_prepend_1["date"] = time_glucose

	
	data_1.insert(0, data_to_prepend_1)
	

	with open('monitor/glucose.json', 'w') as outfile_1:
		json.dump(data_1, outfile_1, indent=4)
		outfile_1.close()


######################update glucose value inside myopenaps_2#######################################################

	os.chdir("../myopenaps_2")
	
	with open("monitor/glucose.json") as f_2:
		data_2 = json.load(f_2)
		f_2.close()

	
	
	data_to_prepend_2 = data_2[0].copy()

	
	read_glucose_from_glucosym_2 = open("../glucosym/closed_loop_algorithm_samples/glucose_output_algo_bw.txt", "r")
	loaded_glucose_2 = read_glucose_from_glucosym_2.read()


	# Inject fault. Make glucose value 0	
	#if _ >20:
	#	data_to_prepend_2["glucose"] = 0

	#else:
	data_to_prepend_2["glucose"] = loaded_glucose_2
	
	data_to_prepend_2["date"] = time_glucose

	
	data_2.insert(0, data_to_prepend_2)
	

	with open('monitor/glucose.json', 'w') as outfile_2:
		json.dump(data_2, outfile_2, indent=4)
		outfile_2.close()


#####################################################################################################################
	
	
	current_timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%dT%H:%M:%S-07:00')
	
	##For the very first time get the time of 5 minutes ago from now and set it to the first glucose data
	#if _==0:
	#	call("date -Ins -s $(date -Ins -d '-5 minute')", shell=True)
	#	first_glucose_to_prepend = data[0].copy()
	#	first_glucose_to_prepend["date"]=int(time.time())*1000
	#	print(data[0])
	#	print(data[0]["date"])
	#	with open("monitor/glucose.json", "w") as dump_first_glucose:
	#		json.dump(data[0], dump_first_glucose, indent=4)
	#		dump_first_glucose.close()	
	#	#print(data_to_prepend["date"])	
	
	
	call("date -Ins -s $(date -Ins -d '+5 minute')", shell=True)	

	call(["openaps", "report", "invoke", "monitor/iob.json"])
	
        #run openaps to get suggested tempbasal
	
	call(["openaps", "report", "invoke", "enact/suggested.json"])
	
	#load the output that we need to compare with other version
	with open("enact/suggested.json") as read_output_2:
		loaded_output_2 = json.load(read_output_2)
		read_output_2.close()

###############################Come back to myopenaps_1###############################

	os.chdir("../myopenaps_1")

	call(["openaps", "report", "invoke", "monitor/iob.json"])
	
        #run openaps to get suggested tempbasal
	
	call(["openaps", "report", "invoke", "enact/suggested.json"])
	
	with open("enact/suggested.json") as read_output_1:
		loaded_output_1 = json.load(read_output_1)
		read_output_1.close()		
	
###############################Come back to myopenaps##################################	
	os.chdir("../myopenaps")

	call(["openaps", "report", "invoke", "monitor/iob.json"])
	
        #run openaps to get suggested tempbasal
	
	call(["openaps", "report", "invoke", "enact/suggested.json"])
	
	with open("enact/suggested.json") as read_output:
		loaded_output = json.load(read_output)
		read_output.close()		
	
######################################## voter logic ################################################

	loaded_output['deliverAt'] = "0"
	loaded_output_1['deliverAt'] = "0"
	loaded_output_2['deliverAt'] = "0"

	if 'rate' in loaded_output and 'rate' in loaded_output_1 and 'rate' in loaded_output_2:

		if loaded_output['rate'] == loaded_output_1['rate'] == loaded_output['rate']:
			final_output = loaded_output

		elif loaded_output['rate'] == loaded_output_1['rate']:
			final_output = loaded_output

		elif loaded_output['rate'] == loaded_output_2['rate']:
			final_output = loaded_output

		elif loaded_output_1['rate'] == loaded_output_2['rate']:
			final_output = loaded_output_1

		elif loaded_output['rate'] != loaded_output_1['rate'] and loaded_output_1 != loaded_output_2['rate']:
			print("\n")
			print("***********************************************")
			print("Fault has been occured: Two output didn't match")	
			print("***********************************************")
			break
			

	else:
		if loaded_output == loaded_output_1 == loaded_output_2:
			final_output = loaded_output	
		elif loaded_output == loaded_output_1:
			final_output = loaded_output
		elif loaded_output == loaded_output_2:
			final_output = loaded_output
		elif loaded_output_1 == loaded_output_2:
			final_output = loaded_output_1

		elif loaded_output != loaded_output_1 and loaded_output_1 != loaded_output_2:
			print("\n")
			print("***********************************************")
			print("Fault has been occured: Two output didn't match")	
			print("***********************************************")
			break

	#if loaded_output['bg'] != loaded_output_1['bg']:
	#	print("Fault")
	#	break
	
	#if 'rate' in loaded_output and loaded_output_1:
	#	if loaded_output['rate'] != loaded_output_1['rate']:	
	#		print("A fault has been occured: Two outputs didn't match")
	#		break
	#else:
	#	if loaded_output['bg'] != loaded_output_1['bg']:
	#		print("A fault has been occured: Two outputs didn't match")
	#		break
		
#	current_timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%dT%H:%M:%S-07:00')
	


####################### Insinde myopenaps ######################################

	#read the output in suggested.json and append it to list_suggested_data_to_dump list. Basically we are trying to get all the suggested data and dump make a list lf that and then dump it to all_suggested.json file		
	with open("enact/suggested.json") as read_suggested:
		loaded_suggested_data = json.load(read_suggested)
		list_suggested_data_to_dump.insert(0,loaded_suggested_data)
		#list_suggested_data_to_dump.append(loaded_suggested_data)
		read_suggested.close()
	
	
	#Update pumphistory only if there is value of temp basal. For 0 temp basal, no need to update pumphistory
	if  'duration' in loaded_suggested_data.keys():
	
		with open("monitor/pumphistory.json") as read_pump_history:
			loaded_pump_history = json.load(read_pump_history) # read whole pump_history.json
			pump_history_0 = loaded_pump_history[0].copy()	#load first element
			pump_history_1 = loaded_pump_history[1].copy() #load second element, fist and second are both for one temp basal
			pump_history_0['duration (min)'] = loaded_suggested_data['duration'] #update the values
			pump_history_1['rate'] = loaded_suggested_data['rate']
			pump_history_0['timestamp'] = current_timestamp
			pump_history_1['timestamp'] = current_timestamp
			
			loaded_pump_history.insert(0, pump_history_1) # insert second element back to whatever we loaded from pumphistory
			loaded_pump_history.insert(0, pump_history_0) #insert first element back to whatever we loaded from pumphistory
			
			read_pump_history.close();
	
		with open("monitor/pumphistory.json", "w") as write_pump_history:
			json.dump(loaded_pump_history, write_pump_history, indent=4)

	# Update temp_basal.json with the current temp_basal rate and duration	
#	if 'rate' in loaded_suggested_data.keys():
	with open("monitor/temp_basal.json") as read_temp_basal:
		loaded_temp_basal = json.load(read_temp_basal)
		
		loaded_temp_basal['duration']-=5
			
		if loaded_temp_basal['duration']<=0:
			loaded_temp_basal['duration'] = loaded_suggested_data['duration']
			loaded_temp_basal['rate'] = loaded_suggested_data['rate']
		
		read_temp_basal.close()
		
	with open("monitor/temp_basal.json", "w") as write_temp_basal:
		json.dump(loaded_temp_basal, write_temp_basal, indent=4)		
	
	
	#print(suggested_data_to_dump)
	#Update all_suggested.json by writing the list_suggested_data_to_dump into all_suggested.json file
	with open("enact/all_suggested.json", "w") as dump_suggested:
		json.dump(list_suggested_data_to_dump, dump_suggested, indent=4)
		dump_suggested.close()	

	#Go to myopenaps_1 and update necessary files

############################################################## Inside myopenaps_1 ##################################################################################

	os.chdir("../myopenaps_1")

	#read the output in suggested.json and append it to list_suggested_data_to_dump list. Basically we are trying to get all the suggested data and dump make a list lf that and then dump it to all_suggested.json file		
	with open("enact/suggested.json") as read_suggested_1:
		loaded_suggested_data_1 = json.load(read_suggested_1)
		list_suggested_data_to_dump_1.insert(0,loaded_suggested_data_1)
		#list_suggested_data_to_dump.append(loaded_suggested_data)
		read_suggested_1.close()
	
	
	#Update pumphistory only if there is value of temp basal. For 0 temp basal, no need to update pumphistory
	if  'duration' in loaded_suggested_data_1.keys():
	
		with open("monitor/pumphistory.json") as read_pump_history_1:
			loaded_pump_history_1 = json.load(read_pump_history_1) # read whole pump_history.json
			pump_history_1_0 = loaded_pump_history_1[0].copy()	#load first element
			pump_history_1_1 = loaded_pump_history_1[1].copy() #load second element, fist and second are both for one temp basal
			pump_history_1_0['duration (min)'] = loaded_suggested_data_1['duration'] #update the values
			pump_history_1_1['rate'] = loaded_suggested_data_1['rate']
			pump_history_1_0['timestamp'] = current_timestamp
			pump_history_1_1['timestamp'] = current_timestamp
			
			loaded_pump_history_1.insert(0, pump_history_1_1) # insert second element back to whatever we loaded from pumphistory
			loaded_pump_history_1.insert(0, pump_history_1_0) #insert first element back to whatever we loaded from pumphistory
			
			read_pump_history_1.close();
	
		with open("monitor/pumphistory.json", "w") as write_pump_history_1:
			json.dump(loaded_pump_history_1, write_pump_history_1, indent=4)

	# Update temp_basal.json with the current temp_basal rate and duration	
#	if 'rate' in loaded_suggested_data.keys():
	with open("monitor/temp_basal.json") as read_temp_basal_1:
		loaded_temp_basal_1 = json.load(read_temp_basal_1)
		
		loaded_temp_basal_1['duration']-=5
			
		if loaded_temp_basal_1['duration']<=0:
			loaded_temp_basal_1['duration'] = loaded_suggested_data_1['duration']
			loaded_temp_basal_1['rate'] = loaded_suggested_data_1['rate']
		
		read_temp_basal_1.close()
		
	with open("monitor/temp_basal.json", "w") as write_temp_basal_1:
		json.dump(loaded_temp_basal_1, write_temp_basal_1, indent=4)		
	
	
	#print(suggested_data_to_dump)
	#Update all_suggested.json by writing the list_suggested_data_to_dump into all_suggested.json file
	with open("enact/all_suggested.json", "w") as dump_suggested_1:
		json.dump(list_suggested_data_to_dump_1, dump_suggested_1, indent=4)
		dump_suggested_1.close()	
	
######################################################## Inside myopenaps_2 ##############################################

	os.chdir("../myopenaps_2")

	#read the output in suggested.json and append it to list_suggested_data_to_dump list. Basically we are trying to get all the suggested data and dump make a list lf that and then dump it to all_suggested.json file		
	with open("enact/suggested.json") as read_suggested_2:
		loaded_suggested_data_2 = json.load(read_suggested_2)
		list_suggested_data_to_dump_2.insert(0,loaded_suggested_data_2)
		#list_suggested_data_to_dump.append(loaded_suggested_data)
		read_suggested_2.close()
	
	
	######################## Update pumphistory ############################## 
	if  'duration' in loaded_suggested_data_2.keys():
	
		with open("monitor/pumphistory.json") as read_pump_history_2:
			loaded_pump_history_2 = json.load(read_pump_history_2) # read whole pump_history.json
			pump_history_2_0 = loaded_pump_history_2[0].copy()	#load first element
			pump_history_2_1 = loaded_pump_history_2[1].copy() #load second element, fist and second are both for one temp basal
			pump_history_2_0['duration (min)'] = loaded_suggested_data_2['duration'] #update the values
			pump_history_2_1['rate'] = loaded_suggested_data_2['rate']
			pump_history_2_0['timestamp'] = current_timestamp
			pump_history_2_1['timestamp'] = current_timestamp
			
			loaded_pump_history_2.insert(0, pump_history_2_1) # insert second element back to whatever we loaded from pumphistory
			loaded_pump_history_2.insert(0, pump_history_2_0) #insert first element back to whatever we loaded from pumphistory
			
			read_pump_history_2.close();
	
		with open("monitor/pumphistory.json", "w") as write_pump_history_2:
			json.dump(loaded_pump_history_2, write_pump_history_2, indent=4)

	# Update temp_basal.json with the current temp_basal rate and duration	
#	if 'rate' in loaded_suggested_data.keys():
	with open("monitor/temp_basal.json") as read_temp_basal_2:
		loaded_temp_basal_2 = json.load(read_temp_basal_2)
		
		loaded_temp_basal_2['duration']-=5
			
		if loaded_temp_basal_2['duration']<=0:
			loaded_temp_basal_2['duration'] = loaded_suggested_data_2['duration']
			loaded_temp_basal_2['rate'] = loaded_suggested_data_2['rate']
		
		read_temp_basal_2.close()
		
	with open("monitor/temp_basal.json", "w") as write_temp_basal_2:
		json.dump(loaded_temp_basal_2, write_temp_basal_2, indent=4)		
	
	
	#print(suggested_data_to_dump)
	#Update all_suggested.json by writing the list_suggested_data_to_dump into all_suggested.json file
	with open("enact/all_suggested.json", "w") as dump_suggested_2:
		json.dump(list_suggested_data_to_dump_2, dump_suggested_2, indent=4)
		dump_suggested_2.close()
	
##########################################################################################################################
	
	#Come back to myopenaps
	os.chdir("../myopenaps")
		
	if 'rate' in final_output.keys():
      	#update the insulin parameter input of glucosym. This insulin parameters is received from openaps(suggested.json)
      		algo_input_list["events"]['basal'][0]['amt'] = final_output['rate']
      		algo_input_list["events"]['basal'][0]['length'] = final_output['duration']
#	else:
#       		
#		algo_input_list["events"]['basal'][0]['amt'] = 0
#		algo_input_list["events"]['basal'][0]['length'] = 30
	
	algo_input_list["events"]['basal'][0]['start'] = _*5
	
	
	
	#os.chdir("../glucosym/closed_loop_algorithm_samples")
	call(["node", "../glucosym/closed_loop_algorithm_samples/algo_bw.js"]);
	algo_input_list['index']=algo_input_list['index']+1

	#print(algo_input_list)

	with open("../glucosym/closed_loop_algorithm_samples/algo_input.json", "w") as write_algo_input:
		json.dump(algo_input_list, write_algo_input, indent=4)
	#os.chdir("../../myopenaps")

	
		
#	data_to_prepend = data[0].copy()
	#current_time = data_to_prepend["display_time"]
	#mytime = datetime.strptime(current_time,"%Y-%m-%dT%H:%M:%S-07:00")
	#dt = timedelta(minutes = 5)
	#mytime += dt

	#make_time_str = str(mytime).split(' ')
	#new_time_str = make_time_str[0]+"T"+make_time_str[1]+"-07:00"

	#data_to_prepend["display_time"] = new_time_str
	#data_to_prepend["dateString"] = new_time_str

	#current_time = data_to_prepend["system_time"]
	#mytime = datetime.strptime(current_time,"%Y-%m-%dT%H:%M:%S-07:00")
	#dt = timedelta(minutes = 5)
	#mytime += dt

	#make_time_str = str(mytime).split(' ')
	#new_time_str = make_time_str[0]+"T"+make_time_str[1]+"-07:00"

	#data_to_prepend["system_time"] =  new_time_str

#	read_glucose_from_glucosym = open("../glucosym/closed_loop_algorithm_samples/glucose_output_algo_bw.txt", "r")
#	loaded_glucose = read_glucose_from_glucosym.read()

	#data_to_prepend["glucose"] = int(data_to_prepend["glucose"])-5
#	data_to_prepend["glucose"] = loaded_glucose
	
#	data_to_prepend["date"]+= 300000
#	call("date -Ins -s $(date -Ins -d '+5 minute')", shell=True)	
#	data.insert(0, data_to_prepend)
	

#	with open('monitor/glucose.json', 'w') as outfile:
#		json.dump(data, outfile, indent=4)
#		outfile.close()


#This part is for ploting glucose and insulin data over the time. This section starts after all the iteration is finished
if _ == iteration_num:
	with open("enact/all_suggested.json") as read_all_suggested:
		loaded_all_suggested = json.load(read_all_suggested)
#y_list = [{"a":1, "b":1},{"a":4, "b":2},{"a":9, "b":3},{"a":16, "b":4}] 
   
#print(loaded_all_suggested)
 
	glucose = []
	insulin = []
	time = []
	 
	time_index = 0
	 
	for _ in loaded_all_suggested:
		if 'bg' in _.keys() and 'rate' in _.keys():
			glucose.insert(0,_['bg'])
			insulin.insert(0,_['rate'])
			time.append(time_index)
			time_index+=5
	#print(glucose)
	#print(time)
	plt.plot(time, glucose)
	plt.plot(time, insulin)
	plt.ylabel("glucose and Insulin")
	plt.xlabel("time")
	plt.show()
	#print("glucose",glucose)
	#print("insulin",insulin)
	#print("time",time)
else:
	print("\n")
	print("Simulation broke")
	print("\n")
