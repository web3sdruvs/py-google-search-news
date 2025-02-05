from openpyxl import Workbook
from datetime import datetime
import json

def save_file(data, type='json', path='../data/'):
    '''
    Save data to a file in JSON, CSV, or XLSX format.

    Parameters:
        data (list): The data to be saved.
        file_type (str): The type of file to save the data to. Default is 'json'.
            Valid options are 'json', 'csv', or 'xlsx'.
        path (str): The directory path where the file will be saved. Default is '../data/'.

    Returns:
        None

    Raises:
        ValueError: If an invalid file type is specified.
    '''
    _date_now = datetime.now().strftime("%Y%m%dT%H%M%S")
    if type == 'json':
        _save_file = open(f'{path}allnews_{_date_now}.json','w')
        json.dump(data,_save_file,indent=6)
    elif type == 'csv':
        with open(f'{path}news_{_date_now}.csv', 'w', newline='', encoding="UTF8") as _data_csv:
            for i in data:
              _data_format = str(i)
              _data_csv.write(_data_format + '\n')
    elif type == 'xlsx':
      _wb = Workbook()
      _plan = _wb.active
      _plan.append(['title','published','search','source','link','describe','url'])

      for i in data:
        _plan.append(i)

      for j in _plan.columns:
        _max_length = 0
        _column_letter = j[0].column_letter

        for cell in j:
          try:
            if len(str(cell.value)) > _max_length:
                _max_length = len(cell.value)
          except:
            pass

        _adjusted_width = (_max_length)
        _plan.column_dimensions[_column_letter].width = _adjusted_width
      _wb.save(f'{path}news_{_date_now}.xlsx')
    else:
      return