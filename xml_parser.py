# -*- coding: utf-8 -*-
#用python把xml转换成aden标准格式的Excel
from lxml import etree
import data_clean
import traceback
import sys
import xlsxwriter
import time
from base_parser import BaseParser
import xlrd

KEY_SPLIT = {
	"ZZ":7,"ZZ_JBBM":7,"ZZ_RYBQ":7,"ZZ_CYBQ":7,
	"QTZD":15,"JBDM":15,"RYBQ":15,"CYQK":15,
	"SSJCZBM":7,"SSJCZRQ":7,"SSJB":7,"SSJCZMC":7,"SZ":7,"YZ":7,"EZ":7,"QKDJ":7,"QKYHLB":7,"MZFS":7,"MZYS":7
}

class ConfigFieldObj:
	def __init__(self, fieldName, needSplit, splitCount):
		self.fieldName = fieldName 		#底表的字段名(英文的)
		self.needSplit = needSplit 		#该字段是否要做切分
		self.splitCount = splitCount

class XMLParser(BaseParser):
	def __init__(self):
		BaseParser.__init__(self)

	#根据底表字段提取字段后面的数字，主要取最后一位数字，因为一般不会把split的写到带有两位数字的字段底下，这算是个坑...
	def _getBackendNumByField(self, fieldName):
		s = fieldName[-1]
		i = 0
		try:
			i = int(s)
		except:
			pass

		return i

	def _initParse(self, config_file, in_file):
		self.user_id = self._get_user_id(in_file)
		config_book = xlrd.open_workbook(config_file)
		self.config_sheet = config_book.sheet_by_index(0)
		config_row_index = self._get_config_row_index(self.user_id, self.config_sheet)
		if config_row_index == 0:
			return False, u"XML file doesn't exist in template excel (XLS在模板excel user_id:%s不存在)" % self.user_id

		try:
			with open(in_file, 'r') as file:
				self.in_xml = etree.fromstring(file.read())
		except IOError as e:
			print(u"Unable to find or open input file(文件不存在)")
			return

		self.config_fields_map = {}	#保存底表字段及索引
		self.config_fields_list = []	#底表字段数组
		self.fields_map_rev = {}
		for col in range(2, self.config_sheet.ncols):
			self.config_fields_map[self.config_sheet.cell(1, col).value] = col - 2
			self.config_fields_list.append(self.config_sheet.cell(1, col).value)
			data_field = self._get_unicode(self.config_sheet.cell(config_row_index, col).value)
			config_field = self.config_sheet.cell(1, col).value
			if data_field != None and data_field != '':
				data_field_obj = ConfigFieldObj(data_field, False, 0)
				if KEY_SPLIT.has_key(config_field[0:len(config_field) - 1]):
					data_field_obj.needSplit = True
					data_field_obj.splitCount = KEY_SPLIT[config_field[0:len(config_field) - 1]]
				self.fields_map_rev[config_field] = data_field_obj
		return True, ''

	def parse(self, config_file, in_file, out_file):
		start_time = time.time()
		res, msg = self._initParse(config_file, in_file)

		if not res:
			print msg
			return
		
		wb_new = xlsxwriter.Workbook(out_file)
		out_sheet = wb_new.add_worksheet()

		print "%s seconds to load file:%s" % (time.time() - start_time, in_file)

		#写入表头，底表所有字段都写入
		out_sheet.write_row(0, 0, self.config_fields_list)

		
		for row, case in enumerate(self.in_xml.findall('CASE'), 1):
			row_data = ['']*len(self.config_fields_list)
			for num, key in enumerate(self.config_fields_list):
				if self.fields_map_rev.has_key(key):
					obj = self.fields_map_rev[key]
					excess_data = ''
					for iteration, found in enumerate(case.iter(obj.fieldName), 1):
						data_field_val = self._get_unicode(found.text)
						data_field_val = self._cleanByField(key, data_field_val, 'xml')
						if iteration == 1:
							row_data[self.config_fields_map[self.config_fields_list[num]]] = data_field_val
						if obj.needSplit:
							tmp_field_name = key[0: len(key) - 1]
							if iteration < obj.splitCount:
								tmp_field_name = tmp_field_name + str(iteration)
								data_field_val = found.text
							else:
								tmp_field_name = tmp_field_name + str(obj.splitCount)
								excess_data+=str(found.text)
								excess_data+='/'
								data_field_val = excess_data[0:len(excess_data)-1]
							
							row_data[self.config_fields_map[tmp_field_name]] = data_field_val
			out_sheet.write_row(row, 0, row_data)
			if row % 100 == 0:
				print '.',
				sys.stdout.flush()
		wb_new.close()
		print "Finished."
		print "%s seconds to parse all data" % (time.time() - start_time)







