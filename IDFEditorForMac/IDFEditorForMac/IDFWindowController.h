//
//  IDFWindowController.h
//  IDFEditorForMac
//
//  Created by Patrick Bivona on 21/02/2013.
//  Copyright (c) 2013 Trico. All rights reserved.
//

#import <Cocoa/Cocoa.h>
#import "MBTableGrid.h"

@interface IDFWindowController : NSWindowController <NSOutlineViewDataSource, NSOutlineViewDelegate, MBTableGridDataSource> {
    IBOutlet NSOutlineView *classesOutlineView;
    IBOutlet MBTableGrid *objectsTable;
    
    NSDictionary *classesWithCount;
}

@property (retain) NSOutlineView *classesOutlineView;
@property (retain) MBTableGrid *objectsTable;

- (void)selectFirstClass;
- (void)selectClass:(NSString *)className;
- (NSString *)selectedClass;

- (void)showClassesWithObjectsOnly:(BOOL)show;

@end
