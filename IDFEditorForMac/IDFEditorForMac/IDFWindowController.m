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
@synthesize objectsTable;

- (id)init {
    self = [super initWithWindowNibName:@"IDFWindow" owner:self];
    if (self) {
        
    }
    return self;
}

- (void)dealloc {
    [objectsTable release];
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

- (IBAction)selectedNewObject:(id)sender {
    NSString *class = [self selectedClass];
    [[self document] addEmptyObject:class];
    [classesOutlineView reloadData];
    [self selectClass:class];
    [objectsTable reloadData];
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
    [objectsTable reloadData];
}


#pragma mark - MBTableGridDataSource

- (NSUInteger)numberOfRowsInTableGrid:(MBTableGrid *)aTableGrid {
    return [[self.document fieldsOfClass:[self selectedClass]] count];
}

- (NSUInteger)numberOfColumnsInTableGrid:(MBTableGrid *)aTableGrid {
    NSArray *objs = [self.document idfObjectsOfClass:[self selectedClass]];
    return [objs count];
}

- (id)tableGrid:(MBTableGrid *)aTableGrid objectValueForColumn:(NSUInteger)columnIndex row:(NSUInteger)rowIndex {
    NSArray *objs = [self.document idfObjectsOfClass:[self selectedClass]];
    if ([objs count] == 0)
        return @"";
    else
        return [[objs objectAtIndex:columnIndex] objectAtIndex:rowIndex+1];
}

- (void)tableGrid:(MBTableGrid *)aTableGrid setObjectValue:(id)anObject forColumn:(NSUInteger)columnIndex row:(NSUInteger)rowIndex {
    NSArray *obj = [self.document objectOfClass:[self selectedClass] atIndex:columnIndex];

    NSMutableArray *mobj = [NSMutableArray arrayWithArray:obj];
    [mobj replaceObjectAtIndex:rowIndex+1 withObject:anObject];

    [self.document replaceObjectAtIndex:columnIndex withObject:mobj];
    
    [objectsTable reloadData];
}

- (NSString *)tableGrid:(MBTableGrid *)aTableGrid headerStringForColumn:(NSUInteger)columnIndex {
    return [NSString stringWithFormat:@"Obj %li", (unsigned long)columnIndex + 1, nil];
}

- (NSString *)tableGrid:(MBTableGrid *)aTableGrid headerStringForRow:(NSUInteger)rowIndex {
    NSArray *fieldNames = [self.document fieldsOfClass:[self selectedClass]];
    if ([fieldNames count] == 0)
        return @"";
    else
        return [fieldNames objectAtIndex:rowIndex];
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
