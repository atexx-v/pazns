#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/env.sh"

cd "$LAB7_QGC" || exit 1
APPIMAGE=QGroundControl-aarch64.AppImage
[ -f "$APPIMAGE" ] || { echo "Немає $LAB7_QGC/$APPIMAGE"; exit 1; }
chmod +x "$APPIMAGE"

if [ ! -x squashfs-root/AppRun ]; then
    ./"$APPIMAGE" --appimage-extract > "$LAB7_LOG/qgc_extract.log" 2>&1 || { echo "Не вдалося розпакувати AppImage"; exit 1; }
fi

GLIBC239="$LAB7_DIR/glibc239/usr/lib/aarch64-linux-gnu"
if [ ! -x "$GLIBC239/ld-linux-aarch64.so.1" ]; then
    mkdir -p "$LAB7_DIR/glibc239/debs" && cd "$LAB7_DIR/glibc239/debs" || exit 1
    BASE=http://ports.ubuntu.com/ubuntu-ports/pool/main
    for pkg in g/glibc/libc6_2.39-0ubuntu8.9_arm64.deb \
               "g/gcc-14/libstdc++6_14.2.0-4ubuntu2~24.04.1_arm64.deb" \
               "g/gcc-14/libgcc-s1_14.2.0-4ubuntu2~24.04.1_arm64.deb"; do
        curl -sSL --retry 5 -O "$BASE/$pkg" || { echo "Не вдалося завантажити $pkg"; exit 1; }
    done
    for deb in *.deb; do dpkg -x "$deb" "$LAB7_DIR/glibc239"; done
    cd "$LAB7_QGC" || exit 1
fi

sed 's#^exec "\$QGC_BINARY" "\$@"#GLIBC239="'"$GLIBC239"'"; LIBPATH="$GLIBC239:$LD_LIBRARY_PATH"; unset LD_LIBRARY_PATH LD_PRELOAD; exec "$GLIBC239/ld-linux-aarch64.so.1" --library-path "$LIBPATH" "$QGC_BINARY" "$@"#' \
    squashfs-root/AppRun > squashfs-root/AppRun_glibc239
chmod +x squashfs-root/AppRun_glibc239
grep -c "ld-linux-aarch64.so.1" squashfs-root/AppRun_glibc239 > /dev/null || { echo "Не вдалося створити AppRun_glibc239"; exit 1; }

echo "SHA-256 AppImage: $(sha256sum "$APPIMAGE" | cut -d' ' -f1)"
echo "Готово. Запуск: squashfs-root/AppRun_glibc239"
