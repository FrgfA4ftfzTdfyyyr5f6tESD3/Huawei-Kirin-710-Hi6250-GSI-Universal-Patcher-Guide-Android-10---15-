#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
   Huawei Kirin 710 / EMUI 9.1 GSI Universal Patcher Tool (Android 10 - 15)
================================================================================
این اسکریپت هر ایمیج GSI خام (مانند AOSP, LineageOS, PixelExperience, Havoc) 
را برای گوشی‌های هواوی با پردازنده Kirin 710 پچ کرده و ایمیج نهایی بدون ریبوت 
و سازگار با Fastboot تولید می‌کند.
"""

import sys
import os
import struct
import subprocess
import time
from pathlib import Path

class Color:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

def log_info(msg):
    print(f"{Color.CYAN}[*]{Color.RESET} {msg}")

def log_success(msg):
    print(f"{Color.GREEN}[+]{Color.RESET} {msg}")

def log_warn(msg):
    print(f"{Color.YELLOW}[!]{Color.RESET} {msg}")

def log_err(msg):
    print(f"{Color.RED}[-]{Color.RESET} {msg}")

def is_sparse_image(file_path: str) -> bool:
    try:
        with open(file_path, "rb") as f:
            magic = struct.unpack("<I", f.read(4))[0]
            return magic == 0xed26ff3a
    except Exception:
        return False

def win_to_wsl_path(win_path: str) -> str:
    p = Path(win_path).resolve()
    drive = p.drive[0].lower()
    rest = p.as_posix()[2:].lstrip("/")
    return f"/mnt/{drive}/{rest}"

def main():
    print(f"{Color.BOLD}{'='*80}")
    print("   Huawei Kirin 710 GSI Universal Patcher (AOSP Android 10-15 -> Kirin EMUI 9)")
    print(f"{'='*80}{Color.RESET}\n")

    if len(sys.argv) < 2:
        print("نحوه استفاده:")
        print("  python kirin_gsi_patcher.py <input_gsi.img> [output_patched.img]\n")
        inp = input("لطفاً مسیر فایل GSI دلخواه (.img) را وارد کنید: ").strip('"').strip("'")
        if not inp or not os.path.exists(inp):
            log_err("فایل ورودی یافت نشد!")
            sys.exit(1)
        src_img = inp
    else:
        src_img = sys.argv[1].strip('"').strip("'")

    if not os.path.exists(src_img):
        log_err(f"فایل ورودی وجود ندارد: {src_img}")
        sys.exit(1)

    src_path = Path(src_img).resolve()
    if len(sys.argv) >= 3:
        dst_img = sys.argv[2].strip('"').strip("'")
    else:
        dst_img = str(src_path.parent / f"{src_path.stem}_kirin_fixed.img")

    script_dir = Path(__file__).resolve().parent
    payload_dir = script_dir / "kirin_patch_payload"
    if not payload_dir.exists():
        payload_dir = Path(r"C:\Users\----\Pictures\kirin_patch_payload")

    if not payload_dir.exists():
        log_err("پوشه پچ‌های اختصاصی کایرین (kirin_patch_payload) یافت نشد!")
        sys.exit(1)

    log_info(f"فایل GSI ورودی:  {src_path}")
    log_info(f"فایل نهایی خروجی: {dst_img}")
    log_info(f"مخزن پچ‌های کایرین: {payload_dir}\n")

    # بررسی و تبدیل Sparse به Raw در صورت نیاز
    is_sparse = is_sparse_image(str(src_path))
    raw_work_img = src_path.parent / f"{src_path.stem}_work_raw.img"

    if is_sparse:
        log_info("ایمیج ورودی از نوع Sparse است. در حال تبدیل به Raw EXT4...")
        wsl_src = win_to_wsl_path(str(src_path))
        wsl_raw = win_to_wsl_path(str(raw_work_img))
        subprocess.run(["wsl", "-d", "Ubuntu", "-u", "root", "-e", "simg2img", wsl_src, wsl_raw], check=True)
    else:
        log_info("ایمیج ورودی Raw است. در حال کپی به محیط کاری...")
        if str(src_path) != str(raw_work_img):
            import shutil
            shutil.copyfile(src_path, raw_work_img)

    wsl_raw_img = win_to_wsl_path(str(raw_work_img))
    wsl_payload = win_to_wsl_path(str(payload_dir))

    # اسکریپت تزریق پچ‌ها در WSL
    wsl_patch_cmd = f"""#!/bin/bash
set -e
IMG="{wsl_raw_img}"
PAYLOAD="{wsl_payload}"
MNT="/tmp/mnt_patch_work"

echo "[1/7] گسترش فضای فایل‌سیستم (+600MB)..."
e2fsck -fy "$IMG" || true
truncate -s +600M "$IMG"
resize2fs "$IMG"

echo "[2/7] مانت فایل‌سیستم..."
mkdir -p "$MNT"
umount "$MNT" 2>/dev/null || true
mount -o rw,loop "$IMG" "$MNT"

SYS="$MNT"
[ -d "$MNT/system/bin" ] && SYS="$MNT/system"

