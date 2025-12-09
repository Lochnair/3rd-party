#!/usr/bin/env python3
# Created For Solus Operating System

from pisi.actionsapi import get, pisitools, shelltools

NoStrip = ["/opt", "/usr"]
IgnoreAutodep = True

# Only needed if you decide to use e.g. "<version>-1" in Source filename;
# kept for parity with enpass/google-chrome examples.
Suffix = "-1"


def setup():
    # Upstream tarball, e.g.
    # https://downloads.1password.com/linux/tar/stable/x86_64/1password-8.11.22.x64.tar.gz
    tarball = "1password-%s.x64.tar.gz" % get.srcVERSION()
    shelltools.system("pwd")
    shelltools.system("tar xvf %s" % tarball)


def install():
    srcdir = "1password-%s.x64" % get.srcVERSION()

    # chrome-sandbox needs to be setuid root (Chromium/Electron classic)
    shelltools.system("chown root:root %s/chrome-sandbox" % srcdir)
    shelltools.system("chmod 4755 %s/chrome-sandbox" % srcdir)

    # Install main payload into /opt/1Password
    # Result: /opt/1Password/{1password,resources,...}
    pisitools.insinto("/opt", srcdir, "1Password")

    # Symlink CLI entry into /usr/bin
    pisitools.dosym("/opt/1Password/1password", "/usr/bin/1password")

    # Install icons (match what the PKGBUILD does)
    for i in ["32", "64", "256", "512"]:
        size = "%sx%s" % (i, i)
        icon_src = "%s/resources/icons/hicolor/%s/apps/1password.png" % (srcdir, size)
        icon_dest = "/usr/share/icons/hicolor/%s/apps" % size
        pisitools.insinto(icon_dest, icon_src, "1password.png")

    # Desktop file
    pisitools.insinto(
        "/usr/share/applications",
        "%s/resources/1password.desktop" % srcdir
    )

    # Optional: ship the custom_allowed_browsers example like AUR does
    pisitools.insinto(
        "/usr/share/doc/1password/examples",
        "%s/resources/custom_allowed_browsers" % srcdir
    )
