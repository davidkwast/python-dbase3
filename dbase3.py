'''
http://ulisse.elettra.trieste.it/services/doc/dbase/DBFstruct.htm
'''

import sys
import os.path
import struct
import datetime
import decimal
import io
import tempfile

class RecordError(Exception): pass
class DeletedRecordException(RecordError): pass
class NotFoundException(RecordError): pass
class CorruptStatusFlag(RecordError): pass

class Record(object):
    def __init__(self, fields_data, raw_data, pk, db):
        self._fields_data = fields_data
        self._pk = pk
        self._db = db
        delta = 0 # status byte
        
        self._keys = []
        self._values = []
        self._items = []
        self._dict_data = {}

        for field_data in fields_data:
            length = field_data['length']
            name = field_data['name'].lower()
            data_type = field_data['type']
            data = self.parse_data( raw_data[ delta : delta+length ], data_type, name )
            
            key = name.decode(self._db.encoding) # fix python 2-> 3 str()
            setattr(self, key, data)
            
            self._keys.append(key)
            self._values.append(data)
            self._items.append((key, data))
            self._dict_data[key] = data

            delta += length
    
    def __str__(self):
        s = ''
        s += '%s: %s\n' % ('PK', self._pk)
        for field, data in [(field, getattr(self, str(field))) for field in self._db.fields]: # fix str()
            s += '%s: %s\n' % (field, data)
        return str(s)
    
    def __eq__(self, other):
        return self._pk == other._pk
    
    def __hash__(self):
        return self._pk
    
    def __repr__(self):
        return 'Record %s' % self._pk
    
    def parse_data(self, data, data_type, field_name):
        data = data.decode(self._db.encoding)
        if field_name not in self._db.dont_strip_fields:
            data = data.strip()
        try:
            if data:
                if data_type == b'N':
                    try:
                        if '.' in data:
                            #return float(s_data)
                            return decimal.Decimal(data)
                        else:
                            return int(data)
                    except (ValueError, decimal.InvalidOperation):
                        return None
                elif data_type == b'D':
                    return datetime.date(*[int(n) for n in (data[:4],data[4:6],data[6:])])
                elif data_type == b'L':
                    if data.lower() in ('t','y','1'):
                        return True
                    elif data.lower() in ('f','n','0'):
                        return False
                    else:
                        return None
                else: # C
                    return data.replace('\\','') # ???
            elif data_type == b'C':
                return ''
            else:
                return None
        except ValueError:
            return data


