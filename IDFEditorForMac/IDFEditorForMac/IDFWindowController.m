//
//  IDFWindowController.m
//  IDFEditorForMac
//
//  Created by Patrick Bivona on 21/02/2013.
//  Copyright (c) 2013 Trico. All rights reserved.
//

#import "IDFWindowController.h"
#import "Document.h"

@implementation IDFWindowController

- (id)init {
    self = [super initWithWindowNibName:@"IDFWindow" owner:self];
    if (self) {
        
    }
    return self;
}

- (void)dealloc {
    [objectsTextView release];
    [super dealloc];
}

- (void)windowDidLoad {
    [super windowDidLoad];
    
    if (self.document) {
        Document *doc = (Document *)self.document;
        NSArray *idfObjects = [doc idfObjects];
        for (NSArray *idfObject in idfObjects) {
            if ([idfObject count] > 0) {
                NSMutableString *obj = [[idfObject componentsJoinedByString:@","] mutableCopy];
                [obj appendString:@";"];
                [objectsTextView insertText:obj];
                [objectsTextView insertText:@"\n"];
            }            
        }
    }
    
}

@end
