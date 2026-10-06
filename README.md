# Claude Desktop - rpm for Fedora and Enterprise Linux (x86_64, aarch64)

An RPM spec file that, if you build it, downloads Anthropic's official Linux build of Claude Desktop (the Debian package of its apt repository) and repackages it as an RPM, so that you can install and run Claude Desktop on Fedora, CentOS Stream, RHEL and their rebuilds.

Status: as of 2.19675.1 the spec repackages the official `.deb` as is (native Electron, native modules and Claude Code helpers), instead of patching the Windows package as earlier versions did. The download is checked against the SHA-256 published in the signed index of Anthropic's apt repository. Tested on CentOS Stream 10 x86_64 with KDE Plasma, including the third-party inference mode configured in `/etc/claude-desktop/managed-settings.json`. Claude Cowork needs QEMU/KVM and is not covered here.

## Build requirements

prereqs for building:

```
sudo dnf install rpm-build rpmdevtools binutils tar xz desktop-file-utils
```

build the RPM:
```
spectool -g -R claude-desktop.spec
rpmbuild -bb claude-desktop.spec
```
The resulting RPM will be in `~/rpmbuild/RPMS/$ARCH/` and can get installed with:

```
ARCH=$(uname -m)
sudo dnf install ~/rpmbuild/RPMS/$ARCH/claude-desktop-*.rpm
```

## Alternative: Use `mock`

The `mock` tool provides a sandbox that allows building rpms in a clean chroot without polluting the host. It also allows to target different distro versions.

prereqs for building:

```
sudo dnf install mock rpmdevtools
```
build the RPM:

```
spectool -g -R claude-desktop.spec

mock --spec claude-desktop.spec --sources "$(rpm --eval '%{_sourcedir}')"
```

The resulting RPM will be in `/var/lib/mock/<os>-<os-version>-<arch>/result/` and can get installed with:

```
sudo dnf install "$(mock -p)/../result/claude-desktop-$(rpmspec -q --qf '%{VERSION}-%{RELEASE}' claude-desktop.spec).$(uname -m).rpm"
```

And optionally cleanup after building:

```
rpmbuild --rmsource claude-desktop.spec
mock --clean
```

## Updating to a new release

Anthropic's apt repository lists every release with its checksum:

```
curl -fsS https://downloads.claude.ai/claude-desktop/apt/stable/dists/stable/main/binary-amd64/Packages | awk '/^Version:/{v=$2} /^SHA256:/{print v, $2}' | sort -V | tail -1
curl -fsS https://downloads.claude.ai/claude-desktop/apt/stable/dists/stable/main/binary-arm64/Packages | awk '/^Version:/{v=$2} /^SHA256:/{print v, $2}' | sort -V | tail -1
```

Pick a version published for both architectures, then update `claude_version`, `sha256_amd64` and `sha256_arm64` in the spec.

## Disclaimer

This is an educational project. Use at your own risk. The closed-source Claude Desktop binaries are not part of this repo and if you want to use them be aware of the terms and licenses that apply.
