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
        
    }
    return self;
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

- (BOOL)readFromData:(NSData *)data ofType:(NSString *)typeName error:(NSError **)outError {
    
    NSString *idfAsString = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
    idfObject = [idfAsString componentsSeparatedByString:@","];
    return TRUE;
}

- (void)makeWindowControllers {
    [self addWindowController:[[IDFWindowController alloc] init]];
}

- (NSArray *)idfObject {
    return idfObject;
}

@end
