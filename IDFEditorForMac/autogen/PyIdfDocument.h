
#import <Cocoa/Cocoa.h>
#import <Python.h>


@interface PyIdfDocument:NSObject 
{
    PyObject *_py;
}
- (PyObject *)pyRef;
- (id)init;
- (NSArray *)objects;
- (void)readFromFile:(NSString *)path;
- (void)writeToFile:(NSString *)path;
@end