class DBase(object):
    '''Dbase doc'''
    
    def __init__(
        self, path_or_fd, indexes=None, encoding='ascii', dont_strip_fields=tuple(),
        cache_indexes=False, cache_indexes_path='',
    ):
        '''
        indexes: ({column: <column_name>, unique: <true_or_false>}, ...)
        '''
        
        self.encoding = encoding
        
        # File Descriptor
        if isinstance(path_or_fd, io.IOBase) or isinstance(path_or_fd, io.BufferedIOBase) or isinstance(path_or_fd, tempfile._TemporaryFileWrapper): # Windows: tempfile._TemporaryFileWrapper
            fd = path_or_fd
            fd.seek(0)
        else:
            fd = open(path_or_fd, 'rb')
        self.fd = fd
        
        
        # Attrs
        self.pk_index = set()
        self.deleted_index = set()
        self.corrupt_index = set()
        self.fields = []
        self._count = None
        
        # Header Parsing
        header = struct.unpack('<4BI2H20x', fd.read(32))
        meta = {}
        self.meta = meta
        
        # meta extras
        # meta['file_name'] = os.path.split(fd.name)[-1]
        
        # bits 0-2 indicate version number: 3 for dBASE Level 5, 4 for dBASE Level 7.
        meta['version'] = header[0] & int('00000111',2)
        
        # bit 3 indicates presence of a dBASE IV or dBASE for Windows memo file
        meta['memo_file'] = bool(header[0]>>3 & int('00000001',2))
        
        # Date of last update; in YYMMDD format.  Each byte contains the number as a binary.
        # YY is added to a base of 1900 decimal to determine the actual year.
        # Therefore, YY has possible values from 0x00-0xFF, which allows for a range from 1900-2155.
        meta['last_update'] = datetime.date(int(header[1])+1900, int(header[2]), int(header[3]))
        
        # Number of records and lengths
        meta['records'] = header[4]
        meta['header_length'] = header[5]
        meta['record_length'] = header[6]
        
        
        # Field Descriptor Array Parsing
        self.meta['fields'] = []
        self.meta['field_dict'] = {}
        
        # 0x0D stored as the Field Descriptor terminator
        while fd.read(1) != b'\x0D':
            fd.seek(fd.tell()-1)
            raw = struct.unpack('<11scI2B14x', fd.read(32))
            
            data = {}
            # field name in ASCII zero-filled
            field_name = raw[0].rstrip(b'\x00')
            data['name'] = field_name
            # field type in ASCII (C N L D or M)
            data['type'] = raw[1]
            # field data address, really necessary?
            #data['addr'] = raw[2]
            # field length in binary
            data['length'] = raw[3]
            # field decimal count in binary
            data['decimal_count'] = raw[4]
            
            if field_name not in self.meta['field_dict']:
                self.meta['fields'].append(data)
                self.meta['field_dict'][field_name] = data
        
        
        # Records begin here?
        if fd.read(1) != b'\x00':
            fd.seek(fd.tell()-1)
        # Save First Record Position
        self._first_record_pos = fd.tell()
        
        # Save Field Names
        self.fields = [field['name'].decode(self.encoding).lower() for field in self.meta['fields']]
        
        # don't strip these fields
        self.dont_strip_fields = dont_strip_fields
        
        # Indexes - last thing to do
        self.indexes = indexes
        self.indexed_columns = {}
        if indexes:
            for index in indexes:
                if index['column'] in self.fields:
                    self.indexed_columns[index['column']] = {}
            
            if cache_indexes:
                import pickle as pickle
                
                db_path = os.path.abspath(fd.name)
                cache_path = os.path.abspath(os.path.join(cache_indexes_path, os.path.basename(db_path)+'.index_cache'))
                
                mtime_db = os.path.getmtime(db_path)
                
                if os.path.exists(cache_path):
                    mtime_cache = os.path.getmtime(cache_path)
                    # carrega o cache, se as datas de modificação foram as mesmas
                    if mtime_db == mtime_cache:
                        with open(cache_path) as cache_fd:
                            loaded_index_data = pickle.load(cache_fd)
                        self.pk_index = loaded_index_data['pk_index']
                        self.indexed_columns = loaded_index_data['indexed_columns']
                        self.deleted_index = loaded_index_data['deleted_index']
                        self.corrupt_index = loaded_index_data['corrupt_index']
                    # verifica se deve apagar o cache
                    else:
                        os.remove(cache_path)
                        print('cache apagado. db_mtime %s != cache_mtime %s' % (mtime_db, mtime_cache))
                
                if not os.path.exists(cache_path):
                    self.get_or_make_indexes()
                    index_data = {
                        'indexes': self.indexes,
                        'pk_index': self.pk_index,
                        'indexed_columns': self.indexed_columns,
                        'deleted_index': self.deleted_index,
                        'corrupt_index': self.corrupt_index,
                    }
                    cache_fd = open(cache_path, 'w')
                    pickle.dump(index_data, cache_fd)
                    cache_fd.close()
                    os.utime(cache_path, (mtime_db, mtime_db))
            
            self.get_or_make_indexes()
    
    
    def _next_record_in_fd(self):
        '''get next record'''
        return self.fd.read(1), self.fd.read(self.meta['record_length']-1) # status
    
    
    def _get_record_position(self, index):
        return self._first_record_pos + index * self.meta['record_length']
    
    
    def _read_record(self, index):
        max_index = self.meta['records']
        if index > max_index:
            raise EOFError('Index in invalid range: 0 - %s' % max_index)
        self.fd.seek(self._get_record_position(index))
        status, raw_record = self._next_record_in_fd()
        if status == b' ':
            return Record(self.meta['fields'], raw_record, index, self)
        elif status == b'*':
            self.deleted_index.add(index)
            raise DeletedRecordException('Deleted record')
        else:
            self.corrupt_index.add(index)
            raise CorruptStatusFlag('Corrupt status flag in record. Index: %s' % index)
    
    
    def count(self):
        '''Returns the number or valid (non-deleted and non-corrupt) records'''
        self.get_or_make_indexes()
        return len(self.pk_index)
    
    def get_or_make_indexes(self):
        if not self.pk_index: self.make_indexes()
    
    def make_indexes(self):
        fd = self.fd
        fd.seek(self._first_record_pos)
        pk_index = self.pk_index
        for count in range(self.meta['records']):
            status, raw_record = self._next_record_in_fd()
            if status == b' ': # [0] => status
                pk_index.add(count)
                # process indexes
                if self.indexes:
                    record = Record(self.meta['fields'], raw_record, count, self)
                    for index in self.indexes:
                        key_dict = self.indexed_columns[index['column']]
                        key = getattr(record, index['column'])
                        if index['unique']:
                            key_dict[key] = count
                        else:
                            if key not in key_dict:
                                key_dict[key] = []
                            key_dict[key].append(count)
            elif status == b'*':
                self.deleted_index.add(count)
            else:
                self.corrupt_index.add(count)
                            
        return len(pk_index)
    
    
    def find(self, conditions=None):
        result_sets = []
        if conditions:
            for field, condition in conditions.items():
                result_set = set()
                if isinstance(condition, dict):
                    raise NotImplementedError('Dict conditions not suported yet')
                else:
                    if field in self.indexed_columns:
                        processed_records = False
                        keys = self.indexed_columns[field][condition]
                        if isinstance(keys, list):
                            for key in keys:
                                result_set.add(key)
                        else:
                            result_set.add(keys)
                    else:
                        processed_records = True
                        for record in self:
                            if condition == getattr(record, field):
                                result_set.add(record)
                        
                result_sets.append(result_set)
        else:
            self.get_or_make_indexes()
            result_sets.append(self.pk_index)
        if len(result_sets) > 1:
            result_set = result_sets[0]
            for _result_set in result_sets[1:]:
                result_set &= _result_set
        elif result_sets:
            result_set = result_sets[0]
        else:
            result_set = set()
        records = set()
        if not processed_records:
            for pk in result_set:
                try: records.add(self._read_record(pk))
                except IndexError as DeletedRecordException: pass
        else:
            records = result_set
        return list(records)
    
    def find_one(self, *args, **kwargs):
        try:
            return self.find(*args, **kwargs)[0]
        except IndexError as DeletedRecordException:
            return None
        
    
    def to_csv(self, path_or_fd, encoding='utf-8'):
        import csv
        if isinstance(path_or_fd, file):
            fd = path_or_fd
        else:
            fd = open(path_or_fd, 'w')
        writer = csv.writer(fd)
        writer.writerow([field.encode(encoding) for field in self.fields])
        for record in self:
            writer.writerow([('%s' % field).encode(encoding) for field in record._values])
    
    def to_sql(self, of, encoding='utf-8'):
        import codecs
        f = codecs.open(of, mode='w', encoding=encoding)
        # init
        f.write('BEGIN;')
        f.write('\n\n')
        # create table
        table_name = os.path.splitext(self.meta['file_name'])[0].lower()
        f.write('CREATE TABLE %s (' % table_name)
        f.write('\n\t''id INTEGER PRIMARY KEY')
        for name, dbase_type, length in [(x['name'],x['type'],x['length']) for x in self.meta['fields']]:
            name = name.lower()
            # convert dbase_type to sql_type
            if dbase_type == 'N':
                sql_type = 'DECIMAL(%d, %d)' % (length*2, length)
            elif dbase_type == 'C':
                sql_type = 'TEXT'
            elif dbase_type == 'D':
                sql_type = 'DATE'
            elif dbase_type == 'L':
                sql_type = 'BOOLEAN'
            else:
                sql_type = 'NUMERIC'
            # f.write(each field
            f.write(',\n\t%s %s' % (name, sql_type))
        f.write('\n);')
        f.write('\n\n')
        # insert values
        for record in self:
            values = record._values
            # convert values
            for index, value in enumerate(values):
                if value == None:
                    values[index] = 'NULL'
                elif isinstance(value, datetime.date):
                    values[index] = value.isoformat()
                elif isinstance(value, bool):
                    values[index] = str(value).lower()
                else:
                    values[index] = str(value)
            # f.write(insert
            f.write('INSERT INTO %s VALUES (' % table_name)
            f.write('%d' % record._pk)
            for value, dbase_type in zip(values, [x['type'] for x in self.meta['fields']]):
                f.write(',')
                if dbase_type == 'C':
                    f.write('"%s"' % str(value).replace('"', r'""'))
                else:
                    f.write(value)
            f.write(');\n')
        # commit
        f.write('\n')
        f.write('COMMIT;')
    
    
    def __getitem__(self, item) -> Record:
        if isinstance(item, slice):
            if not item.start: start = 0
            else: start = item.start
            if not item.stop: stop = self.meta['records']-1
            else: stop = item.stop
            if not item.step: step = 1
            else: step = item.step
            print(start, stop, step)
            return [self[i] for i in range(start, stop, step)]
        else:
            if item < 0:
                item = self.meta['records'] + item
            return self._read_record(item)
    
    def __contains__(self, item):
        self.get_or_make_indexes()
        return item in self.pk_index
    
    def __len__(self):
        if self._count == None:
            self._count = self.count()
        return self._count
    
    def __iter__(self):
        return DBaseIterator(self)


class DBaseIterator(object):
    def __init__(self, dbase):
        self.dbase = dbase
        self.index = 0
    
    def __next__(self):
        while True:
            try:
                record = self.dbase._read_record(self.index)
                self.index += 1
                return record
            except RecordError:
                self.index += 1
            except EOFError:
                raise StopIteration
    
    next = __next__


if __name__ == '__main__':
    try:
        if sys.argv[1] == 'to_csv':
            try:
                db_file = sys.argv[2]
                encoding = sys.argv[3]
                out_file = sys.argv[4]
            except IndexError:
                print('Usage: %s < db file >  < db encoding >  < out file >' % sys.argv[0])
                exit(0)
            DBase(db_file, encoding=encoding).to_csv(out_file)
        
        if sys.argv[1] == 'to_sql':
            try:
                db_file = sys.argv[2]
                encoding = sys.argv[3]
                out_file = sys.argv[4]
            except IndexError:
                print('Usage: %s < db file >  < db encoding >  < out file >' % sys.argv[0])
                exit(0)
            DBase(db_file, encoding=encoding).to_sql(out_file)
    
    except IndexError:
        print('Usage: %s [to_csv|to_sql]' % sys.argv[0])
