from pymilvus import connections, FieldSchema, CollectionSchema, Collection, utility
from typing import Dict, List, Optional, Union
class mivils():
    def __init__(self,host,port):
        MILVUS_HOST = host
        MILVUS_PORT = port
        connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
        self.collection = None

    def create_collection(self,name,fields:list[FieldSchema],description=None,index_params:dict=None):
        if utility.has_collection(name):
            utility.drop_collection(name)
        Collection_Schema = CollectionSchema(fields=fields, description=description)
        self.collection = Collection(name=name, schema=Collection_Schema)
        if index_params:
            index = [value for value in index_params.keys() if 'index_name' in value.lower()]
            if len(index) == 0:
                raise Exception('`index_name` is needed when index_params is provided')
            index_name = index_params.pop(index[0])
            self.collection.create_index(field_name=index_name,index_params=index_params)

    def connect_to_collection(self,name:str):
        self.collection = Collection(name=name)
        self.collection.load()
    
    def Insert(self,data:list[list]):
        self.collection.insert(data)
    
    def fieldschema(self,name: str, dtype: str|int, description: str = "", **kwargs):
        '''
        dtype:\n
            NONE <--> 0\n
            BOOL <--> 1\n
            INT8 <--> 2\n
            INT16 <--> 3\n
            INT32 <--> 4\n
            INT64 <--> 5\n
            FLOAT <--> 10\n
            DOUBLE <--> 11\n
            STRING <--> 20\n
            VARCHAR <--> 21\n
            JSON <--> 23\n
            BINARY_VECTOR <--> 100\n
            FLOAT_VECTOR <--> 101\n
            UNKNOWN <--> 999
        '''
        dty = {"NONE":0,"BOOL":1,"INT8":2,"INT16":3,"INT32":4,"INT64":5,"FLOAT":10,"DOUBLE":11,"STRING":20,"VARCHAR":21,"JSON":23,"BINARY_VECTOR":100,"FLOAT_VECTOR":101,"UNKNOWN":999}
        if isinstance(dtype,str):
            dtype = dty[dtype.upper()]
        return FieldSchema(name, dtype, description,**kwargs)

    def Query(self,
        expr: str,
        output_fields: Optional[List[str]] = None,
        partition_names: Optional[List[str]] = None,
        timeout: Optional[float] = None,
        **kwargs,):
        return self.collection.query(expr,output_fields,partition_names,timeout,**kwargs)
    
    def Search(self,
        data: List,
        anns_field: str,
        param: Dict,
        limit: int,
        expr: Optional[str] = None,
        partition_names: Optional[List[str]] = None,
        output_fields: Optional[List[str]] = None,
        timeout: Optional[float] = None,
        round_decimal: int = -1,
        **kwargs,):
        return self.collection.search(data,anns_field,param,limit,expr,partition_names,output_fields,timeout,round_decimal,**kwargs)