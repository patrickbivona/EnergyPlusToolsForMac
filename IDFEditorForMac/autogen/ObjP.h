#import <Cocoa/Cocoa.h>
#import <Python.h>

#define OBJP_LOCKGIL PyGILState_STATE gilState = PyGILState_Ensure()
#define OBJP_UNLOCKGIL PyGILState_Release(gilState)

// This macro below can only be used inside OBJP_LOCKGIL and OBJP_UNLOCKGIL because when there's
// an exception, the GIL will be released before throwing an exception.
#define OBJP_ERRCHECK(x) if (x == NULL) {ObjP_raisePyExceptionInCocoa(gilState);}

PyObject* ObjP_findPythonClass(NSString *name, NSString *inModule);
PyObject* ObjP_classInstanceWithRef(NSString *className, NSString *inModule, id ref);
void ObjP_raisePyExceptionInCocoa(PyGILState_STATE gilState);
NSString* ObjP_str_p2o(PyObject *pStr);
PyObject* ObjP_str_o2p(NSString *str);
NSInteger ObjP_int_p2o(PyObject *pInt);
PyObject* ObjP_int_o2p(NSInteger i);
CGFloat ObjP_float_p2o(PyObject *pFloat);
PyObject* ObjP_float_o2p(CGFloat f);
BOOL ObjP_bool_p2o(PyObject *pBool);
PyObject* ObjP_bool_o2p(BOOL b);
NSObject* ObjP_obj_p2o(PyObject *pObj);
PyObject* ObjP_obj_o2p(NSObject *obj);
NSArray* ObjP_list_p2o(PyObject *pList);
PyObject* ObjP_list_o2p(NSArray *list);
NSDictionary* ObjP_dict_p2o(PyObject *pDict);
PyObject* ObjP_dict_o2p(NSDictionary *dict);
NSPoint ObjP_nspoint_p2o(PyObject *pPoint);
PyObject* ObjP_nspoint_o2p(NSPoint p);
NSSize ObjP_nssize_p2o(PyObject *pSize);
PyObject* ObjP_nssize_o2p(NSSize s);
NSRect ObjP_nsrect_p2o(PyObject *pRect);
PyObject* ObjP_nsrect_o2p(NSRect r);
PyObject* ObjP_pyref_o2p(PyObject *pyref);

