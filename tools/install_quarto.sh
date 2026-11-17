#!/usr/bin/env sh
# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
# Install Quarto into .tools/quarto (no root, nothing outside the repo).
# Skipped if .tools/quarto already has this version. Version checked 2026-11-16.
set -eu
VERSION="${QUARTO_VERSION:-1.11.9}"
DEST="$(cd "$(dirname "$0")/.." && pwd)/.tools/quarto"

if [ -x "$DEST/bin/quarto" ] && [ "$("$DEST/bin/quarto" --version)" = "$VERSION" ]; then
  echo "quarto $VERSION already in .tools/quarto"
  exit 0
fi

case "$(uname -s)-$(uname -m)" in
  Linux-x86_64)  ASSET="quarto-$VERSION-linux-amd64.tar.gz" ;;
  Linux-aarch64) ASSET="quarto-$VERSION-linux-arm64.tar.gz" ;;
  Darwin-*)      ASSET="quarto-$VERSION-macos.tar.gz" ;;
  *) echo "No Quarto download for $(uname -s)-$(uname -m). Install it yourself: https://quarto.org/docs/download/" >&2; exit 1 ;;
esac

URL="https://github.com/quarto-dev/quarto-cli/releases/download/v$VERSION/$ASSET"
echo "downloading $URL"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
curl -fsSL "$URL" -o "$TMP/quarto.tar.gz"
rm -rf "$DEST"
mkdir -p "$DEST"
tar -xzf "$TMP/quarto.tar.gz" -C "$DEST" --strip-components=1
echo "installed quarto $("$DEST/bin/quarto" --version) in .tools/quarto"
