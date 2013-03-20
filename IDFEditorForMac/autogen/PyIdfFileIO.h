
#import <Cocoa/Cocoa.h>
#import <Python.h>


@interface PyIdfFileIO:NSObject 
{
    PyObject *_py;
}
- (PyObject *)pyRef;
- (id)init;
- (NSArray *)readEplusObjectsFromFile:(NSString *)path;
@end
