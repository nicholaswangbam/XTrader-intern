#!/usr/bin/python
# -*- coding: utf-8 -*-

#version number
version = '0.9.4dev'
import sys
import os
import argparse
#from src.xml2excel_script import xml_to_excel
#from src.dbf2excel_script import dbf_to_excel
#from src.xls2excel_script import xls_to_excel
from src.excel_parser import ExcelParser
from src.dbf_parser import DBFParser
from src.xml_parser import XMLParser

def main():
	parser = argparse.ArgumentParser(description=u'Convert file to aden templated excel(把数据文件转换成aden标准格式的Excel')
	parser.add_argument('file', nargs='?', help=u"file path name if no other args（如果没有别的参数，这是输入文件名）")
	parser.add_argument('--infile', help=u"file path name (输入文件名)")
	parser.add_argument('--version', help=u"print program version (程序版本)", action="store_true")
	parser.add_argument('--config', help=u"config excel name (模板文件名)")
	args = parser.parse_args()
	
	if len(sys.argv)==1:
		parser.print_help(sys.stderr)
		return

	#--version
	if args.version:
		print version
		return
	#--infile
	
	input_file = args.infile
	if input_file == None:
		input_file = args.file


	#--config
	config_file = args.config
	if config_file == None or config_file == '':
		config_file = "config.xlsx"
	#get file extension
	ext_pos = input_file.rfind('.') + 1
	file_ext = input_file[ext_pos:]
	
	#format output file name
	output_file = input_file[:ext_pos - 1]
	if os.sep in output_file:
		output_file = output_file.split(os.sep)[-1]
	output_file = 'out' + os.sep + output_file + '.xlsx'
	
	#check for out directory
	if not os.path.isdir('out'):
		os.mkdir('out')

	if file_ext == 'dbf':
		print "Converting DBF file..."
		#dbf_to_excel(input_file, config_file, output_file)
		p = DBFParser()
		p.parse(config_file, input_file, output_file)
	elif file_ext == 'xls' or file_ext == 'xlsx':
		print "Converting XLS file..."
		# xls_to_excel(input_file, config_file, output_file)
		p = ExcelParser()
		p.parse(config_file, input_file, output_file)
	elif file_ext == 'xml':
		print "Converting XML file..."
		#xml_to_excel(input_file, config_file, output_file)
		p = XMLParser()
		p.parse(config_file, input_file, output_file) 
	else:
		print u"File extension not supported (文件扩展名不支持)"

if __name__ == '__main__':
	main()
