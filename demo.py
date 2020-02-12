#!/usr/bin/env python3
# Sample Padatious program used for testing

import os
import sys
import json
from builtins import input
from glob import glob
from os.path import basename

from padatious import IntentContainer
from padatious.util import expand_parentheses

class FnnClassifier(object):

	def __init__(self, data_path, cache_path):
		self.data_path = data_path
		self.cache_path = cache_path
		self.container = IntentContainer(self.cache_path)

	def cleanup(self):                
		for files in [ '*.intent', '*.entity', '*.response' ]:
			for file_name in glob( self.data_path + files ):
				os.remove(file_name)		

		for file_name in glob( self.cache_path + '*.*'):
				os.remove(file_name)

	def load(self):
		response_json_data = {}
		with open( self.data_path + 'data.json', 'r') as data_json:
			json_data = json.load(data_json)
			
			for data in json_data["intents"]:				
				# print(data, json_data)
				if "intent" in json_data["intents"][data]:
					with open( self.data_path + data + '.intent', 'w') as intent_file:
						for intent in json_data["intents"][data]['intent']:
							intent_file.write(intent + '\n')
				
				if "response" in json_data["intents"][data]:
					with open( self.data_path + data + '.response', 'w') as response_file:
						for response in json_data["intents"][data]['response']:
							response_file.write(response + '\n')
							expanded_value = [ ''.join(s) for s in expand_parentheses(response) ]
							if data in response_json_data:
								response_json_data[ data ] = response_json_data[ data ] + expanded_value
							else:
								response_json_data[ data ] = expanded_value
   
			with open( self.cache_path + 'response.json', 'w') as fp:
				json.dump(response_json_data, fp)

		# with open( self.data_path + 'data_entity.json', 'r') as data_json:
			# json_data = json.load(data_json)
			
			for data in json_data["entities"]:				
				with open( self.data_path + data + '.entity', 'w') as intent_file:
					for intent in json_data["entities"][data]:
						intent_file.write(intent + '\n')

	def train(self):
		# load intents
		for file_name in glob(self.data_path + '*.intent'):
			name = basename(file_name).replace('.intent', '')
			self.container.load_file(name, file_name, reload_cache=True)

		# load entity
		for file_name in glob(self.data_path + '*.entity'):
			name = basename(file_name).replace('.entity', '')
			self.container.load_entity(name, file_name, reload_cache=True)

		# train container in multithread
		self.container.train(debug=True, force=False, single_thread=True)

	def add_intent(self, name: str, lines: list, reload_cache: bool):
		inserted_flag = False
		for file_name in glob(self.data_path + '*.intent'):
			if name == basename(file_name).replace('.intent', ''):
				inserted_flag = True
				with open(file_name, "a") as myfile:
					for line in lines:
						myfile.write('\n'+line)

		if not inserted_flag:
			with open(self.data_path + name + '.intent', "w") as myfile:
				for line in lines:
					myfile.write('\n'+line)
		
		json_data = None
		with open( self.data_path + 'data.json', 'r') as data_json:
			json_data = json.load(data_json)

			if name in json_data["intents"]:
				source = json_data["intents"][name]["intent"]
				target = lines
				result = source + list( set(target) - set(source) )
				json_data["intents"][name]["intent"] = result
			else:
				json_data["intents"][name] = {
					"intent": lines
				}

		with open(self.data_path + 'data.json', 'w') as fp:
			json.dump(json_data, fp)

		self.container.add_intent(name, lines, reload_cache)

	def add_entity(self, name: str, lines: list, reload_cache: bool):
		inserted_flag = False
		for file_name in glob(self.data_path + '*.entity'):
			if name == basename(file_name).replace('.entity', ''):
				inserted_flag = True
				with open(file_name, "a") as myfile:
					for line in lines:
						myfile.write('\n'+line)

		if not inserted_flag:
			with open(self.data_path + name + '.entity', "w") as myfile:
				for line in lines:
					myfile.write('\n'+line)
		
		json_data = None
		with open( self.data_path + 'data.json', 'r') as data_json:
			json_data = json.load(data_json)

			if name in json_data["entities"]:
				source = json_data["entities"][name]
				target = lines
				result = source + list( set(targt) - set(source) )
				json_data["entities"][name] = result
			else:
				json_data["entities"][name] = lines

		with open(self.data_path + 'data.json', 'w') as fp:
			json.dump(json_data, pf)

		self.container.add_entity(name, lines, reload_cache)

	def add_response(self, name: str, lines: list):
		
		json_data = None
		with open( self.cache_path + 'response.json', 'r') as data_json:
			json_data = json.load(data_json)

			if name in json_data:
				source = json_data[name]
				target = lines
				result = source + list( set(targt) - set(source) )
				json_data[name] = result
			else:
				json_data[name] = lines

		with open(self.cache_path + 'response.json', 'w') as fp:
			json.dump(json_data, fp)

		json_data = None
		with open( self.data_path + 'data.json', 'r') as data_json:
			json_data = json.load(data_json)

			if name in json_data["intents"]:
				if "response" in json_data["intents"][name]:
					source = json_data[name]["response"]
					target = lines
					result = source + list( set(targt) - set(source) )
					json_data["intents"][name]["response"] = result
				else:
					json_data["intents"][name]["response"] = lines

		with open(self.data_path + 'data.json', 'w') as fp:
			json.dump(json_data, fp)
   

# reload_cache = len(sys.argv) > 1 and sys.argv[1] == '-r'
# container = IntentContainer('intent_cache')

# for file_name in glob('data/*.intent'):
#     name = basename(file_name).replace('.intent', '')
#     container.load_file(name, file_name, reload_cache=reload_cache)

# for file_name in glob('data/*.entity'):
#     name = basename(file_name).replace('.entity', '')
#     container.load_entity(name, file_name, reload_cache=reload_cache)


# container.add_intent("greetings", ["hi(| {names})","hello"], True)
# container.add_entity("names", ["senthil","jarvis"], True)

# container.train()


container = FnnClassifier('intent_data/', 'intent_cache/')
container.cleanup()
container.load()
container.train()

container.add_intent(name="welcome", lines=["welcome(| back)"], reload_cache=True)
container.add_response(name="welcome", lines=["okay(| response)"])

query = None
while query != 'q':
	try:
		query = input('> ')
	except (KeyboardInterrupt, EOFError):
		print()
		break
	data = container.container.calc_intent(query)
	print(data.name + ': ' + str(data.conf))
	# print(str(data))
	for key, val in data.matches.items():
		print('\t' + key + ': ' + val)
