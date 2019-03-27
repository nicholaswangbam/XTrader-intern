# -*- coding: utf-8 -*-
#用python把xls转换成aden标准格式的Excel
import time
from base_parser import BaseParser
import traceback
import sys
import time
import xlsxwriter
import datetime
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
		self.splitStr = ','

class ExcelParser(BaseParser):

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

	#处理其他诊断、其他手术（包括编码、名称等信息）里第一个如果跟主诊断或主手术相同则移除掉的问题
	def _removeRepeatData(self, fieldName, ls, row_data):
		compare_map = {
			#其他诊断与主诊断对比关系
			"QTZD":"ZYZD", "JBDM":"JBDM", "RYBQ":"RYBQ", "CYQK":"CYQK",		
			#手术与主手术对比关系
			"SSJCZBM":"SSJCZBM1", "SSJCZRQ":"SSJCZRQ1", "SSJB":"SSJB1", 
			"SSJCZMC":"SSJCZMC1", "SZ":"SZ1", "YZ":"YZ1", "EZ":"EZ1", 
			"QKDJ":"QKDJ1", "QKYHLB":"QKYHLB1", "MZFS":"MZFS1", "MZYS":"MZYS1"
		}
		res = ls
		if compare_map.has_key(fieldName):
			source = ls[0]
			target = row_data[self.config_fields_map[compare_map[fieldName]]]
			# print('source:%s, target:%s' % (source, target))
			if len(target) > 0:
				if source[0] == '0' and target[0] != '0':	#处理编码类字段，主编码的第一个0会被Excel去掉的问题
					target = '0' + target
			if source == target:
				res = ls[1:len(ls)]

		return res

	def _checkExcelDate(self, row, col, data_field_val):
		if self.in_sheet.cell(row, col).ctype == xlrd.XL_CELL_DATE:
			i = self.in_sheet.cell(row, col).value
 			i = int(i)
 			data_field_val = str(i)
			try:
				data_field_val = xlrd.xldate.xldate_as_datetime(self.in_sheet.cell(row, col).value, 0)
				data_field_val = self._get_unicode(data_field_val)
			except Exception, e:
				data_field_val = '1900-01-01'

		return data_field_val



	def _initParse(self, config_file, in_file):
		self.user_id = self._get_user_id(in_file)
		config_book = xlrd.open_workbook(config_file)
		self.config_sheet = config_book.sheet_by_index(0)
		self.config_row_index = self._get_config_row_index(self.user_id, self.config_sheet)
		if self.config_row_index == 0:
			return False, u"XLS file doesn't exist in template excel (XLS在模板excel user_id:%s不存在)" % self.user_id

		in_book = xlrd.open_workbook(in_file)
		self.in_sheet = in_book.sheet_by_index(0)
		

		#遍历配置文件对应行的所有列，构造字段对应关系
		self.config_fields_map = {}	#保存底表字段及索引
		self.config_fields_list = []	#底表字段数组
		self.fields_map = {}
		for col in range(2, self.config_sheet.ncols):
			self.config_fields_map[self.config_sheet.cell(1, col).value] = col - 2
			self.config_fields_list.append(self.config_sheet.cell(1, col).value)

			data_field = self._get_unicode(self.config_sheet.cell(self.config_row_index, col).value)
			data_field = data_field.upper()			#这里也转成大写吧，万一他们写成小写了。。。
			config_field = self.config_sheet.cell(1, col).value
			if data_field != None and data_field != '':
				config_field_obj = ConfigFieldObj(config_field, False, 0)
				if data_field.find("|SPLIT|") != -1:
					ls = data_field.split('|')
					data_field = self._get_unicode(ls[0])
					config_field_obj.needSplit = True
					config_field_obj.splitStr = ls[2]
					config_field_obj.splitCount = KEY_SPLIT[config_field[0:len(config_field)-1]]

				self.fields_map[data_field] = config_field_obj
	
		if self.config_sheet.cell(self.config_row_index, 1).value == 'xls_row_col':
			return False, 'xls_row_col'

		return True, ''

	def parse(self, config_file, in_file, out_file):
		start_time = time.time()
		res, msg = self._initParse(config_file, in_file)

		if not res:
			if msg == u'xls_row_col':
				print "%s seconds to load file:%s" % (time.time() - start_time, in_file)
				self.xls_row_col_parse(in_file, out_file)
			else:
				print msg
			return
		
		wb_new = xlsxwriter.Workbook(out_file)
		out_sheet = wb_new.add_worksheet()

		print "%s seconds to load file:%s" % (time.time() - start_time, in_file)

		#写入表头，底表所有字段都写入
		out_sheet.write_row(0, 0, self.config_fields_list)

		#开始遍历输入的文件，按行处理并写入到输出文件里
		process_row_count = 0
		for row in range(1, self.in_sheet.nrows):
			row_data = ['']*len(self.config_fields_list)
			process_row_count += 1
			for col in range(0, self.in_sheet.ncols):
				data_field_name = self._get_unicode(self.in_sheet.cell(0, col).value)
				data_field_name = data_field_name.upper()		#有些表头可能是小写的，所以直接转成大写再比较
				if self.fields_map.has_key(data_field_name):		#只有在对应关系里能找到的列才处理
					obj = self.fields_map[data_field_name]
					
					data_field_val = self._get_unicode(self.in_sheet.cell(row, col).value)
					data_field_val = self._checkExcelDate(row, col, data_field_val)
					
					if not obj.needSplit:
						data_field_val = self.dc.cleanByField(obj.fieldName, data_field_val, 'xls')
						row_data[self.config_fields_map[obj.fieldName]] = data_field_val
					else:
						if data_field_val != None and data_field_val != '':
							ls = data_field_val.split(obj.splitStr)
							tmp_field_val = ''
							num = self._getBackendNumByField(obj.fieldName)
							tmp_field_name = obj.fieldName[0:len(obj.fieldName)-1]

							ls = self._removeRepeatData(tmp_field_name, ls, row_data)

							for i in range(0, len(ls)):
								if i < obj.splitCount - num:
									tmp_field_name = obj.fieldName[0:len(obj.fieldName)-1]
									tmp_field_name = '%s%d' % (tmp_field_name, num + i)
									# if obj.fieldName.find('SSJCZMC') != -1:
									# 	print('xxx row:%d, name:%s, val:%s' % (row, tmp_field_name, ls[i]))
									row_data[self.config_fields_map[tmp_field_name]] = self._cleanByField(tmp_field_name, ls[i], 'xls')
								else:
									tmp_field_name = obj.fieldName[0:len(obj.fieldName)-1]
									tmp_field_name = '%s%d' % (tmp_field_name, obj.splitCount)
									tmp_field_val = tmp_field_val + ls[i] + '/'
									# if obj.fieldName.find('SSJCZMC') != -1:
									# 	print('row:%d, name:%s, val:%s' % (row, tmp_field_name, tmp_field_val))
									row_data[self.config_fields_map[tmp_field_name]] = self._cleanByField(tmp_field_name, tmp_field_val[0:len(tmp_field_val)-1], 'xls')
				else:
					pass
					# print 'column:%s not found in config excel.' % data_field_name

			out_sheet.write_row(row, 0, row_data)
			if process_row_count % 100 == 0:
				print '.',
				sys.stdout.flush()

		wb_new.close()
		print 'Finished.'
		print "%s seconds to parse all data." % (time.time() - start_time)

	def xls_row_col_parse(self, in_file, out_file):
		start_time = time.time()
		wb_new = xlsxwriter.Workbook(out_file)
		out_sheet = wb_new.add_worksheet()

		#写入表头，底表所有字段都写入
		out_sheet.write_row(0, 0, self.config_fields_list)

		#用check_same_map的key来判断两行是相同的
		check_same_map = {'BAH':None, 'RYSJ':None, 'CYSJ':None, 'ZYCS':None, 'ZFY':None}
		#check_same_map的key在in_file的列
		check_same_col_map = {}
		
		#find corresponding column number and make map for KEY_SPLIT
		#KEY_SPLIT的key在in_file的列
		repeat_config_key_col_map = {}
		#数key已经有几次重复了
		repeat_config_key_count_map = {}
		for col in range(0, self.in_sheet.ncols):
			data_field_name = self.in_sheet.cell(0, col).value
			if self.fields_map.has_key(data_field_name):
				config_field_name = self.fields_map[data_field_name].fieldName
				if check_same_map.has_key(config_field_name):
					check_same_col_map[config_field_name] = col
				elif KEY_SPLIT.has_key(config_field_name[0:-1]):
					if self._getBackendNumByField(config_field_name) != 0:
						config_field_name = config_field_name[0:-1]
					repeat_config_key_col_map[config_field_name] = col
					repeat_config_key_count_map[config_field_name] = 1


		#开始遍历输入的文件，按行处理并写入到输出文件里
		out_row_count = 0 #输出的行数跟输入的行数不一样
		row_data = ['']*len(self.config_fields_list)
		for row in range(1, self.in_sheet.nrows):
			#先判断这行跟前一行是是否同一个case
			for key in check_same_map.keys():
				if check_same_map[key] == self._get_unicode(self.in_sheet.cell(row, check_same_col_map[key]).value):
					same_as_prev_row = True
				else:
					#如果不是第一行之前，把row_data输入到excel里面
					if out_row_count != 0:
						out_sheet.write_row(out_row_count, 0, row_data)
					
					#reset
					row_data = ['']*len(self.config_fields_list)
					for key in repeat_config_key_count_map.keys():
						repeat_config_key_count_map[key] = 1
					
					out_row_count += 1
					same_as_prev_row = False

					break

			if not same_as_prev_row:
				#先把新的Case放在map里面
				for key in check_same_map.keys():
					data_field_val = self._get_unicode(self.in_sheet.cell(row, check_same_col_map[key]).value)
					check_same_map[key] = data_field_val

				#新的Case要把每一列都加进row_data
				for col in range(0, self.in_sheet.ncols):
					data_field_name = self._get_unicode(self.in_sheet.cell(0, col).value)
					data_field_name = data_field_name.upper()		#有些表头可能是小写的，所以直接转成大写再比较
					if self.fields_map.has_key(data_field_name):		#只有在对应关系里能找到的列才处理
						obj = self.fields_map[data_field_name]						
						data_field_val = self._get_unicode(self.in_sheet.cell(row, col).value)
						data_field_val = self._checkExcelDate(row, col, data_field_val)
						data_field_val = self._cleanByField(obj.fieldName, data_field_val, 'xls')
						row_data[self.config_fields_map[obj.fieldName]] = data_field_val
						
						len_of_num = len(str(self._getBackendNumByField(obj.fieldName)))
						if repeat_config_key_count_map.has_key(obj.fieldName[0:(len_of_num * -1)]):
							if data_field_val != '' and data_field_val != None:
								repeat_config_key_count_map[obj.fieldName[0:(len_of_num * -1)]] += 1
			else:
				#重复的data都跳过去，只看KEY_SPLIT里面key的data
				for a,key in enumerate(repeat_config_key_col_map, 1):
					data_field_name = self._get_unicode(self.in_sheet.cell(0, col).value)
					data_field_name = data_field_name.upper()		#有些表头可能是小写的，所以直接转成大写再比较					
					if self.fields_map.has_key(data_field_name):		#只有在对应关系里能找到的列才处理
						obj = self.fields_map[data_field_name]
						data_field_val = self._get_unicode(self.in_sheet.cell(row, repeat_config_key_col_map[key]).value)
						data_field_val = self._checkExcelDate(row, repeat_config_key_col_map[key], data_field_val)
						data_field_val = self._cleanByField(self.config_fields_map[key + str(repeat_config_key_count_map[key])], data_field_val, 'xls')
						#把data写在config1, 2, 3...里面
						if data_field_val != '' and data_field_val != None:
							if repeat_config_key_count_map[key] != KEY_SPLIT[key]:
								row_data[self.config_fields_map[key + str(repeat_config_key_count_map[key])]] = data_field_val
								
								repeat_config_key_count_map[key] += 1
							else:
								if row_data[self.config_fields_map[key + str(repeat_config_key_count_map[key])]] != '':
									data_field_val = '/' + data_field_val
								row_data[self.config_fields_map[key + str(repeat_config_key_count_map[key])]] += data_field_val
			if out_row_count % 100 == 0:
				print '.',
				sys.stdout.flush()
				
		out_sheet.write_row(row, 0, row_data) #最后一行还要写进去
		wb_new.close()
		print 'Finished.'
		print "%s seconds to parse all data." % (time.time() - start_time)




if __name__ == '__main__':
	p = ExcelParser()
	p.parse('../config.xlsx', '../in/医院数据/广东/a_b_guangdongrm.xls', '../out/tmp.xlsx')





