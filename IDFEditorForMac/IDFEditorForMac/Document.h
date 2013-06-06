//
//  Document.h
//  IDFEditorForMac
//
//  Created by Patrick Bivona on 04/02/2013.
//  Copyright (c) 2013 Trico. All rights reserved.
//

#import <Cocoa/Cocoa.h>
#import "PyIdfDocument.h"


@class PyIdfFileIO;
@class IDFWindowController;


@interface Document : NSDocument {
    IDFWindowController *idfWinController;
    PyIdfDocument *pyDoc;
    BOOL showClassesWithObjectsOnly;
}

- (NSArray *)idfObjects;
- (NSArray *)idfObjectsOfClass:(NSString *)className;
- (NSArray *)fieldsOfClass:(NSString *)className;
- (NSArray *)objectOfClass:(NSString *)className atIndex:(NSUInteger)index;
- (void)replaceObjectAtIndex:(NSUInteger)index withObject:(NSArray *)obj;
- (void)deleteObjectOfClass:(NSString*)className atIndex:(NSUInteger)index;

- (NSDictionary *)allClassesWithObjectCount;
- (NSDictionary *)onlyClassesWithObjectsWithObjectCount;

- (void)addEmptyObject:(NSString *)className;

- (IBAction)selectedShowClassesWithObjectsOnly:(id)sender;

@end
