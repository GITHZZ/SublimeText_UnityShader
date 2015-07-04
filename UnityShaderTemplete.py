# Text plugin Templete create By hezunzu On 2015
# 
#------------------Add
# 2015321 9:59 -- Create File, add base function
# 2015322 8:30 -- Add File Head
# 2015406 10:59 -- Can Add Body Templete
# 2015526 20:46 -- Add Change data and author
# 2015527 11:57 -- Begin to support st3
#
#------------------Fix
# 2015524 21:00 -- Fix add body templete file content have space

import sublime
import sublime_plugin

import os
import glob
import datetime
import zipfile
import getpass

PACKAGE_PATH = sublime.packages_path() #for st2

PACKAGE_NAME = 'UnityShader'
TMLP_PATH = 'templates/head/shader.tmpl'
TEMPLETE_PATH = 'templates'
TMPL_HEAD_PATH = 'templates/head'
TMPL_BODY_PATH = 'templates/body' 
LANGUAGE_PATH = 'Packages/UnityShader/UnityShader.tmLanguage'

IS_ST3_VERSION = int(sublime.version()[0]) >= 3

class UnityShaderTempleteCreateCommand(sublime_plugin.TextCommand):
	def run(self, edit, fileName):
		view = self.view
		self.fileName = fileName
		self.tab = self.create_tab(view, fileName)

		code = self.get_head_code()
		body_code = self.get_body_code()

		self.set_syntax()
		self.set_templete_code(code, True)
		self.set_templete_code(body_code, False)

	def get_setting(self):
		settings = sublime.load_settings(PACKAGE_NAME + '.sublime-settings')
		return settings

	def create_tab(self, view, fileName):
		win = view.window()
		tab = win.new_file()
		tab.set_name(fileName)
		return tab

	def set_syntax(self):
		v = self.tab
		path = LANGUAGE_PATH
		v.set_syntax_file(path)

	def read_content_from_file(self, path, mode = 'r'):
		fp = open(path, mode)
		code = fp.read()
		fp.close()
		return code
	
	def decode_code(self, code):
		settings = self.get_setting()
		format = settings.get('date_format')
		data = datetime.datetime.now().strftime(format)

		if not IS_ST3_VERSION:
			code = code.decode('utf8') #for chinese in st2

		code = code.replace('${date}', data)
		code = code.replace('${time}', data)
		code = code.replace('${author}', getpass.getuser())
		code = code.replace('${name}', getpass.getuser())
		code = code.replace('${shader_name}', self.fileName)

		return code

	def get_head_code(self):
		code = ''
		file_name = 'shader.tmpl'
		isError = False

		if IS_ST3_VERSION:
			tmpl_dir = 'Packages/' + PACKAGE_NAME + '/' + TMPL_HEAD_PATH + '/'
		else:
			tmpl_dir = os.path.join(PACKAGE_PATH, PACKAGE_NAME, TMPL_HEAD_PATH)

		self.tmpl_path = os.path.join(tmpl_dir, file_name)

		if IS_ST3_VERSION:
			try:
				code = sublime.load_resource(self.tmpl_path)
			except IOError:
				isError = True 
		else:
			if os.path.isfile(self.tmpl_path):
				code = self.read_content_from_file(self.tmpl_path)
			else:
				isError = true 

		if isError:
			sublime.message_dialog('[decode_head_code error] No Find templete file')

		return self.decode_code(code)

	def get_body_code(self):
		code = ''

		file_name = ''
		isError = False

		settings = self.get_setting()
		templete_body_file = settings.get('templete_body_file', {})
		file_name = templete_body_file.get('basic')

		if IS_ST3_VERSION:
			tmpl_dir = 'Packages/' + PACKAGE_NAME + '/' + TMPL_BODY_PATH + '/'
		else:
			tmpl_dir = os.path.join(PACKAGE_PATH, PACKAGE_NAME, TMPL_BODY_PATH)

		self.tmpl_path = os.path.join(tmpl_dir, file_name)

		if IS_ST3_VERSION:
			try:
				code = sublime.load_resource(self.tmpl_path)
			except IOError:
				isError = True 
		else:
			if os.path.isfile(self.tmpl_path):
				code = self.read_content_from_file(self.tmpl_path)
			else:
				isError = True 
		if isError:
			sublime.message_dialog('[decode_head_code error] No Find templete file')

		return self.decode_code(code)

	def set_templete_code(self, code, isHead):
		tab = self.tab
		if isHead == False:
			tab.run_command('insert', {'characters': '\n\n'})
		
		tab.run_command("insert_snippet", {'contents': code})

class UnityShaderTempleteInputClassNameCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.window.show_input_panel('Input File Name', '',
            self.on_done, self.on_change, self.on_cancel)
	def on_done(self, input):
		self.window.run_command('unity_shader_templete_create', {"fileName" : input})
	def on_change(self, input):
		pass
	def on_cancel(self):
		pass

class UnityShaderTempleteHeadReplaceCommand(sublime_plugin.TextCommand):
	def run(self, edit, a, b, strings):
		region = sublime.Region(int(a), int(b))
		self.view.replace(edit, region, strings)

class UnityShaderTempleteListener(sublime_plugin.EventListener):
	def get_setting(self):
		settings = sublime.load_settings(PACKAGE_NAME + '.sublime-settings')
		return settings

	def get_change_time(self):
		settings = self.get_setting()
		format = settings.get('date_format')
		date = datetime.datetime.now().strftime(format)
		return date

	def read_content_from_file(self, path, mode = 'r'):
		fp = open(path, mode)
		code = fp.read()
		fp.close()
		return code
	
	def on_pre_save(self, view):
		fileContent = self.read_content_from_file(view.file_name())
		lines = fileContent.split('\n') 

		start_index = -1
		end_index = -1
		for line in lines:
			# print(len(line))
			typeIndex = line.find(':')
			lineType = line[0:typeIndex]
			# print(lineType)

			if lineType == '// @Last change by':
				end_index = start_index + len(line) + 1
				
				#get time
				settings = self.get_setting()
				format = settings.get('date_format')
				data = datetime.datetime.now().strftime(format)

				#get user
				user = getpass.getuser()

				desc = '// @Last change by:' +  user + ' on ' + data
				view.run_command('unity_shader_templete_head_replace', {'a': start_index + 1, 'b': end_index, 'strings': desc})
				break
			else:
				lineLen = len(line) + 1
				start_index = start_index + lineLen 


		# 	search = regex.search(line)
		# 	if search is not None:
		# 		var = search.group()
  #               index = line.find(var)

  #               for i in range(index - 1, 0, -1):
  #                   if line[i] != ' ':
  #                       space_start = i + 1
  #                       print(space_start)
  #                       break
                        
			# typeIndex = line.find(':')
			# lineType = line[0:typeIndex]
			# print(line)
			# line.replace('// @Last change by:*apple on *2015-06-07 18:24:23', '123')

		# lastChangeStr = lines[3]
		# changeTimeIndex = lastChangeStr.index('*')
		# test = lastChangeStr.replace('Last', '122')
		# print(lastChangeStr)
		# print(test)

		# view.run_command('unity_shader_templete_head_replace', {'a': 18, 'b': 20, 'strings': '123'})

	def on_post_save(self, view):
		pass