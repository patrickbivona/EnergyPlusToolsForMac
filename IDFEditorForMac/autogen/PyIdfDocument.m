
#import "PyIdfDocument.h"
#import "ObjP.h"

@implementation PyIdfDocument
- (void)dealloc
{
    OBJP_LOCKGIL;
    Py_DECREF(_py);
    OBJP_UNLOCKGIL;
    [super dealloc];
}

- (PyObject *)pyRef
{
    return _py;
}


- (id)init
{
    self = [super init];
    OBJP_LOCKGIL;
    PyObject *pFunc = ObjP_findPythonClass(@"PyIdfDocument", nil);
    

    PyObject *pResult = PyObject_CallFunctionObjArgs(pFunc, NULL);

    OBJP_ERRCHECK(pResult);
    Py_DECREF(pFunc);

    _py = pResult;
    OBJP_UNLOCKGIL;
    return self;
}

- (void)addEmptyObject:(NSString *)className
{
    OBJP_LOCKGIL;
    PyObject *pFunc = PyObject_GetAttrString(_py, "addEmptyObject_");
    OBJP_ERRCHECK(pFunc);
    
    PyObject *pclassName = ObjP_str_o2p(className);
    PyObject *pResult = PyObject_CallFunctionObjArgs(pFunc, pclassName, NULL);
    Py_DECREF(pclassName);
    OBJP_ERRCHECK(pResult);
    Py_DECREF(pFunc);

    
    Py_DECREF(pResult);
    OBJP_UNLOCKGIL;

}

- (NSDictionary *)allClassesWithObjectCount
{
    OBJP_LOCKGIL;
    PyObject *pFunc = PyObject_GetAttrString(_py, "allClassesWithObjectCount");
    OBJP_ERRCHECK(pFunc);
    

    PyObject *pResult = PyObject_CallFunctionObjArgs(pFunc, NULL);

    OBJP_ERRCHECK(pResult);
    Py_DECREF(pFunc);

    
    NSDictionary * result = ObjP_dict_p2o(pResult);
    Py_DECREF(pResult);
    OBJP_UNLOCKGIL;
    return result;

}

- (NSArray *)fieldsOfClass:(NSString *)className
{
    OBJP_LOCKGIL;
    PyObject *pFunc = PyObject_GetAttrString(_py, "fieldsOfClass_");
    OBJP_ERRCHECK(pFunc);
    
    PyObject *pclassName = ObjP_str_o2p(className);
    PyObject *pResult = PyObject_CallFunctionObjArgs(pFunc, pclassName, NULL);
    Py_DECREF(pclassName);
    OBJP_ERRCHECK(pResult);
    Py_DECREF(pFunc);

    
    NSArray * result = ObjP_list_p2o(pResult);
    Py_DECREF(pResult);
    OBJP_UNLOCKGIL;
    return result;

}

- (NSArray *)objectOfClass:(NSString *)className atIndex:(NSInteger)index
{
    OBJP_LOCKGIL;
    PyObject *pFunc = PyObject_GetAttrString(_py, "objectOfClass_atIndex_");
    OBJP_ERRCHECK(pFunc);
    
    PyObject *pclassName = ObjP_str_o2p(className);
    PyObject *pindex = ObjP_int_o2p(index);
    PyObject *pResult = PyObject_CallFunctionObjArgs(pFunc, pclassName, pindex, NULL);
    Py_DECREF(pclassName);
    Py_DECREF(pindex);
    OBJP_ERRCHECK(pResult);
    Py_DECREF(pFunc);

    
    NSArray * result = ObjP_list_p2o(pResult);
    Py_DECREF(pResult);
    OBJP_UNLOCKGIL;
    return result;

}

- (NSArray *)objects
{
    OBJP_LOCKGIL;
    PyObject *pFunc = PyObject_GetAttrString(_py, "objects");
    OBJP_ERRCHECK(pFunc);
    

    PyObject *pResult = PyObject_CallFunctionObjArgs(pFunc, NULL);

    OBJP_ERRCHECK(pResult);
    Py_DECREF(pFunc);

    
    NSArray * result = ObjP_list_p2o(pResult);
    Py_DECREF(pResult);
    OBJP_UNLOCKGIL;
    return result;

}

- (NSArray *)objectsOfClass:(NSString *)className
{
    OBJP_LOCKGIL;
    PyObject *pFunc = PyObject_GetAttrString(_py, "objectsOfClass_");
    OBJP_ERRCHECK(pFunc);
    
    PyObject *pclassName = ObjP_str_o2p(className);
    PyObject *pResult = PyObject_CallFunctionObjArgs(pFunc, pclassName, NULL);
    Py_DECREF(pclassName);
    OBJP_ERRCHECK(pResult);
    Py_DECREF(pFunc);

    
    NSArray * result = ObjP_list_p2o(pResult);
    Py_DECREF(pResult);
    OBJP_UNLOCKGIL;
    return result;

}

- (NSDictionary *)onlyClassesWithObjectsWithObjectCount
{
    OBJP_LOCKGIL;
    PyObject *pFunc = PyObject_GetAttrString(_py, "onlyClassesWithObjectsWithObjectCount");
    OBJP_ERRCHECK(pFunc);
    

    PyObject *pResult = PyObject_CallFunctionObjArgs(pFunc, NULL);

    OBJP_ERRCHECK(pResult);
    Py_DECREF(pFunc);

    
    NSDictionary * result = ObjP_dict_p2o(pResult);
    Py_DECREF(pResult);
    OBJP_UNLOCKGIL;
    return result;

}

- (void)readFromFile:(NSString *)path
{
    OBJP_LOCKGIL;
    PyObject *pFunc = PyObject_GetAttrString(_py, "readFromFile_");
    OBJP_ERRCHECK(pFunc);
    
    PyObject *ppath = ObjP_str_o2p(path);
    PyObject *pResult = PyObject_CallFunctionObjArgs(pFunc, ppath, NULL);
    Py_DECREF(ppath);
    OBJP_ERRCHECK(pResult);
    Py_DECREF(pFunc);

    
    Py_DECREF(pResult);
    OBJP_UNLOCKGIL;

}

- (void)replaceObjectAtIndex:(NSInteger)index withObject:(NSArray *)obj
{
    OBJP_LOCKGIL;
    PyObject *pFunc = PyObject_GetAttrString(_py, "replaceObjectAtIndex_withObject_");
    OBJP_ERRCHECK(pFunc);
    
    PyObject *pindex = ObjP_int_o2p(index);
    PyObject *pobj = ObjP_list_o2p(obj);
    PyObject *pResult = PyObject_CallFunctionObjArgs(pFunc, pindex, pobj, NULL);
    Py_DECREF(pindex);
    Py_DECREF(pobj);
    OBJP_ERRCHECK(pResult);
    Py_DECREF(pFunc);

    
    Py_DECREF(pResult);
    OBJP_UNLOCKGIL;

}

- (void)writeToFile:(NSString *)path
{
    OBJP_LOCKGIL;
    PyObject *pFunc = PyObject_GetAttrString(_py, "writeToFile_");
    OBJP_ERRCHECK(pFunc);
    
    PyObject *ppath = ObjP_str_o2p(path);
    PyObject *pResult = PyObject_CallFunctionObjArgs(pFunc, ppath, NULL);
    Py_DECREF(ppath);
    OBJP_ERRCHECK(pResult);
    Py_DECREF(pFunc);

    
    Py_DECREF(pResult);
    OBJP_UNLOCKGIL;

}

@end
