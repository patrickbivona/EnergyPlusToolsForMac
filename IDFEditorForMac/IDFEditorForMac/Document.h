//
//  Document.h
//  IDFEditorForMac
//
//  Created by Patrick Bivona on 04/02/2013.
//  Copyright (c) 2013 Trico. All rights reserved.
//

#import <Cocoa/Cocoa.h>


@class IDFWindowController;


@interface Document : NSDocument {
    IDFWindowController *idfWinController;
    NSArray *idfObject;
}

- (NSArray *)idfObject;


@end
