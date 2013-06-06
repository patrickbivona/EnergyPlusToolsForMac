//
//  Document.m
//  IDFEditorForMac
//
//  Created by Patrick Bivona on 04/02/2013.
//  Copyright (c) 2013 Trico. All rights reserved.
//

#import "Document.h"
#import "IDFWindowController.h"

@implementation Document

- (id)init {
    self = [super init];
    if (self) {
        pyDoc = [[PyIdfDocument alloc] init];
        showClassesWithObjectsOnly = NO;
    }
    return self;
}

- (void)dealloc {
    [pyDoc release];
    [idfWinController release];
    [super dealloc];
}

+ (BOOL)autosavesInPlace {
    return YES;
}

-(BOOL)writeToURL:(NSURL *)url ofType:(NSString *)typeName error:(NSError **)outError {
    
    if (! (url.isFileURL && pyDoc))
        return FALSE;
    
    [pyDoc writeToFile:[url path]];
    return TRUE;
}

-(BOOL)readFromURL:(NSURL *)url ofType:(NSString *)typeName error:(NSError *__autoreleasing *)outError {

    if (! url.isFileURL)
        return FALSE;
    
    NSString *path =[url path];
    [pyDoc readFromFile:path];
    return TRUE;
}

- (void)makeWindowControllers {
    if (!idfWinController) {
        idfWinController = [[IDFWindowController alloc] init];
        [self addWindowController:idfWinController];
    }
}

#pragma mark - Menu items

- (BOOL)validateMenuItem:(NSMenuItem *)menuItem {
    if ([menuItem action] == @selector(selectedShowClassesWithObjectsOnly:)) {
        if (showClassesWithObjectsOnly)
            [menuItem setState:NSOnState];
        else
            [menuItem setState:NSOffState];
        return [[self idfObjects] count] > 0;
    }
    return [super validateMenuItem:menuItem];
}


- (IBAction)selectedShowClassesWithObjectsOnly:(id)sender {
    showClassesWithObjectsOnly = !showClassesWithObjectsOnly;
    [idfWinController showClassesWithObjectsOnly:showClassesWithObjectsOnly];
}

#pragma mark - Py-ObjC bridge

- (NSArray *)idfObjects {
    return [pyDoc objects];
}

- (NSArray *)idfObjectsOfClass:(NSString *)className {
    return [pyDoc objectsOfClass:className];
}

- (NSDictionary *)allClassesWithObjectCount {
    return [pyDoc allClassesWithObjectCount];
}

- (NSDictionary *)onlyClassesWithObjectsWithObjectCount {
    return [pyDoc onlyClassesWithObjectsWithObjectCount];
}

- (NSArray*)fieldsOfClass:(NSString *)className {
    return [pyDoc fieldsOfClass:className];
}

- (void)addEmptyObject:(NSString *)className {
    [pyDoc addEmptyObject:className];
}

- (NSArray *)objectOfClass:(NSString *)className atIndex:(NSUInteger)index {
    return [pyDoc objectOfClass:className atIndex:index];
}

- (void)replaceObjectAtIndex:(NSUInteger)index withObject:(NSArray *)obj {
    [pyDoc replaceObjectAtIndex:index withObject:obj];
}

- (void)deleteObjectOfClass:(NSString*)className atIndex:(NSUInteger)index {
    [pyDoc deleteObjectOfClass:className atIndex:index];
}

@end
