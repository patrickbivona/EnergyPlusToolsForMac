import sys
from .. import __version__

def infoPlistDict(CFBundleExecutable, plist={}):
    CFBundleExecutable = str(CFBundleExecutable)
    NSPrincipalClass = ''.join(CFBundleExecutable.split())
    version = sys.version[:3]
    pdict = dict(
        CFBundleDevelopmentRegion='English',
        CFBundleDisplayName=plist.get('CFBundleName', CFBundleExecutable),
        CFBundleExecutable=CFBundleExecutable,
        CFBundleIconFile=CFBundleExecutable,
        CFBundleIdentifier='org.pythonmac.unspecified.%s' % (NSPrincipalClass,),
        CFBundleInfoDictionaryVersion='6.0',
        CFBundleName=CFBundleExecutable,
        CFBundlePackageType='BNDL',
        CFBundleShortVersionString=plist.get('CFBundleVersion', '0.0'),
        CFBundleSignature='????',
        CFBundleVersion='0.0',
        LSHasLocalizedDisplayName=False,
        NSAppleScriptEnabled=False,
        NSHumanReadableCopyright='Copyright not specified',
        NSMainNibFile='MainMenu',
        NSPrincipalClass=NSPrincipalClass,
        PyMainFileName='__boot__.py',
        PyLibraryPath = 'lib/python{}'.format(version),
        PyRuntimeLocation='@executable_path/../Frameworks/Python.framework/Versions/{}/Python'.format(version),
    )
    pdict.update(plist)
    pythonInfo = pdict.setdefault('PythonInfoDict', {})
    pythonInfo.update(dict(
        PythonLongVersion=str(sys.version),
        PythonShortVersion=str(sys.version[:3]),
        PythonExecutable=str(sys.executable),
    ))
    pythonInfo.setdefault('pluginbuilder', {}).update(dict(version=__version__))
    return pdict
