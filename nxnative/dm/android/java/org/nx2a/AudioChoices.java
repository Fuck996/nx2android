package org.nx2a;

import android.media.AudioDeviceInfo;

final class AudioChoices {
    private AudioChoices() {}

    static String name(AudioDeviceInfo device, boolean chinese) {
        int type = device.getType();
        if (type == AudioDeviceInfo.TYPE_BUILTIN_SPEAKER) return (chinese ? "内置扬声器" : "Phone speaker");
        if (type == AudioDeviceInfo.TYPE_BLUETOOTH_A2DP || type == AudioDeviceInfo.TYPE_BLE_HEADSET || type == AudioDeviceInfo.TYPE_BLE_SPEAKER) {
            CharSequence product = device.getProductName();
            return product == null || product.toString().trim().isEmpty() ? (chinese ? "蓝牙音频" : "Bluetooth audio") : product.toString();
        }
        if (type == AudioDeviceInfo.TYPE_HDMI || type == AudioDeviceInfo.TYPE_HDMI_ARC || type == AudioDeviceInfo.TYPE_USB_DEVICE || type == AudioDeviceInfo.TYPE_USB_HEADSET)
            return (chinese ? "外部音频 · " : "External audio \u00B7 ") + device.getProductName();
        return null;
    }
}
