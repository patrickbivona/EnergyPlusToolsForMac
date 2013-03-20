#import "ObjP.h"

/* Returns the python class `className` in `inModule`.

   If inModule is nil, look for class in __main__.
*/
PyObject* ObjP_findPythonClass(NSString *className, NSString *inModule)
{
    PyObject *pModule, *pClass;
    OBJP_LOCKGIL;
    if (inModule == nil) {
        pModule = PyImport_AddModule("__main__");
    }
    else {
        pModule = PyImport_ImportModule([inModule UTF8String]);
    }
    OBJP_ERRCHECK(pModule);
    pClass = PyObject_GetAttrString(pModule, [className UTF8String]);
    OBJP_ERRCHECK(pClass);
    if (inModule != nil) {
        Py_DECREF(pModule);
    }
    OBJP_UNLOCKGIL;
    return pClass;
}

/* Return a class `className` instantiated with `ref` as a reference objc class.

   `ref` will *not* be retained by the python class.
*/
PyObject* ObjP_classInstanceWithRef(NSString *className, NSString *inModule, id ref)
{
    PyObject *pClass, *pRefCapsule, *pResult;
    pClass = ObjP_findPythonClass(className, inModule);
    OBJP_LOCKGIL;
    pRefCapsule = PyCapsule_New(ref, NULL, NULL);
    OBJP_ERRCHECK(pRefCapsule);
    pResult = PyObject_CallFunctionObjArgs(pClass, pRefCapsule, Py_False, NULL);
    OBJP_ERRCHECK(pResult);
    Py_DECREF(pClass);
    Py_DECREF(pRefCapsule);
    OBJP_UNLOCKGIL;
    return pResult;
}

void ObjP_raisePyExceptionInCocoa(PyGILState_STATE gilState)
{
    PyObject *pExcType, *pExcValue, *pExcTraceback;
    PyErr_Fetch(&pExcType, &pExcValue, &pExcTraceback);
    if (pExcType == NULL) {
        NSLog(@"ObjP_raisePyExceptionInCocoa() called with no exception set.");
        return;
    }
    PyErr_NormalizeException(&pExcType, &pExcValue, &pExcTraceback);
    PyObject *pErrType = PyObject_Str(pExcType);
    PyObject *pErrMsg = PyObject_Str(pExcValue);
    NSString *errType = ObjP_str_p2o(pErrType);
    NSString *errMsg = ObjP_str_p2o(pErrMsg);
    NSString *reason = [NSString stringWithFormat:@"%@: %@", errType, errMsg];
    NSException *exc = [NSException exceptionWithName:@"PythonException" reason:reason userInfo:nil];
    Py_DECREF(pErrType);
    Py_DECREF(pErrMsg);
    // PyErr_Fetch cleared the exception so we have to restore it if we want to print it. This call
    // Also steals reference to its arguments.
    PyErr_Restore(pExcType, pExcValue, pExcTraceback);
    // This will print the exception and, more importantly, call sys.excepthook.
    PyErr_Print();
    OBJP_UNLOCKGIL;
    @throw exc;
}

NSString* ObjP_str_p2o(PyObject *pStr)
{
    if (pStr == Py_None) {
        return nil;
    }
    OBJP_LOCKGIL;
    PyObject *pBytes = PyUnicode_AsUTF8String(pStr);
    OBJP_ERRCHECK(pBytes);
    char *utf8Bytes = PyBytes_AS_STRING(pBytes);
    NSString *result = [NSString stringWithUTF8String:utf8Bytes];
    Py_DECREF(pBytes);
    OBJP_UNLOCKGIL;
    return result;
}

PyObject* ObjP_str_o2p(NSString *str)
{
    OBJP_LOCKGIL;
    PyObject *pResult;
    if (str != nil) {
        pResult = PyUnicode_FromString([str UTF8String]);
        OBJP_ERRCHECK(pResult);
    }
    else {
        pResult = Py_None;
        Py_INCREF(pResult);
    }
    OBJP_UNLOCKGIL;
    return pResult;
}

NSInteger ObjP_int_p2o(PyObject *pInt)
{
    OBJP_LOCKGIL;
    NSInteger result = PyLong_AsLong(pInt);
    OBJP_UNLOCKGIL;
    return result;
}

PyObject* ObjP_int_o2p(NSInteger i)
{
    OBJP_LOCKGIL;
    PyObject *pResult = PyLong_FromLong(i);
    OBJP_ERRCHECK(pResult);
    OBJP_UNLOCKGIL;
    return pResult;
}

