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
    [classesOutlineView release];
    [super dealloc];
}

- (void)windowDidLoad {
    [super windowDidLoad];
    
    if (self.document) {
        [classesOutlineView sizeLastColumnToFit];
        [classesOutlineView setFloatsGroupRows:NO];
        [self updateClassList];
        
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

- (void)updateClassList {
    if (classesWithCount) {
        [classesWithCount release];
    }
    if (self.document) {
        classesWithCount = [[self.document classesWithObjectCount] retain];
    } else {
        classesWithCount = [[NSDictionary dictionary] retain];
    }
    [classesOutlineView reloadData];
}


#pragma mark - NSOutlineViewDataSource


- (id)outlineView:(NSOutlineView *)outlineView child:(NSInteger)index ofItem:(id)item {
    if (! classesWithCount || item)
        return nil;
    // TODO optimise by not sorting the list at every call
    NSArray *orderedClasses = [classesWithCount keysSortedByValueUsingSelector:@selector(compare:)];
    NSString *result = [orderedClasses objectAtIndex:index];
    return result;
}

- (NSInteger)outlineView:(NSOutlineView *)outlineView numberOfChildrenOfItem:(id)item {
    if (! classesWithCount || item)
        return 0;
    return [classesWithCount count];
}

- (BOOL)outlineView:(NSOutlineView *)outlineView isItemExpandable:(id)item {
    return NO;
}

- (NSView *)outlineView:(NSOutlineView *)outlineView viewForTableColumn:(NSTableColumn *)tableColumn item:(id)item {
    NSTableCellView *result = [outlineView makeViewWithIdentifier:@"EplusClassName" owner:self];
    [result.textField setStringValue:item];
    return result;
}

@end
