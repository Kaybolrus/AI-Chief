import subprocess
import sys
import os
import glob

WAKELOCK_CONTENT = """group 'dev.fluttercommunity.plus.wakelock'
version '1.0'
buildscript {
    repositories { google(); mavenCentral() }
    dependencies { classpath 'com.android.tools.build:gradle:7.3.0' }
}
rootProject.allprojects {
    repositories { google(); mavenCentral() }
}
apply plugin: 'com.android.library'
android {
    namespace 'dev.fluttercommunity.plus.wakelock'
    compileSdkVersion 35
    sourceSets { main.java.srcDirs += 'src/main/kotlin' }
    defaultConfig { minSdkVersion 21; targetSdkVersion 35 }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
}
dependencies { implementation 'androidx.annotation:annotation:1.1.0' }
"""

def patch_all():
    for path in glob.glob("/tmp/**/wakelock_plus*/android/build.gradle", recursive=True):
        if "example" not in path:
            open(path, "w").write(WAKELOCK_CONTENT)
            print(f"Patched: {path}")
    for path in glob.glob(os.path.expanduser("~/.pub-cache/**/wakelock_plus*/android/build.gradle"), recursive=True):
        if "example" not in path:
            open(path, "w").write(WAKELOCK_CONTENT)
            print(f"Patched: {path}")
    for path in glob.glob("/tmp/**/android/app/build.gradle", recursive=True):
        content = open(path).read()
        content = content.replace("compileSdkVersion 34", "compileSdkVersion 35")
        content = content.replace("compileSdk = 34", "compileSdk = 35")
        open(path, "w").write(content)
        print(f"App patched: {path}")

if __name__ == "__main__":
    patch_all()
    result = subprocess.run(sys.argv[1:])
    sys.exit(result.returncode)
