//
//  Created by Bob Ippolito on Mon September 20 2004.
//  Copyright (c) 2004 Bob Ippolito. All rights reserved.
//

#import <Foundation/Foundation.h>
#include <mach-o/dyld.h>
#include <mach-o/loader.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/syslimits.h>
#include <crt_externs.h>
#include <wchar.h>
#include <locale.h>
#include <langinfo.h>

#include <objc/objc-class.h>

#include <Python.h>

//
// Constants
//
NSString *ERR_CANNOT_SAVE_LOCALE = @"Cannot save locale information";
NSString *ERR_REALLYBADTITLE = @"The bundle could not be launched.";
NSString *ERR_TITLEFORMAT = @"%@ has encountered a fatal error, and will now terminate.";
NSString *ERR_PYRUNTIMELOCATIONS = @"The Info.plist file must have a PyRuntimeLocation string containing the Python runtime location.  These strings should be \"otool -L\" style mach ids; \"@executable_stub\" and \"~\" prefixes will be translated accordingly.";
NSString *ERR_NOPYTHONRUNTIME = @"A Python runtime could be located.\r";
NSString *ERR_NOPYTHONSCRIPT = @"The main script could not be located in the Resources folder.\rThe name that was looked for:\r\r";
NSString *ERR_LINKERRFMT = @"An internal error occurred while attempting to link with:\r\r%s\r\rSee the Console for a detailed dyld error message";
NSString *ERR_PYTHONEXCEPTION = @"An uncaught exception was raised during execution of the main script:\r\r%@: %@\r\rThis may mean that an unexpected error has occurred, or that you do not have all of the dependencies for this bundle.";

#define PYMACAPP_NSIMAGEFLAGS (NSADDIMAGE_OPTION_RETURN_ON_ERROR | NSADDIMAGE_OPTION_WITH_SEARCHING)
#define PYMACAPP_NSLOOKUPSYMBOLINIMAGEFLAGS (NSLOOKUPSYMBOLINIMAGE_OPTION_BIND | NSLOOKUPSYMBOLINIMAGE_OPTION_RETURN_ON_ERROR)

//
// Signatures
//

static int report_error(NSString *err);
static int report_linkEdit_error(const char* name);
static int report_script_error(NSString *err, NSString *errClassName, NSString *errName);
static NSString *pyStandardizePath(NSString *pyLocation);
static BOOL doesPathExist(NSString *path);
static NSString *getBundleName(void);
static NSString *getErrorTitle(NSString *bundleName);
static const char *bundlePath(void);
static NSBundle *bundleBundle(void);
static int pyobjc_main(int argc, char * const *argv);

//
// Mach-O Constructor
//

static void __attribute__ ((constructor)) _pluginbuilder_bundle_load(void);

//
// Implementation
//

static
const char *bundlePath(void) {
    int i;
    const struct mach_header *myHeader = _dyld_get_image_header_containing_address(&bundlePath);
    int count = _dyld_image_count();
    for (i = 0; i < count; i++) {
        if (_dyld_get_image_header(i) == myHeader) {
            return _dyld_get_image_name(i);
        }
    }
    abort();
    return NULL;
}

static
NSBundle *bundleBundle(void) {
    static NSBundle *myBundle = NULL;
    if (!myBundle) {
        int i;
        NSString *path = [NSString stringWithUTF8String:bundlePath()];
        // strip Contents/MacOS/App
        for (i = 0; i < 3; i++) {
            path = [path stringByDeletingLastPathComponent];
        }
        myBundle = [[NSBundle alloc] initWithPath:path];
    }
    return myBundle;
}

static
int report_error(NSString *err) {
    NSLog(@"%@", getErrorTitle(getBundleName()));
    NSLog(@"%@", err);
    return -1;
}

static
int report_linkEdit_error(const char* name) {
    NSLinkEditErrors errorClass;
    int errorNumber;
    const char *fileName;
    const char *errorString;
    NSLinkEditError(&errorClass, &errorNumber, &fileName, &errorString);
    NSLog(@"%s: %s", name, errorString);
    printf("<<<pluginbuilder>>>> %s: %s\n", name, errorString);
    return report_error([NSString stringWithFormat:ERR_LINKERRFMT, fileName]);
}

static
NSString *pyStandardizePath(NSString *pyLocation) {
        if ([pyLocation hasPrefix:@"@executable_path/"]) {
            NSMutableArray *newComponents = [[pyLocation pathComponents] mutableCopy];
            [newComponents replaceObjectAtIndex:0 withObject:[bundleBundle() privateFrameworksPath]];
            pyLocation = [NSString pathWithComponents: newComponents];
        }
        return [pyLocation stringByStandardizingPath];
};

