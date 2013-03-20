
#import "PyIdfFileIO.h"
#import "ObjP.h"

@implementation PyIdfFileIO
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
    PyObject *pFunc = ObjP_findPythonClass(@"PyIdfFileIO", nil);
    

    PyObject *pResult = PyObject_CallFunctionObjArgs(pFunc, NULL);

    OBJP_ERRCHECK(pResult);
    Py_DECREF(pFunc);

    _py = pResult;
    OBJP_UNLOCKGIL;
    return self;
}

- (NSArray *)readEplusObjectsFromFile:(NSString *)path
{
    OBJP_LOCKGIL;
    PyObject *pFunc = PyObject_GetAttrString(_py, "readEplusObjectsFromFile_");
    OBJP_ERRCHECK(pFunc);
    
    PyObject *ppath = ObjP_str_o2p(path);
    PyObject *pResult = PyObject_CallFunctionObjArgs(pFunc, ppath, NULL);
    Py_DECREF(ppath);
    OBJP_ERRCHECK(pResult);
    Py_DECREF(pFunc);

    
    NSArray * result = ObjP_list_p2o(pResult);
    Py_DECREF(pResult);
    OBJP_UNLOCKGIL;
    return result;

}

@end
