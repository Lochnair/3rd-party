#!/usr/bin/env python3

from pisi.actionsapi import pisitools, shelltools

def install():
    # Install main files to /opt
    # eopkg usually cd's into the first directory in the archive
    if shelltools.can_access_directory("browser"):
        # We are inside the 'zen' directory
        pisitools.insinto("/opt/zen-browser", "*")
        icon_path = "browser/chrome/icons/default/default%s.png"
    else:
        # We are one level up
        pisitools.insinto("/opt/zen-browser", "zen/*")
        icon_path = "zen/browser/chrome/icons/default/default%s.png"

    # Symlink to /usr/bin
    pisitools.dosym("/opt/zen-browser/zen", "/usr/bin/zen-browser")

    # Install icons
    for size in ["16", "32", "48", "64", "128"]:
        target_icon = icon_path % size
        if shelltools.can_access_file(target_icon):
            pisitools.insinto("/usr/share/icons/hicolor/%sx%s/apps" % (size, size),
                              target_icon, "zen-browser.png")
