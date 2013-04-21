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

@synthesize classesOutlineView;
@synthesize objectsTextView;

- (id)init {
    self = [super initWithWindowNibName:@"IDFWindow" owner:self];
    if (self) {
        
    }
    return self;
}

- (void)dealloc {
    [objectsTextView release];
    [classesOutlineView release];
    [classesWithCount release];
    [super dealloc];
}

- (void)windowDidLoad {
    [super windowDidLoad];
    
    if (self.document) {
        [classesOutlineView sizeLastColumnToFit];
        [classesOutlineView setFloatsGroupRows:NO];
        [self showClassesWithObjectsOnly:NO];
        
        [self selectFirstClass];
    }
}


#pragma mark - NSOutlineViewDataSource


- (id)outlineView:(NSOutlineView *)outlineView child:(NSInteger)index ofItem:(id)item {
    if (! classesWithCount || item)
        return nil;
    // TODO optimise by not sorting the list at every call
    NSArray *orderedClasses = [classesWithCount keysSortedByValueUsingSelector:@selector(compare:)];
    NSString *className = [orderedClasses objectAtIndex:index];
    NSNumber *count = [classesWithCount objectForKey:className];
    NSString *result = [NSString stringWithFormat:@"%@ (%i)", className, [count intValue]];
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

#pragma mark - NSOutlineViewDelegate

- (void)outlineViewSelectionDidChange:(NSNotification *)notification {
    NSString *className = [[self orderedClassNames] objectAtIndex:classesOutlineView.selectedRow];
    NSArray *obj = [self.document idfObjectsOfClass:className];
    [self updateObjectList:obj];
}

#pragma mark - Public

- (void)selectFirstClass {
    [classesOutlineView selectRowIndexes:[NSIndexSet indexSetWithIndex:0]
                    byExtendingSelection:NO];
}

- (void)selectClass:(NSString *)className {
    NSUInteger index = [[self orderedClassNames] indexOfObject:className];
    if (index == NSNotFound)
        return;
    [classesOutlineView selectRowIndexes:[NSIndexSet indexSetWithIndex:index]
                    byExtendingSelection:NO];
}

- (NSString *)selectedClass {
    NSInteger index = classesOutlineView.selectedRow;
    if (index == -1)
        return @"";
    
    if ([classesWithCount count] == 0)
        return @"";
    
    return [[self orderedClassNames] objectAtIndex:index];
}


- (void)updateObjectList:(NSArray *)idfObjects {
    [objectsTextView setString:@""];
    
    for (NSArray *idfObject in idfObjects) {
        if ([idfObject count] > 0) {
            NSMutableString *obj = [[idfObject componentsJoinedByString:@","] mutableCopy];
            [obj appendString:@";"];
            [objectsTextView insertText:obj];
            [objectsTextView insertText:@"\n"];
        }
    }
}

- (void)showClassesWithObjectsOnly:(BOOL)show {
    NSString *selectedClass = [self selectedClass];
    
    if (classesWithCount)
        [classesWithCount release];

    if (show)
        classesWithCount = [[self.document onlyClassesWithObjectsWithObjectCount] retain];
    else
        classesWithCount = [[self.document allClassesWithObjectCount] retain];
    [classesOutlineView reloadData];
    
    if ([[self orderedClassNames] indexOfObject:selectedClass] == NSNotFound)
        [self selectFirstClass];
    else
        [self selectClass:selectedClass];
}

#pragma mark - Helpers

- (NSArray *)orderedClassNames {
    if (classesWithCount)
        return [classesWithCount keysSortedByValueUsingSelector:@selector(compare:)];
    else
        return [NSArray array];
}

@end