static
BOOL doesPathExist(NSString *path) {
        struct stat sb;
        return (stat([path fileSystemRepresentation], &sb) == -1) ? NO : YES;
}

static
NSString *getBundleName(void) {
    NSDictionary *infoDictionary = [bundleBundle() infoDictionary];
    NSString *bundleName = [infoDictionary objectForKey:@"CFBundleName"];
    if (!bundleName) {
        bundleName = [infoDictionary objectForKey:@"CFBundleExecutable"];
    }
    return bundleName;
}

static
NSString *getErrorTitle(NSString *bundleName) {
    if (!bundleName) {
        return ERR_REALLYBADTITLE;
    }
    return [NSString stringWithFormat:ERR_TITLEFORMAT,bundleName];
}

static
NSString *getMainPyPath(NSDictionary *infoDictionary) {
    NSString *mainPyFilename = [infoDictionary objectForKey:@"PyMainFileNames"];
    if ( !mainPyFilename ) {
        mainPyFilename = @"__boot__.py";
    }
    NSString *mainPyPath = [bundleBundle() pathForResource:mainPyFilename ofType:nil];
    if (!mainPyPath) {
        report_error([ERR_NOPYTHONSCRIPT stringByAppendingString:mainPyPath]);
    }
    return mainPyPath;
}

static
BOOL getPyOption(NSDictionary *infoDictionary, NSString *optionName) {
    NSDictionary *pyOptions = [infoDictionary objectForKey:@"PyOptions"];
    NSNumber *optionAsNumber = [pyOptions objectForKey:optionName];
    if (optionAsNumber == nil) {
        return NO;
    }
    return [optionAsNumber boolValue];
}

