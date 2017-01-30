#!/usr/bin/python

# Created For Solus Operating System

from pisi.actionsapi import get, pisitools, shelltools

NoStrip = ["/usr"]
IgnoreAutodep = True

InstallDir = get.installDIR()
PkgName = get.srcNAME()
Version = get.srcVERSION()

def setup():
    shelltools.system("mkdir crashplan")
    shelltools.system("cd crashplan; zcat ../CrashPlan_" + Version + ".cpi | cpio -i")

    shelltools.system("sed -i 's/^$ENGINE_SCRIPT stop.*/systemctl stop crashplan >> $logfile 2>\&1/g' 'crashplan/bin/restartLinux.sh'")
    shelltools.system("sed -i 's/^$ENGINE_SCRIPT start.*/systemctl start crashplan >> $logfile 2>\&1/g' 'crashplan/bin/restartLinux.sh'")
    shelltools.system("sed -i 's|Exec=.*|Exec=/opt/" + PkgName + "/bin/CrashPlanDesktop|' 'scripts/CrashPlan.desktop'")
    shelltools.system("sed -i 's|Icon=.*|Icon=crashplan|' 'scripts/CrashPlan.desktop'")

def install():
    pisitools.insinto("/opt/", "crashplan")
    shelltools.system("chmod -R g-w " + InstallDir + "/opt/crashplan")
    shelltools.system("chmod 777 " + InstallDir + "/opt/crashplan/log")

    for size in ['16x16', '32x32', '64x64', '128x128']:
        pisitools.insinto("/usr/share/icons/hicolor/" + size + "/apps/", "crashplan/skin/icon_app_" + size + ".png", "crashplan.png")

    pisitools.doexe("scripts/CrashPlanDesktop", "/opt/" + PkgName + "/bin/")
    pisitools.doexe("scripts/CrashPlanEngine", "/opt/" + PkgName + "/bin/")
    pisitools.insinto("/opt/" + PkgName + "/bin/", "scripts/run.conf")
    pisitools.insinto("/usr/share/applications/", "scripts/CrashPlan.desktop", "crashplan.desktop")
