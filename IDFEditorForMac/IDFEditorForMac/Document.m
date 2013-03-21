//
//  Document.m
//  IDFEditorForMac
//
//  Created by Patrick Bivona on 04/02/2013.
//  Copyright (c) 2013 Trico. All rights reserved.
//

#import "Document.h"
#import "IDFWindowController.h"
#import "PyIdfFileIO.h"

@implementation Document

- (id)init {
    self = [super init];
    if (self) {
        
    }
    return self;
}

- (void)dealloc
{
    [py release];
    [idfObject release];
    [idfWinController release];
    [super dealloc];
}

+ (BOOL)autosavesInPlace {
    return YES;
}

-(BOOL)writeToURL:(NSURL *)url ofType:(NSString *)typeName error:(NSError **)outError {
    
    if (! (url.isFileURL && py))
        return FALSE;
    
    [py writeEplusObjects:[NSArray arrayWithObject:idfObject] toFile:[url path]];
    return TRUE;
}

-(BOOL)readFromURL:(NSURL *)url ofType:(NSString *)typeName error:(NSError *__autoreleasing *)outError {

    if (! url.isFileURL)
        return FALSE;
    
    py = [[PyIdfFileIO alloc] init];

    NSString *path =[url path];
    NSArray *objects = [py readEplusObjectsFromFile:path];
    if (! objects || [objects count] == 0)
        return FALSE;

    idfObject = [[objects objectAtIndex:0] retain];
    return TRUE;
}

- (void)makeWindowControllers {
    [self addWindowController:[[IDFWindowController alloc] init]];
}

- (NSArray *)idfObject {
    return idfObject;
}

@end
