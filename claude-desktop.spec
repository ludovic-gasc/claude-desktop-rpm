%global claude_version 2.19675.1
# SHA-256 of each .deb, from the Packages index of Anthropic's signed apt
# repository (dists/stable/main/binary-<arch>/Packages).
%global sha256_amd64   9ba127eeccf270f6e60d35f5c5333654053bf0540c88fc82a009d01711b106fc
%global sha256_arm64   681d122ae97d0eb302f0e6d92c7f232847064bb01746458dc50a2c095a40ed12

# Prebuilt Electron app: nothing to strip, no debuginfo, and no build-id
# links that would clash with other Electron apps.
%global debug_package  %{nil}
%global __os_install_post %{nil}
%global _build_id_links none

Name:           claude-desktop
Version:        %{claude_version}
Release:        1%{?dist}
Summary:        Claude Desktop for Linux
License:        Proprietary
URL:            https://claude.com/download/

# Anthropic's official Linux build, repackaged as is.
%global deb_pool https://downloads.claude.ai/claude-desktop/apt/stable/pool/main/c/claude-desktop
Source0:        %{deb_pool}/claude-desktop_%{claude_version}_amd64.deb
Source1:        %{deb_pool}/claude-desktop_%{claude_version}_arm64.deb

ExclusiveArch:  aarch64 x86_64
# The bundled libraries (libffmpeg.so, libvulkan.so.1…) are private to the
# app: neither provide nor require them.
AutoReqProv:    no

BuildRequires:  binutils
BuildRequires:  tar
BuildRequires:  xz
BuildRequires:  desktop-file-utils

# Debian dependencies of the .deb, by their Fedora/EL names.
Requires:       gtk3
Requires:       libnotify
Requires:       nss
Requires:       xdg-utils
Requires:       at-spi2-core
Requires:       libdrm
Requires:       mesa-libgbm
Requires:       libxcb
Requires:       libsecret
Requires:       libXtst
Requires:       libuuid
Requires:       pipewire-libs
Requires:       xdg-desktop-portal
Requires:       (xdg-desktop-portal-kde or xdg-desktop-portal-gtk or xdg-desktop-portal-gnome)
Recommends:     alsa-lib
Recommends:     ca-certificates

%description
Claude Desktop for Linux: Anthropic's official Linux build (the Debian
package of its apt repository), repackaged as an RPM.

# ---------------------------------------------------------------------------
# %%prep — check and unpack the Debian package
# ---------------------------------------------------------------------------
%prep
%ifarch x86_64
%global deb_source %{SOURCE0}
%global deb_sha256 %{sha256_amd64}
%else
%global deb_source %{SOURCE1}
%global deb_sha256 %{sha256_arm64}
%endif
echo "%{deb_sha256}  %{deb_source}" | sha256sum --check --strict
rm -rf deb data
mkdir deb data
cd deb
ar x %{deb_source}
tar -xf data.tar.* -C ../data

# ---------------------------------------------------------------------------
# %%build — nothing to compile
# ---------------------------------------------------------------------------
%build

# ---------------------------------------------------------------------------
# %%install
# ---------------------------------------------------------------------------
%install
cp -a data/. %{buildroot}/
# Chromium's setuid sandbox helper, as in the .deb (tar drops the bit when
# not run as root).
chmod 4755 %{buildroot}/usr/lib/claude-desktop/chrome-sandbox
# Debian-only metadata.
rm -rf %{buildroot}%{_datadir}/lintian
# The .deb's postinst copies these into place; ship them as files instead.
_res=%{buildroot}/usr/lib/claude-desktop/resources
install -Dm644 "$_res"/gnome-search-provider/com.anthropic.Claude.search-provider.ini \
    %{buildroot}%{_datadir}/gnome-shell/search-providers/com.anthropic.Claude.search-provider.ini
install -Dm644 "$_res"/gnome-search-provider/com.anthropic.Claude.SearchProvider.service \
    %{buildroot}%{_datadir}/dbus-1/services/com.anthropic.Claude.SearchProvider.service
