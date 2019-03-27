# -*- coding: utf-8 -*-
from data_clean import DataClean
import xlrd

class BaseParser:
	def __init__(self):
		self.dc = DataClean()

	def _get_user_id(self, in_file):
		user_id = in_file.split('_')[-1]
		ext_pos = user_id.find('.') + 1
		user_id = user_id[:ext_pos-1].decode('utf-8')
		return user_id

	def _get_config_row_index(self, user_id, config_sheet):
		res = 0
		for row in range(0, config_sheet.nrows):
			s = config_sheet.cell(row, 0).value
			if config_sheet.cell(row, 0).ctype == xlrd.XL_CELL_NUMBER:
				i = int(config_sheet.cell(row, 0).value)
				s = str(i)
			if s == user_id:
				res = row
				break
		return res

	def _get_unicode(self, value):
		if type(value) != type(u""):
			value = str(value)
			value = unicode(value, "utf-8")
		
		return value

	def _cleanByField(self, fieldName, fieldValue, fieldType):
		res = fieldValue
		try:
			res = self.dc.cleanByField(fieldName, fieldValue, fieldType)
		except Exception,e:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			print('fieldName:%s, fieldValue:%s, cleanError:%s' % (fieldName, fieldValue, e))
			traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
		return res