#!/usr/bin/env bash
#
# Builds pynzbget's source and binary RPMs. Run inside one of the
# docker-compose.yml containers (tox -e rpm does this for you).
#
# - Uses the source package in dist/ (tox -e build-sdist makes it)
# - Puts the finished RPMs in dist/rpm/<distribution>/
#
set -euo pipefail

SRC_DIR="${SRC_DIR:-/pynzbget}"
SPEC="$SRC_DIR/packaging/redhat/python-nzbget.spec"

# Keep rpmbuild's work folders out of the source tree
TOP_DIR="$(mktemp -d)"
OUT_DIR="$SRC_DIR/dist/rpm/${DIST:-unknown}"

# Find the source package that matches the spec file's version
VERSION=$(rpmspec -q --qf "%{version}\n" "$SPEC" | head -n1)
TARBALL="$SRC_DIR/dist/pynzbget-${VERSION}.tar.gz"

if [[ ! -f "$TARBALL" ]]; then
    echo "Source package not found: $TARBALL"
    echo "Run 'tox -e build-sdist' first, and check the spec's Version:"
    exit 1
fi

echo "==> Checking the spec file"
rpmlint "$SPEC" || true

echo "==> Building RPMs for ${DIST:-unknown}"
mkdir -p "$TOP_DIR/SOURCES" "$OUT_DIR"
cp "$TARBALL" "$TOP_DIR/SOURCES/"

rpmbuild --define "_topdir $TOP_DIR" \
         --define "_srcrpmdir $OUT_DIR" \
         --define "_rpmdir $OUT_DIR" \
         -ba "$SPEC"

rm -rf "$TOP_DIR"

echo "==> Done:"
find "$OUT_DIR" -type f -name "*.rpm"
