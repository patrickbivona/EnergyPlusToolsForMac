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

- (void)windowDidLoad {
    [super windowDidLoad];
    
    if (self.document) {

        if (objectsTableView.tableColumns.count > 0) {
            NSTableColumn *oldTableColumn = [objectsTableView.tableColumns objectAtIndex:0];
            while (oldTableColumn) {
                [objectsTableView removeTableColumn:oldTableColumn];
                oldTableColumn = [objectsTableView.tableColumns objectAtIndex:0];
            }
        }
    
        Document *doc = (Document *)self.document;
        NSArray *idfObject = [doc idfObject];
        for (NSString *elt in idfObject) {
            NSTableColumn *tableColumn = [[NSTableColumn alloc] initWithIdentifier:elt];
            [tableColumn.headerCell setTitle:elt];
            [objectsTableView addTableColumn:tableColumn];
        }
    }
    
}

- (NSInteger)numberOfRowsInTableView:(NSTableView *)tableView {
    return 1;
}

- (NSView *)tableView:(NSTableView *)tableView viewForTableColumn:(NSTableColumn *)tableColumn row:(NSInteger)row {
        
    NSTextField *result = [tableView makeViewWithIdentifier:@"MyView" owner:self];
    if (! result) {
        result = [[NSTextField alloc] initWithFrame:CGRectZero];
        [result setBordered:FALSE];
        result.identifier = @"MyView";
    }
    
    Document *doc = (Document *)self.document;
    result.stringValue = [[doc idfObject] objectAtIndex:0];
    
    return result;
}

@end
