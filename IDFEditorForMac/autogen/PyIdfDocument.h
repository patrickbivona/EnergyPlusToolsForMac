
#import <Cocoa/Cocoa.h>
#import <Python.h>


@interface PyIdfDocument:NSObject 
{
    PyObject *_py;
}
- (PyObject *)pyRef;
- (id)init;
- (void)addEmptyObject:(NSString *)className;
- (NSDictionary *)allClassesWithObjectCount;
- (NSArray *)fieldsOfClass:(NSString *)className;
- (NSArray *)objectOfClass:(NSString *)className atIndex:(NSInteger)index;
- (NSArray *)objects;
- (NSArray *)objectsOfClass:(NSString *)className;
- (NSDictionary *)onlyClassesWithObjectsWithObjectCount;
- (void)readFromFile:(NSString *)path;
- (void)replaceObjectAtIndex:(NSInteger)index withObject:(NSArray *)obj;
- (void)writeToFile:(NSString *)path;
@end
