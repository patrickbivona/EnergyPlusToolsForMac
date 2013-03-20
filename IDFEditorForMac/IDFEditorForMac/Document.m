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

- (NSData *)dataOfType:(NSString *)typeName error:(NSError **)outError {
    if (! idfObject) {
        return nil;
    }
    NSString *idfAsString = [idfObject componentsJoinedByString:@","];
    return [idfAsString dataUsingEncoding:NSUTF8StringEncoding];
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
