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
    [self addWindowController:[[IDFWindowController alloc] init]];
}

- (NSArray *)idfObjects {
    if (pyDoc)
        return [pyDoc objects];
    else
        return [NSArray array];
}

- (NSDictionary *)classesWithObjectCount {
    return [pyDoc classesWithObjectCount];
}

@end
