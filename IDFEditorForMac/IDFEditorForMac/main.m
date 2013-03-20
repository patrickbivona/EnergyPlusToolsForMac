//
//  main.m
//  IDFEditorForMac
//
//  Created by Patrick Bivona on 04/02/2013.
//  Copyright (c) 2013 Trico. All rights reserved.
//

#import <Cocoa/Cocoa.h>
#import <Python.h>
#include <wchar.h>

int main(int argc, char *argv[])
{
    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
    NSString *respath = [[NSBundle mainBundle] resourcePath];
    NSString *pypath = [respath stringByAppendingPathComponent:@"py"];
    NSString *mainpy = [pypath stringByAppendingPathComponent:@"pyplugin.py"];
    wchar_t wPythonPath[PATH_MAX+1];
    mbstowcs(wPythonPath, [pypath fileSystemRepresentation], PATH_MAX+1);
    Py_SetPath(wPythonPath);
    Py_Initialize();
    FILE* fp = fopen([mainpy UTF8String], "r");
    PyRun_SimpleFile(fp, "pyplugin.py");
    fclose(fp);
    int result = NSApplicationMain(argc,  (const char **) argv);
    Py_Finalize();
    [pool release];
    return result;
}
