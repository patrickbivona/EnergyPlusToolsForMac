
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

- (NSDictionary *)classesWithObjectCount
{
    OBJP_LOCKGIL;
    PyObject *pFunc = PyObject_GetAttrString(_py, "classesWithObjectCount");
    OBJP_ERRCHECK(pFunc);
    

    PyObject *pResult = PyObject_CallFunctionObjArgs(pFunc, NULL);

    OBJP_ERRCHECK(pResult);
    Py_DECREF(pFunc);

    
    NSDictionary * result = ObjP_dict_p2o(pResult);
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
