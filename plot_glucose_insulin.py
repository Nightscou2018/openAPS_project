from matplotlib import pyplot as plt
import json

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
plt.plot(time, insulin, label = 'Insulin', color='r')
#plt.plot(time, glucose, label='Glucose')
#plt.ylabel("glucose/Insulin in mg/dL and U/hr respectively")

plt.ylabel("insulin U/hr")
#plt.ylabel("glucose in mg/dL")
plt.xlabel("time in minute")

#plt.legend()

#plt.yscale("log")
#plt.margins(x=0)
#plt.margins(y=0)
plt.show()
#print("glucose",glucose)
#print("insulin",insulin)
#print("time",time)

	
