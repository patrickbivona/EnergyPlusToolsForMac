//
//  IDFEditorForMacTests.m
//  IDFEditorForMacTests
//
//  Created by Patrick Bivona on 20/04/2013.
//  Copyright (c) 2013 Trico. All rights reserved.
//

#import <OCMock/OCMock.h>
#import "Document.h"
#import "IDFEditorForMacTests.h"


@implementation IDFEditorForMacTests

- (void)setUp
{
    [super setUp];
    
    controller = [[IDFWindowController alloc] init];
    doc = [[Document alloc] init];
    docMock = [OCMockObject partialMockForObject:doc];
    [docMock addWindowController:controller];

    NSDictionary *allClasses = @{ @"Version": [NSNumber numberWithInt:1],
                                  @"Timestep": [NSNumber numberWithInt:0] };
    [[[docMock stub] andReturn:allClasses] allClassesWithObjectCount];

    NSDictionary *classesWithObjects = @{ @"Version": [NSNumber numberWithInt:1] };
    [[[docMock stub] andReturn:classesWithObjects] onlyClassesWithObjectsWithObjectCount];
    
    [controller windowDidLoad];
}

- (void)tearDown
{
    [controller release];
    
    [super tearDown];
}

- (void)testPreservesSelectionWhenSwitchingToShowOnlyClassesWithObjectsAndPreviouslySelectedClassHadObjects {
    
    [controller selectClass:@"Version"];
    [controller showClassesWithObjectsOnly:YES];
    
    STAssertEqualObjects([controller selectedClass], @"Version", nil);
}

- (void)testSelectsFirstClassWhenSwitchingToShowOnlyClassesWithObjectsAndPreviouslySelectedClassHadNoObjects {
    
    [controller selectClass:@"Timestep"];
    [controller showClassesWithObjectsOnly:YES];
    
    STAssertEqualObjects([controller selectedClass], @"Version", nil);
}

@end