# Launchers: /usr/bin/claude-desktop, and the `ccd` terminal launcher when
# the build ships one (same link as the postinst).
echo %{_bindir}/claude-desktop > bin.files
if [ -x "$_res"/bin/ccd ]; then
    ln -s ../lib/claude-desktop/resources/bin/ccd %{buildroot}%{_bindir}/ccd
    echo %{_bindir}/ccd >> bin.files
fi
desktop-file-validate %{buildroot}%{_datadir}/applications/com.anthropic.Claude.desktop
# The postinst also writes an AppArmor profile (EL uses SELinux) and
# registers the apt repository: neither applies to an RPM.

# ---------------------------------------------------------------------------
%files -f bin.files
%dir /usr/lib/claude-desktop
/usr/lib/claude-desktop/*
%{_datadir}/applications/com.anthropic.Claude.desktop
%{_datadir}/icons/hicolor/*/apps/claude-desktop.png
%{_datadir}/gnome-shell/search-providers/com.anthropic.Claude.search-provider.ini
%{_datadir}/dbus-1/services/com.anthropic.Claude.SearchProvider.service
%doc %{_docdir}/claude-desktop

%post
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :
touch -h %{_datadir}/icons/hicolor >/dev/null 2>&1 || :
update-desktop-database %{_datadir}/applications || :

%postun
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :
update-desktop-database %{_datadir}/applications || :

%changelog
* Wed Oct 07 2026 Claude Desktop Linux Maintainers - 2.19675.1-1
- update to Claude Desktop 2.19675.1
- repackage Anthropic's official Linux build (the .deb of its apt repository,
  checked against the SHA-256 of the signed index) instead of patching the
  Windows package: native Electron, claude-native and node-pty, so the
  third-party inference configuration (/etc/claude-desktop/managed-settings.json)
  is read
- builds on EL 10 as well as Fedora (no 7-Zip, npm or compiler needed)
- escape the macros in comments (rpm 4.19 rejects "%%install" in a comment)

* Tue Sep 22 2026 Claude Desktop Linux Maintainers - 2.2553.1-1
- update to Claude Desktop 2.2553.1
- update Electron from 41.6.1 to 44.2.0, node-pty to 1.2.0-beta.14
- source the Squirrel nupkg from the release feed instead of the hashed installer exe
- apply the main-process patches across the new split index.chunk-*.js bundle
- fetch the electron runtime explicitly (electron 42 dropped its postinstall hook)
- ship the Linux pty.node inside the asar header so it can be required

* Wed Jun 10 2026 Claude Desktop Linux Maintainers - 1.11847.5-1
- update to Claude Desktop 1.11847.5

* Tue Jun 09 2026 Claude Desktop Linux Maintainers - 1.11187.4-1
- update to Claude Desktop 1.11187.4
- update Electron from 40.4.1 to 41.6.1
- drop bundled claude-ssh binaries (now downloaded at runtime by the app)
- copy new ion-dist resource bundle into the app
- build node-pty for Linux so Claude Code "run in terminal" works
- disable the system tray on Linux (unreliable across desktops; app now quits on window close)

* Sat Feb 21 2026 Claude Desktop Linux Maintainers - 1.1.3918-1
- update to Claude Desktop 1.1.3918

* Fri Feb 20 2026 Claude Desktop Linux Maintainers - 1.1.3770-1
- update to Claude Desktop 1.1.3770
- claude-ssh binaries now included in Windows installer, macOS DMG no longer needed

* Sun Feb 15 2026 Claude Desktop Linux Maintainers - 1.1.3189-1
- update to Claude Desktop 1.1.3189
- update Electron from 39.5.0 to 40.4.1
- add claude-ssh binaries from macOS DMG for SSH remote feature

* Thu Feb 12 2026 Claude Desktop Linux Maintainers - 1.1.2685-1
- update to Claude Desktop 1.1.2685

* Sun Feb 08 2026 Claude Desktop Linux Maintainers - 1.1.2321-1
- update to Claude Desktop 1.1.2321
