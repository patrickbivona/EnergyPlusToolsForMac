
#import <Cocoa/Cocoa.h>
#import <Python.h>


@interface PyIdfDocument:NSObject 
{
    PyObject *_py;
}
- (PyObject *)pyRef;
- (id)init;
- (NSDictionary *)classesWithObjectCount;
- (NSArray *)objects;
- (NSArray *)objectsOfClass:(NSString *)className;
- (void)readFromFile:(NSString *)path;
- (void)writeToFile:(NSString *)path;
@end
