//
//  IDFWindowController.h
//  IDFEditorForMac
//
//  Created by Patrick Bivona on 21/02/2013.
//  Copyright (c) 2013 Trico. All rights reserved.
//

#import <Cocoa/Cocoa.h>

@interface IDFWindowController : NSWindowController <NSTableViewDataSource, NSTableViewDelegate> {
    IBOutlet NSTableView *objectsTableView;
}

@end