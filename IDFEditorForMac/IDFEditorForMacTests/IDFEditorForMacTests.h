//
//  IDFEditorForMacTests.h
//  IDFEditorForMacTests
//
//  Created by Patrick Bivona on 20/04/2013.
//  Copyright (c) 2013 Trico. All rights reserved.
//

#import <SenTestingKit/SenTestingKit.h>
#import "IDFWindowController.h"

@interface IDFEditorForMacTests : SenTestCase {
    IDFWindowController *controller;
    Document *doc;
    id docMock;
}

@end
