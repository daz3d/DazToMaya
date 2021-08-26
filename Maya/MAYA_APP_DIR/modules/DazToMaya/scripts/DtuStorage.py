'''
These functions have been taken from:
https://discourse.techart.online/t/maya-api-singleton-nodes/3883
With Slight Edits:
    - Changes YAML To JSON
    - Converted To Helper Class
'''

import json
import base64
from  maya.cmds import fileInfo
import itertools

class DtuStorage:
    def save(self, key, value):
        '''
        save the specified value as a base64 encoded json dunp at key 'key'
        '''
        encoded =self.encode(value)
        fileInfo(key, encoded)

    def load(self, key):
        '''
        return the value stored at 'key', or None if the value can't be found
        
        @note it is possible to store a 'None' in the value, so this doesn't prove that the key does not exist !
        '''
        answer = fileInfo(key, q=True)
        if not answer:
            return None
        return self.decode(answer[0])

    def exists(self, key):
        '''
        returns true if the specified key exists
        '''
        answer = fileInfo(key, q=True)
        return len(answer) != 0
    
    def ls(self):
        '''
        a generator that returns all of the key-value pairs in this file's fileInfo
        
        @note:  these are not decoded, because they contain a mix of native stirngs and b64 values
        '''
        all_values = fileInfo(q=True)
        keys = itertools.islice(all_values, 0, None, 2)
        values = itertools.islice(all_values, 1, None, 2)
        return itertools.izip(keys, values)


    def delete(self, key):
        '''
        remove the key and any data stored with it from this file
        '''
        fileInfo(rm=key)
        
    def decode(self, value):
        '''
        convert a base64'ed json object back into a maya object
        
        if the object is not encoded (eg, one of the default string values) return it untouched
        '''
        try:
            val = base64.b64decode(value)
            return json.loads(val)
        except TypeError:  
            return value
        
        
        
    def encode(self, value):
        '''
        return the supplied value encoded into base64-packed json dump
        '''
        return  base64.b64encode(json.dumps(value))

