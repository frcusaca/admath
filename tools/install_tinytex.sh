#!/usr/bin/env sh
# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
# Install TinyTeX (a small TeX Live) into .tools/TinyTeX for the PDF builds.
# No root, nothing outside the repo. Quarto finds it through PATH (the Makefile
# puts .tools/TinyTeX/bin/* first) and uses its tlmgr to fetch missing LaTeX
# packages on the first PDF render. Release checked 2026-11-16.
#
# Why not the system TeX? Debian's TeX Live may lack luaotfload-tool, so
# LuaLaTeX cannot load any OpenType font; XeLaTeX may be missing entirely.
set -eu
VERSION="${TINYTEX_VERSION:-v2026.11}"
DEST="$(cd "$(dirname "$0")/.." && pwd)/.tools/TinyTeX"

if [ -f "$DEST/.version" ] && [ "$(cat "$DEST/.version")" = "$VERSION" ]; then
  echo "TinyTeX $VERSION already in .tools/TinyTeX"
  exit 0
fi

case "$(uname -s)-$(uname -m)" in
  Linux-x86_64)  ASSET="TinyTeX-1-linux-x86_64-$VERSION.tar.xz" ;;
  Linux-aarch64) ASSET="TinyTeX-1-linux-arm64-$VERSION.tar.xz" ;;
  Darwin-*)      ASSET="TinyTeX-1-darwin-$VERSION.tar.xz" ;;
  *) echo "No TinyTeX download for $(uname -s)-$(uname -m). Run: quarto install tinytex" >&2; exit 1 ;;
esac

URL="https://github.com/rstudio/tinytex-releases/releases/download/$VERSION/$ASSET"
echo "downloading $URL"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
curl -fsSL "$URL" -o "$TMP/tinytex.tar.xz"
rm -rf "$DEST"
mkdir -p "$DEST"
tar -xJf "$TMP/tinytex.tar.xz" -C "$DEST" --strip-components=1
BIN="$(ls -d "$DEST"/bin/* | head -1)"
# TinyTeX is relocatable: no post-install steps. (Do not set tlmgr's sys_bin to
# this folder; `tlmgr path add` would then link every binary to itself.)
echo "$VERSION" > "$DEST/.version"
echo "installed TinyTeX $VERSION in .tools/TinyTeX ($BIN)"