echo "[3/7] تزریق پوشه کامل Flattened VNDK 28 APEX..."
mkdir -p "$SYS/system_ext/apex"
cp -a "$PAYLOAD/apex/com.android.vndk.v28" "$SYS/system_ext/apex/"

echo "[4/7] تزریق کتابخانه‌ها و HALهای باینری کایرین..."
mkdir -p "$SYS/lib64" "$SYS/system_ext/lib64" "$SYS/framework" "$SYS/phh" "$SYS/bin" "$SYS/etc/init"
cp -a "$PAYLOAD/lib64/"* "$SYS/lib64/" 2>/dev/null || true
cp -a "$PAYLOAD/system_ext_lib64/"* "$SYS/system_ext/lib64/" 2>/dev/null || true
cp -a "$PAYLOAD/framework/"* "$SYS/framework/" 2>/dev/null || true
cp -a "$PAYLOAD/phh/"* "$SYS/phh/" 2>/dev/null || true
cp -a "$PAYLOAD/bin/"* "$SYS/bin/" 2>/dev/null || true
cp -a "$PAYLOAD/etc_init/"* "$SYS/etc/init/" 2>/dev/null || true

echo "[5/7] خنثی‌سازی دستور ریبوت bpfloader و اصلاح eBPF در کرنل 4.9..."
BPF_RC="$SYS/etc/init/bpfloader.rc"
if [ -f "$BPF_RC" ]; then
    # کامنت کردن دستور ریبوت در صورت خطای bpfloader
    sed -i 's/reboot_on_failure reboot,bpfloader-failed/# reboot_on_failure reboot,bpfloader-failed/g' "$BPF_RC"
    # تنظیم پرچم موفقیت لود bpf برای جلوگیری از قفل شدن netd
    if ! grep -q "setprop bpf.progs_loaded 1" "$BPF_RC"; then
        sed -i '/exec_start bpfloader/a \    setprop bpf.progs_loaded 1' "$BPF_RC"
    fi
fi

echo "[6/7] ثبت مقادیر بهینه‌ساز کایرین و غیرفعال‌سازی eBPF در build.prop..."
BUILD_PROP="$SYS/build.prop"
if [ -f "$BUILD_PROP" ]; then
    if ! grep -q "persist.kirin.alloc_buffer_sync" "$BUILD_PROP"; then
        cat << 'EOF' >> "$BUILD_PROP"

# ==========================================
# Huawei Kirin 710 GSI Compatibility Patches
# ==========================================
# 1. BPF / Network Compatibility for Linux 4.9
ro.kernel.ebpf.supported=false
ro.bpf.disabled=1
bpf.progs_loaded=1

# 2. Kirin 710 Graphics & Buffer Sync
persist.sys.phh.mainkeys=0
persist.sys.huawei.debug.on=0
persist.kirin.alloc_buffer_sync=true
persist.kirin.texture_cache_opt=1
persist.kirin.touch_move_opt=1
persist.kirin.touch_vsync_opt=1
persist.kirin.touchevent_opt=1
ro.kirin.config.hw_perfgenius=true
ro.kirin.config.hw_board_ipa=true

# 3. Audio & Sensor Drivers
persist.kirin.media.usbvoice.enable=true
persist.kirin.media.offload.enable=true
persist.kirin.media.hires.enable=true
persist.kirin.media.lowlatency.enable=true
persist.sys.phh.disable_sensor_direct_report=true
EOF
    fi
fi

echo "[7/7] تنظیم دسترسی‌های فایل‌های اجرایی..."
chmod -R 755 "$SYS/bin"
sync
umount "$MNT"
"""

    log_info("در حال اعمال پچ‌های کامل کایرین و خنثی‌سازی eBPF بر روی فایل‌سیستم...")
    res = subprocess.run(["wsl", "-d", "Ubuntu", "-u", "root", "-e", "bash", "-c", wsl_patch_cmd], capture_output=True, text=True)
    if res.returncode != 0:
        log_err(f"خطا در اعمال پچ‌ها:\n{res.stderr}")
        sys.exit(1)
    print(res.stdout)

    log_info("در حال تبدیل فایل نهایی به فرمت فشرده و استاندارد Fastboot Sparse...")
    wsl_dst = win_to_wsl_path(dst_img)
    subprocess.run(["wsl", "-d", "Ubuntu", "-u", "root", "-e", "img2simg", wsl_raw_img, wsl_dst], check=True)

    # پاکسازی فایل موقت Raw
    if raw_work_img.exists() and str(raw_work_img) != str(src_path):
        try:
            os.remove(raw_work_img)
        except Exception:
            pass

    log_success("عملیات با موفقیت پایان یافت!")
    print(f"\n{Color.GREEN}{Color.BOLD}فایل پچ‌شده و نهایی جهت فلش:{Color.RESET}")
    print(f"📁 {dst_img}\n")
    print("دستور فلش از طریق Fastboot:")
    print(f"{Color.CYAN}fastboot flash system \"{dst_img}\"{Color.RESET}\n")

if __name__ == "__main__":
    main()
