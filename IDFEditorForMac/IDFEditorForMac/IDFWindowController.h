//
//  IDFWindowController.h
//  IDFEditorForMac
//
//  Created by Patrick Bivona on 21/02/2013.
//  Copyright (c) 2013 Trico. All rights reserved.
//

#import <Cocoa/Cocoa.h>

@interface IDFWindowController : NSWindowController <NSOutlineViewDataSource, NSOutlineViewDelegate> {
    IBOutlet NSOutlineView *classesOutlineView;
    IBOutlet NSTextView *objectsTextView;
    
    NSDictionary *classesWithCount;
}

@property (retain) NSOutlineView *classesOutlineView;
@property (retain) NSTextView *objectsTextView;

- (void)selectFirstClass;
- (void)selectClass:(NSString *)className;
- (NSString *)selectedClass;

- (void)updateObjectList:(NSArray *)idfObjects;

- (void)showClassesWithObjectsOnly:(BOOL)show;

@end