CGFloat ObjP_float_p2o(PyObject *pFloat)
{
    OBJP_LOCKGIL;
    CGFloat result = PyFloat_AsDouble(pFloat);
    OBJP_UNLOCKGIL;
    return result;
}

PyObject* ObjP_float_o2p(CGFloat f)
{
    OBJP_LOCKGIL;
    PyObject *pResult = PyFloat_FromDouble(f);
    OBJP_ERRCHECK(pResult);
    OBJP_UNLOCKGIL;
    return pResult;
}

BOOL ObjP_bool_p2o(PyObject *pBool)
{
    OBJP_LOCKGIL;
    BOOL result = PyObject_IsTrue(pBool);
    OBJP_UNLOCKGIL;
    return result;
}

PyObject* ObjP_bool_o2p(BOOL b)
{
    if (b) {
        Py_RETURN_TRUE;
    }
    else {
        Py_RETURN_FALSE;
    }
}

NSObject* ObjP_obj_p2o(PyObject *pObj)
{
    NSObject *result;
    OBJP_LOCKGIL;
    if (pObj == Py_None) {
        result = nil;
    }
    else if (PyUnicode_Check(pObj)) {
        result = ObjP_str_p2o(pObj);
    }
    else if (PyLong_Check(pObj)) {
        result = [NSNumber numberWithInt:ObjP_int_p2o(pObj)];
    }
    else if (PyFloat_Check(pObj)) {
        result = [NSNumber numberWithDouble:ObjP_float_p2o(pObj)];
    }
    else if (PyBool_Check(pObj)) {
        result = [NSNumber numberWithBool:ObjP_bool_p2o(pObj)];
    }
    else if (PySequence_Check(pObj)) {
        result = ObjP_list_p2o(pObj);
    }
    else if (PyDict_Check(pObj)) {
        result = ObjP_dict_p2o(pObj);
    }
    else {
        NSLog(@"Warning, ObjP_obj_p2o failed.");
        result = nil;
    }
    OBJP_UNLOCKGIL;
    return result;
}

PyObject* ObjP_obj_o2p(NSObject *obj)
{
    if (obj == nil) {
        Py_RETURN_NONE;
    }
    else if ([obj isKindOfClass:[NSString class]]) {
        return ObjP_str_o2p((NSString *)obj);
    }
    else if ([obj isKindOfClass:[NSNumber class]]) {
        const char *objc_type = [(NSNumber *)obj objCType];
        if (objc_type[0] == 'c') {
            return ObjP_bool_o2p([(NSNumber *)obj boolValue]);
        }
        else if ((objc_type[0] == 'f') || (objc_type[0] == 'd')) {
            return ObjP_float_o2p([(NSNumber *)obj doubleValue]);
        }
        else {
            return ObjP_int_o2p([(NSNumber *)obj intValue]);
        }
    }
    else if ([obj isKindOfClass:[NSArray class]]) {
        return ObjP_list_o2p((NSArray *)obj);
    }
    else if ([obj isKindOfClass:[NSDictionary class]]) {
        return ObjP_dict_o2p((NSDictionary *)obj);
    }
    else {
        return NULL;
    }
}

NSArray* ObjP_list_p2o(PyObject *pList)
{
    if (pList == Py_None) {
        return nil;
    }
    OBJP_LOCKGIL;
    PyObject *iterator = PyObject_GetIter(pList);
    OBJP_ERRCHECK(iterator);
    PyObject *item;
    NSMutableArray *result = [NSMutableArray array];
    while ( (item = PyIter_Next(iterator)) ) {
        OBJP_ERRCHECK(item);
        NSObject *value = ObjP_obj_p2o(item);
        if (value == nil) {
            value = [NSNull null];
        }
        [result addObject:value];
        Py_DECREF(item);
    }
    Py_DECREF(iterator);
    OBJP_UNLOCKGIL;
    return result;
}

PyObject* ObjP_list_o2p(NSArray *list)
{
    OBJP_LOCKGIL;
    PyObject *pResult = PyList_New([list count]);
    OBJP_ERRCHECK(pResult);
    NSInteger i;
    for (i=0; i<[list count]; i++) {
        NSObject *obj = [list objectAtIndex:i];
        PyObject *pItem = ObjP_obj_o2p(obj);
        PyList_SET_ITEM(pResult, i, pItem);
    }
    OBJP_UNLOCKGIL;
    return pResult;
}

