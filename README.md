# Huawei Kirin 710 (Hi6250) GSI Universal Patcher (Android 10 - 15)

A standalone automated tool to patch, adapt, and build bootable Generic System Images (GSI) — including **AOSP, LineageOS, PixelExperience, CrDroid, Havoc-OS, DerpFest, and EvolutionX** — for Huawei and Honor devices powered by the **HiSilicon Kirin 710 chipset on EMUI 9.1 / Linux Kernel 4.9** (e.g., Huawei P30 Lite, Nova 4e, P Smart 2019, Honor 8X, Honor 10 Lite, Y9 2019).

---

## 🔗 Credits & Upstream References

The patches included in this toolchain are built upon the foundational work and research of the Project Treble community and Kirin custom ROM maintainers:

1. **[phhusson / treble_experimentations](https://github.com/phhusson/treble_experimentations)**
   - The creator of Project Treble GSI. Author of foundational runtime scripts (`rw-system.sh`, `phh-on-boot.sh`), automated VNDK detection logic, and legacy Huawei HAL shims.
2. **[TrebleDroid / treble_experimentations](https://github.com/TrebleDroid/treble_experimentations)**
   - The modern continuation of phh treble patches, bringing Treble compatibility to Android 13, 14, and 15, including eBPF and sepolicy adaptations.
3. **[Iceows / lineage_build_leaos](https://github.com/Iceows/lineage_build_leaos)**
   - Developer of LeaOS for Huawei Kirin devices (Kirin 710 / 659 / 970 / 980). Origin of the flattened VNDK 28 APEX runtime environment, `libfm-kirin-emui9` HAL shim, Kirin TrustZone (`teecd` / `/dev/dsm`) security patches, and EMUI 9.1 graphic buffer sync optimizations.

---

## 🚀 Quick Start Guide

### Step 1: Patch Any GSI Image
Run the Python script in your terminal (PowerShell, Command Prompt, or Linux/WSL) and pass the path to your raw or sparse GSI `.img`:

```powershell
python "C:\Users\----\Pictures\kirin_gsi_patcher.py" "C:\Path\To\your_gsi_image.img"
```

> **Note:** If executed without arguments, the script will interactively prompt you to enter the image path.

---

### Step 2: Flash via Fastboot
Once patching finishes (typically ~30–45 seconds), a fastboot-ready sparse image with the suffix `_kirin_fixed.img` is produced.

```powershell
# 1. Boot device into Fastboot mode (Hold Volume Down + Connect USB cable)
# 2. Flash the system partition
fastboot flash system "C:\Users\----\Pictures\system_patched_kirin_fixed.img"

# 3. Wipe user data and cache (Required when changing Android versions)
fastboot erase userdata
fastboot erase cache

# 4. Reboot device
fastboot reboot
```

---

## 🛠️ Implemented Patches & Fixes

This tool automatically applies 7 critical architectural adaptations required for Android 10–15 GSIs to boot smoothly on Kirin 710's Linux 4.9.148 kernel and EMUI 9.1 vendor partition:

| # | Root Cause in Stock GSI | Fix & Mechanism Applied | Upstream Origin |
| :--- | :--- | :--- | :--- |
| **1** | **Instant Reboot on Boot (`bpfloader-failed`)** | Neutralized `reboot_on_failure` in `/system/etc/init/bpfloader.rc`. Injected `bpf.progs_loaded=1` and `ro.kernel.ebpf.supported=false` so `netd` does not hang waiting for missing Linux 4.14+ eBPF map helpers. | TrebleDroid / Linux 4.9 Patch |
| **2** | **Missing EMUI 9.1 Vendor Libraries (VNDK 28)** | Injected complete flattened APEX directory at `/system/system_ext/apex/com.android.vndk.v28/`, allowing all Android 9 vendor HALs to resolve dependencies on modern Android 13/14/15. | Iceows LeaOS |
| **3** | **Kirin TrustZone Security Daemon Crash (`teecd`)** | Set mandatory node permissions (`chmod 0660 /dev/dsm` & `chown system:system /dev/dsm`) required by HiSilicon security firmware. | phhusson & Iceows |
| **4** | **Camera, Audio & Sensor HAL Crash (`libminijail`)** | Injected runtime bind-mount of VNDK 28 `libminijail.so` over `/vendor/lib64/libminijail_vendor.so` in `phh-on-boot.sh`. | phhusson Treble |
| **5** | **UI Glitches, Black Screen & Buffer Latency** | Appended Kirin 710 graphics optimizations to `build.prop` (`persist.kirin.alloc_buffer_sync=true`, `persist.kirin.texture_cache_opt=1`, etc.). | Iceows LeaOS |
| **6** | **Hardware Video Decode Failure** | Forced fallback to stable software media codecs (`setprop ctl.start media.swcodec`). | phhusson Treble |
| **7** | **Vendor Service Crashloop Protection** | Background daemon in `phh-on-boot.sh` stops looping proprietary vendor services after 30s to prevent battery drain and thermal throttling. | phhusson Treble |

---

## 📁 Package Structure
- `kirin_gsi_patcher.py`: Standalone Python tool automating unsparsing, resizing, patch injection, eBPF neutralization, and sparse generation.
- `kirin_patch_payload/`: Directory containing pre-compiled Kirin 64-bit binary HALs, flattened VNDK 28 APEX, Java framework JARs, and init scripts.
- `system_patched_kirin_fixed.img`: Tested, bootable, ready-to-flash Android 13 system image for Kirin 710.
- `README.md`: This technical documentation.
