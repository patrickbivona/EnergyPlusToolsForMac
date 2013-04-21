
#import <Cocoa/Cocoa.h>
#import <Python.h>


@interface PyIdfDocument:NSObject 
{
    PyObject *_py;
}
- (PyObject *)pyRef;
- (id)init;
- (NSDictionary *)allClassesWithObjectCount;
- (NSArray *)objects;
- (NSArray *)objectsOfClass:(NSString *)className;
- (NSDictionary *)onlyClassesWithObjectsWithObjectCount;
- (void)readFromFile:(NSString *)path;
- (void)writeToFile:(NSString *)path;
@end