NSDictionary* ObjP_dict_p2o(PyObject *pDict)
{
    if (pDict == Py_None) {
        return nil;
    }
    PyObject *pKey, *pValue;
    Py_ssize_t pos = 0;
    OBJP_LOCKGIL;
    NSMutableDictionary *result = [NSMutableDictionary dictionary];
    while (PyDict_Next(pDict, &pos, &pKey, &pValue)) {
        OBJP_ERRCHECK(pKey);
        OBJP_ERRCHECK(pValue);
        NSString *key = ObjP_str_p2o(pKey);
        NSObject *value = ObjP_obj_p2o(pValue);
        if (value == nil) {
            value = [NSNull null];
        }
        [result setObject:value forKey:key];
    }
    OBJP_UNLOCKGIL;
    return result;
}

PyObject* ObjP_dict_o2p(NSDictionary *dict)
{
    OBJP_LOCKGIL;
    PyObject *pResult = PyDict_New();
    OBJP_ERRCHECK(pResult);
    for (NSString *key in dict) {
        NSObject *value = [dict objectForKey:key];
        PyObject *pValue = ObjP_obj_o2p(value);
        PyDict_SetItemString(pResult, [key UTF8String], pValue);
        Py_DECREF(pValue);
    }
    OBJP_UNLOCKGIL;
    return pResult;
}

NSPoint ObjP_nspoint_p2o(PyObject *pPoint)
{
    OBJP_LOCKGIL;
    NSPoint result;
    PyObject *iterator = PyObject_GetIter(pPoint);
    OBJP_ERRCHECK(iterator);
    PyObject *item = PyIter_Next(iterator);
    OBJP_ERRCHECK(item);
    result.x = ObjP_float_p2o(item);
    item = PyIter_Next(iterator);
    OBJP_ERRCHECK(item);
    result.y = ObjP_float_p2o(item);
    OBJP_UNLOCKGIL;
    return result;
}

PyObject* ObjP_nspoint_o2p(NSPoint p)
{
    OBJP_LOCKGIL;
    PyObject *pX = ObjP_float_o2p(p.x);
    PyObject *pY = ObjP_float_o2p(p.y);
    PyObject *pResult = PyTuple_Pack(2, pX, pY);
    OBJP_ERRCHECK(pResult);
    Py_DECREF(pX);
    Py_DECREF(pY);
    OBJP_UNLOCKGIL;
    return pResult;
}

// NSSize and NSPoint have the same structure, we can same some code duplication here.
NSSize ObjP_nssize_p2o(PyObject *pSize)
{
    NSPoint p = ObjP_nspoint_p2o(pSize);
    return NSMakeSize(p.x, p.y);
}

PyObject* ObjP_nssize_o2p(NSSize s)
{
    NSPoint p = NSMakePoint(s.width, s.height);
    return ObjP_nspoint_o2p(p);
}

NSRect ObjP_nsrect_p2o(PyObject *pRect)
{
    OBJP_LOCKGIL;
    NSRect result;
    PyObject *iterator = PyObject_GetIter(pRect);
    OBJP_ERRCHECK(iterator);
    PyObject *item = PyIter_Next(iterator);
    OBJP_ERRCHECK(item);
    result.origin.x = ObjP_float_p2o(item);
    item = PyIter_Next(iterator);
    OBJP_ERRCHECK(item);
    result.origin.y = ObjP_float_p2o(item);
    item = PyIter_Next(iterator);
    OBJP_ERRCHECK(item);
    result.size.width = ObjP_float_p2o(item);
    item = PyIter_Next(iterator);
    OBJP_ERRCHECK(item);
    result.size.height = ObjP_float_p2o(item);
    OBJP_UNLOCKGIL;
    return result;
}

PyObject* ObjP_nsrect_o2p(NSRect r)
{
    OBJP_LOCKGIL;
    PyObject *pX = ObjP_float_o2p(r.origin.x);
    PyObject *pY = ObjP_float_o2p(r.origin.y);
    PyObject *pW = ObjP_float_o2p(r.size.width);
    PyObject *pH = ObjP_float_o2p(r.size.height);
    PyObject *pResult = PyTuple_Pack(4, pX, pY, pW, pH);
    OBJP_ERRCHECK(pResult);
    Py_DECREF(pX);
    Py_DECREF(pY);
    Py_DECREF(pW);
    Py_DECREF(pH);
    OBJP_UNLOCKGIL;
    return pResult;
}

/* We can use pyref as is, but in all other o2p code, we expect to have to decref the result,
   so in pyrefs case, we have to incref our pyref before returning it.
*/
PyObject* ObjP_pyref_o2p(PyObject *pyref)
{
    Py_INCREF(pyref);
    return pyref;
}
