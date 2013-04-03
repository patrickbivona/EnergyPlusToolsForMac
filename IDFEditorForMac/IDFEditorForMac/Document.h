//
//  Document.h
//  IDFEditorForMac
//
//  Created by Patrick Bivona on 04/02/2013.
//  Copyright (c) 2013 Trico. All rights reserved.
//

#import <Cocoa/Cocoa.h>
#import "PyIdfDocument.h"


@class PyIdfFileIO;
@class IDFWindowController;


@interface Document : NSDocument {
    IDFWindowController *idfWinController;
    PyIdfDocument *pyDoc;
}

- (NSArray *)idfObjects;
- (NSDictionary *)classesWithObjectCount;

@end
