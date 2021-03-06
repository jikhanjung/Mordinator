from distutils.core import setup
#import py2exe
#import sys

use_mplot = False
  
from Mordinator_version import *  

manifest_template = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
/>
<description>%(prog)s Program</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
'''

RT_MANIFEST = 24

mordinator = dict(
    script = "MordinatorMain.py",
    other_resources = [(RT_MANIFEST, 1, manifest_template % dict(prog="Mordinator"))],
    dest_base = r"prog\Mordinator")

zipfile = r"lib/shardlib"

options = {"py2exe": {
                      "compressed": 1,
                      "optimize": 2,
                      #"includes": ["ctypes", "logging"],
                      #"excludes": ["OpenGL"],
                      }
          }

import os

class InnoScript:
    def __init__(self,
                 name,
                 groupname,
                 lib_dir,
                 dist_dir,
                 windows_exe_files = [],
                 lib_files = [],
                 version = "1.0"):
        self.lib_dir = lib_dir
        self.dist_dir = dist_dir
        if not self.dist_dir[-1] in "\\/":
            self.dist_dir += "\\"
        self.name = name
        self.groupname = groupname
        self.version = version
        self.windows_exe_files = [self.chop(p) for p in windows_exe_files]
        self.lib_files = [self.chop(p) for p in lib_files]

    def chop(self, pathname):
        assert pathname.startswith(self.dist_dir)
        return pathname[len(self.dist_dir):]
    
    def create(self, pathname="dist\\Mordinator.iss"):
        self.pathname = pathname
        ofi = self.file = open(pathname, "w")
        print >> ofi, "; WARNING: This script has been created by py2exe. Changes to this script"
        print >> ofi, "; will be overwritten the next time py2exe is run!"
        print >> ofi, r"[Setup]"
        print >> ofi, r"AppName=%s" % self.name
        print >> ofi, r"AppVerName=%s %s" % (self.name, self.version)
        print >> ofi, r"DefaultDirName={pf}\%s\%s" % ( self.groupname, self.name )
        print >> ofi, r"DefaultGroupName=%s" % self.groupname
        print >> ofi, r"OutputBaseFilename=%s-%s-win32" % ( self.name, self.version )
        print >> ofi

        print >> ofi, r"[Files]"
        for path in self.windows_exe_files + self.lib_files:
            print >> ofi, r'Source: "%s"; DestDir: "{app}\%s"; Flags: ignoreversion' % (path, os.path.dirname(path))
        print >> ofi

        print >> ofi, r"[Icons]"
        for path in self.windows_exe_files:
            print >> ofi, r'Name: "{group}\%s"; Filename: "{app}\%s"; WorkingDir: "{app}"; ' % \
                  (self.name, path)
        print >> ofi, 'Name: "{group}\Uninstall %s"; Filename: "{uninstallexe}"' % self.name

# https://translate.svn.sourceforge.net/svnroot/translate/src/trunk/spelt/setup.py

    def compile(self):
        try:
            import ctypes
        except ImportError:
            try:
                import win32api
            except ImportError:
                import os
                os.startfile(self.pathname)
            else:
                print "Ok, using win32api."
                win32api.ShellExecute(0, "compile",
                                                self.pathname,
                                                None,
                                                None,
                                                0)
        else:
            print "Cool, you have ctypes installed."
            res = ctypes.windll.shell32.ShellExecuteA(0, "compile",
                                                      self.pathname,
                                                      None,
                                                      None,
                                                      0)
            if res < 32:
                raise RuntimeError, "ShellExecute failed, error %d" % res

#from py2exe.build_exe import py2exe
from py2exe.build_exe import py2exe
 
class build_installer(py2exe):
    # This class first builds the exe file(s), then creates a Windows installer.
    # You need InnoSetup for it.
    def run(self):
        # First, let py2exe do it's work.
        py2exe.run(self)

        lib_dir = self.lib_dir
        dist_dir = self.dist_dir
        
        # create the Installer, using the files py2exe has created.
        script = InnoScript("Mordinator",
                            "DiploSoft",
                            lib_dir,
                            dist_dir,
                            self.windows_exe_files,
                            self.lib_files,
                            version = MORDINATOR_VERSION )
        print "*** creating the inno setup script***"
        script.create()
        print "*** compiling the inno setup script***"
        script.compile()
        # Note: By default the final setup.exe will be in an Output subdirectory.

################################################################

data_files = [ ('icon',['icon/Mordinator.ico','icon/newdataset.png','icon/analyze.png']),     
              ]

#data_files += mpl.get_py2exe_datafiles()
go_build = True
if go_build:
  setup(
      options = options,
      # The lib directory contains everything except the executables and the python dll.
      zipfile = zipfile,
      windows = [{'script':'MordinatorMain.py','icon_resources':[(1,'icon/Mordinator.ico')]}],
      # use out build_installer class as extended py2exe build command
      cmdclass = {"py2exe": build_installer},
      #package_dir={'libpy': 'libpy', 'gui':'gui'},
      #packages=['libpy','gui'],
      data_files=data_files,
      )
 

#setup(name="Modan",windows=['modan.py'],
#      package_dir={'libpy': 'libpy', 'gui':'gui'},
#      packages=['libpy','gui'],
#)