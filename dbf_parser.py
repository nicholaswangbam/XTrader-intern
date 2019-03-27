# -*- coding: utf-8 -*-
#用python把dbf转换成aden标准格式的Excel
from dbfread import DBF, FieldParser, InvalidValue
from base_parser import BaseParser
import time
import sys
import traceback
import xlsxwriter
import xlrd

class DBFParser(BaseParser):
	def __init(self):
		BaseParser.__init__(self)

	def _initParse(self, config_file, in_file):
		self.user_id = self._get_user_id(in_file)
		config_book = xlrd.open_workbook(config_file)
		self.config_sheet = config_book.sheet_by_index(0)
		config_row_index = self._get_config_row_index(self.user_id,self.config_sheet)
		if config_row_index == 0:
			return False, u"DBF file doesn't exist in template excel (XLS在模板excel user_id:%s不存在)" % self.user_id

		#class to ignore badly formatted dbfs
		class MyFieldParser(FieldParser):
			def parse(self, field, data):
				try:
					return FieldParser.parse(self, field, data)
				except ValueError:
					return InvalidValue(data)

		try:
			self.in_dbf = DBF(in_file, encoding = 'GBK', parserclass=MyFieldParser)
		except IOError as e:
			print(u"Unable to find or open input file (文件不存在)")
			return

			

		#遍历配置文件对应行的所有列，构造字段对应关系
		self.config_fields_map = {}	#保存底表字段及索引
		self.config_fields_list = []	#底表字段数组
		self.fields_map_rev = {}
		for col in range(2, self.config_sheet.ncols):
			self.config_fields_map[self.config_sheet.cell(1, col).value] = col - 2
			self.config_fields_list.append(self.config_sheet.cell(1, col).value)
			data_field = self._get_unicode(self.config_sheet.cell(config_row_index, col).value)
			config_field = self.config_sheet.cell(1, col).value
			if data_field != None and data_field != '':
				self.fields_map_rev[config_field] = data_field
		return True, ''

	def parse(self, config_file, in_file, out_file):
		start_time = time.time()
		res, msg = self._initParse(config_file, in_file)

		if not res:
			print msg
			return

		wb_new = xlsxwriter.Workbook(out_file)
		out_sheet = wb_new.add_worksheet()

		print "%s seconds to load file:%s." % (time.time() - start_time, in_file)

		#写入表头，底表所有字段都写入
		out_sheet.write_row(0, 0, self.config_fields_list)

		for row, record in enumerate(self.in_dbf):
			row_data = ['']*len(self.config_fields_list)
			empty = 0
			for num, key in enumerate(self.config_fields_list):
				if self.fields_map_rev.has_key(key):
					if self.fields_map_rev[key] in record:
						data_field_val = self._get_unicode(record[self.fields_map_rev[key]])
						if data_field_val != '' and data_field_val != None and data_field_val != "None":
							data_field_val = self._cleanByField(key, data_field_val, 'dbf')
						else:
							empty += 1
							data_field_val = self._cleanByField(key, '', 'dbf')
						row_data[self.config_fields_map[self.config_fields_list[num]]] = data_field_val
					else:
						empty += 1
			if empty == len(self.config_fields_list):
				break

			out_sheet.write_row(row + 1, 0, row_data)

			if row % 100 == 0:
				print '.',
				sys.stdout.flush()
		wb_new.close()
		print "Finished."
		print "%s seconds to parse all data" % (time.time() - start_time)




