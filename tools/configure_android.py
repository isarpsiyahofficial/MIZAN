from pathlib import Path

manifest = Path("android/app/src/main/AndroidManifest.xml")
text = manifest.read_text(encoding="utf-8")
text = text.replace('android:label="lefferion_prime_mizan"', 'android:label="LEFFERION PRIME - MIZAN"')
permissions = """    <uses-permission android:name=\"android.permission.POST_NOTIFICATIONS\" />
    <uses-permission android:name=\"android.permission.RECEIVE_BOOT_COMPLETED\" />
    <uses-permission android:name=\"android.permission.SCHEDULE_EXACT_ALARM\" />
"""
if "android.permission.POST_NOTIFICATIONS" not in text:
    text = text.replace("<manifest xmlns:android=\"http://schemas.android.com/apk/res/android\">", "<manifest xmlns:android=\"http://schemas.android.com/apk/res/android\">\n" + permissions)
receivers = """
        <receiver android:exported=\"false\" android:name=\"com.dexterous.flutterlocalnotifications.ScheduledNotificationReceiver\" />
        <receiver android:exported=\"false\" android:name=\"com.dexterous.flutterlocalnotifications.ScheduledNotificationBootReceiver\">
            <intent-filter>
                <action android:name=\"android.intent.action.BOOT_COMPLETED\" />
                <action android:name=\"android.intent.action.MY_PACKAGE_REPLACED\" />
                <action android:name=\"android.intent.action.QUICKBOOT_POWERON\" />
                <action android:name=\"com.htc.intent.action.QUICKBOOT_POWERON\" />
            </intent-filter>
        </receiver>
"""
if "ScheduledNotificationReceiver" not in text:
    text = text.replace("    </application>", receivers + "    </application>")
manifest.write_text(text, encoding="utf-8")

build = Path("android/app/build.gradle.kts")
text = build.read_text(encoding="utf-8")
if "isCoreLibraryDesugaringEnabled" not in text:
    text = text.replace("    compileOptions {", "    compileOptions {\n        isCoreLibraryDesugaringEnabled = true")
if "coreLibraryDesugaring(" not in text:
    text += """

dependencies {
    coreLibraryDesugaring(\"com.android.tools:desugar_jdk_libs:2.1.5\")
}
"""
build.write_text(text, encoding="utf-8")
