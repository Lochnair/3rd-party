#!/usr/bin/env python3

# Created For Solus Operating System

from pisi.actionsapi import pisitools, shelltools

NoStrip = ["/opt", "/usr"]
IgnoreAutodep = True

def install():
    pisitools.insinto("/opt/antigravity", "*")
    pisitools.dosym("/opt/antigravity/antigravity", "/usr/bin/antigravity")

    # Install icon
    pisitools.insinto("/usr/share/icons/hicolor/512x512/apps", "resources/app/resources/linux/code.png", "antigravity.png")

    # Create desktop file
    shelltools.system("mkdir -p usr/share/applications")
    shelltools.echo("usr/share/applications/antigravity.desktop", """[Desktop Entry]
Name=Antigravity
Comment=Google Antigravity
Exec=/opt/antigravity/antigravity %F
Icon=antigravity
Type=Application
StartupNotify=true
Categories=Development;IDE;
MimeType=text/plain;
""")
    pisitools.insinto("/usr/share/applications", "usr/share/applications/antigravity.desktop")