int pyobjc_main(int argc, char * const *argv) {
    char* curenv;
    char* curlocale;
    NSDictionary *infoDictionary = [bundleBundle() infoDictionary];

    NSString *pyLocation = [infoDictionary objectForKey:@"PyRuntimeLocation"];
    if (!pyLocation) {
        return report_error(ERR_PYRUNTIMELOCATIONS);
    }
    pyLocation = pyStandardizePath(pyLocation);
    if (!doesPathExist(pyLocation)) {
        return report_error(ERR_NOPYTHONRUNTIME);
    }

    // Find our resource path and possible PYTHONPATH
    NSString *resourcePath = [bundleBundle() resourcePath];
    NSString *libraryPath = [resourcePath stringByAppendingPathComponent:[infoDictionary objectForKey:@"PyLibraryPath"]];

    // find the main script
    NSString *mainPyPath = getMainPyPath(infoDictionary);
    if (!mainPyPath) {
        // error already reported
        return -1;
    }

    // Load the Python dylib (may have already been loaded, that is OK)
    const struct mach_header *py_dylib = NSAddImage([pyLocation fileSystemRepresentation], PYMACAPP_NSIMAGEFLAGS);
    if (!py_dylib) { 
        return report_linkEdit_error([pyLocation fileSystemRepresentation]);
    }

    /*
     * When apps are started from the Finder (or anywhere
     * except from the terminal), the LANG and LC_* variables
     * aren't set in the environment. This confuses Py_Initialize
     * when it tries to import the codec for UTF-8, 
     * therefore explicitly set the locale. 
     *
     * Also set the LC_CTYPE environment variable because Py_Initialize
     * reset the locale information using the environment :-(
     */
    curlocale = setlocale(LC_ALL, NULL);
    if (curlocale != NULL) {
	curlocale = strdup(curlocale);
	if (curlocale == NULL) {
		(void)report_error(ERR_CANNOT_SAVE_LOCALE);
		return -1;
	}
    }
    setlocale(LC_ALL, "en_US.UTF-8");

    curenv = getenv("LC_CTYPE");
    if (curenv) {
        curenv = strdup(curenv);
    }


    // Set up the environment variables
    setenv("PYOBJC_BUNDLE_ADDRESS", [[NSString stringWithFormat:@"%p", bundleBundle()] UTF8String], 1);
    setenv("RESOURCEPATH", [resourcePath UTF8String], 1);
    setenv("LIBRARYPATH", [libraryPath UTF8String], 1);
    
    // bootstrap Python with information about how to find what it needs
    // if it is not already initialized
    if (!getPyOption(infoDictionary, @"alias")) {
        wchar_t wPythonHome[PATH_MAX+1];
        mbstowcs(wPythonHome, [resourcePath fileSystemRepresentation], PATH_MAX+1);
        Py_SetPythonHome(wPythonHome);
    }
    
    NSString *pythonProgramName = [pyLocation stringByDeletingLastPathComponent];
    pythonProgramName = [[pythonProgramName stringByAppendingPathComponent:@"bin"] stringByAppendingPathComponent:@"python"];
    wchar_t wPythonName[PATH_MAX+1];
    mbstowcs(wPythonName, [pythonProgramName fileSystemRepresentation], PATH_MAX+1);
    Py_SetProgramName(wPythonName);
    
    int rval = 0;
    FILE *mainPyFile = NULL;
    Py_Initialize();
    PyEval_InitThreads();
    
    /*
     * Reset the environment and locale information
     */
    setlocale(LC_CTYPE, curlocale);
    free(curlocale);

    if (curenv) {
        setenv("LC_CTYPE", curenv, 1);
        free(curenv);
    } else {
        unsetenv("LC_CTYPE");
    }


    PyGILState_STATE gilState = PyGILState_Ensure();

    char *c_mainPyPath = (char *)[mainPyPath fileSystemRepresentation];
    mainPyFile = fopen(c_mainPyPath, "r");
    if (!mainPyFile) {
        rval = report_error([NSString stringWithFormat:@"Could not open main script %@",mainPyPath]);
        goto cleanup;
    }
    NSMutableData *data_argv = [NSMutableData dataWithCapacity:(sizeof(char *) * argc)];
    char **argv_new = [data_argv mutableBytes];
    argv_new[0] = c_mainPyPath;
    memcpy(&argv_new[1], &argv[1], (argc - 1) * sizeof(char *));
    PySys_SetArgv(argc, argv_new);

    // create a unique moduleName by CFBundleIdentifier replacing . with _ and prepending __main__
    NSString *moduleName = [NSString stringWithFormat:@"__main__%@", [[[infoDictionary objectForKey:@"CFBundleIdentifier"] componentsSeparatedByString:@"."] componentsJoinedByString:@"_"]];
    PyObject *module = PyImport_AddModule((char *)[moduleName UTF8String]);
    if (!module) {
        rval = report_error([NSString stringWithFormat:@"Could not create module '%@'",moduleName]);
        goto cleanup;
    }
    PyModule_AddStringConstant(module, "__file__", c_mainPyPath);
    PyObject *builtins = PyImport_ImportModule("builtins");
    PyModule_AddObject(module, "__builtins__", builtins);
    PyObject *module_dict = PyModule_GetDict(module);
    if (PyErr_Occurred()) {
        goto cleanup;
    }

    PyObject *res = PyRun_File(mainPyFile, c_mainPyPath, Py_file_input, module_dict, module_dict);
    Py_DecRef(res);

cleanup:
    if (mainPyFile) {
        fclose(mainPyFile);
    }
    if (PyErr_Occurred()) {
        rval = -1;
        PyErr_Print();
    }
    while ( rval ) {
        PyObject *exc = PySys_GetObject("last_type");
        if ( !exc ) {
            rval = report_error([NSString stringWithFormat:ERR_PYTHONEXCEPTION,"<<PyMacAppException>>","The exception went away?"]);
            break;
        }

        PyObject *exceptionClassName = PyObject_GetAttrString(exc, "__name__");
        if ( !exceptionClassName ) {
            rval = report_error([NSString stringWithFormat:ERR_PYTHONEXCEPTION,"<<PyMacAppException>>","Could not get exception class name?"]);
            break;
        }

        PyObject *v = PySys_GetObject("last_value");
        PyObject *exceptionName = NULL;
        if ( v )
            exceptionName = PyObject_Str(v);

        PyObject *b = PyObject_CallMethod(exceptionClassName, "encode", "s", "utf-8");
        NSString *nsExceptionClassName = [NSString stringWithCString:PyBytes_AsString(b) encoding:NSUTF8StringEncoding];
        Py_DecRef(exceptionClassName);Py_DecRef(b);
        NSString *nsExceptionName;
        if ( exceptionName ) {
            PyObject *b = PyObject_CallMethod(exceptionName, "encode", "s", "utf-8");
            nsExceptionName = [NSString stringWithCString:PyBytes_AsString(b) encoding:NSUTF8StringEncoding];
            Py_DecRef(exceptionName);Py_DecRef(b);
        } else {
            nsExceptionName = @"";
        }
        rval = report_error([NSString stringWithFormat:ERR_PYTHONEXCEPTION, nsExceptionClassName, nsExceptionName]);
        break;
    }
    PyErr_Clear();
    PyGILState_Release(gilState);
    if (gilState == PyGILState_LOCKED) {
        PyThreadState_Swap(NULL);
        PyEval_ReleaseLock();
    }

    return rval;
}


static
void _pluginbuilder_bundle_load(void)
{
    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
    int argc = 1;
    char * const argv[] = { (char *)bundlePath(), NULL };
    (void)pyobjc_main(argc, argv);
    [pool release];
}


