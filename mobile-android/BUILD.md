# Build Instructions for Yamato Android App

## Prerequisites

- Android Studio Hedgehog (2023.1.1) or later
- JDK 17 or later
- Android SDK 34
- Minimum 8GB RAM (16GB recommended)

## Quick Start

### 1. Open in Android Studio

```bash
# Clone the repository
git clone https://github.com/essaie-creator/yamato-phonetic-transcriber.git
cd yamato-phonetic-transcriber/mobile-android

# Open in Android Studio
studio .
```

### 2. Sync Gradle

Android Studio will automatically sync Gradle dependencies. Wait for sync to complete.

### 3. Build APK

**Debug Build:**
```bash
./gradlew assembleDebug
```

APK location: `app/build/outputs/apk/debug/app-debug.apk`

**Release Build:**
```bash
./gradlew assembleRelease
```

APK location: `app/build/outputs/apk/release/app-release.apk`

## Signing Release APK

For distribution, you need to sign the release APK:

### 1. Generate Keystore

```bash
keytool -genkey -v -keystore yamato-release-key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias yamato
```

### 2. Configure Signing

Create `gradle.properties` in project root:

```properties
YAMATO_RELEASE_STORE_FILE=yamato-release-key.jks
YAMATO_RELEASE_KEY_ALIAS=yamato
YAMATO_RELEASE_STORE_PASSWORD=your_password
YAMATO_RELEASE_KEY_PASSWORD=your_password
```

Update `app/build.gradle.kts`:

```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("YAMATO_RELEASE_STORE_FILE") ?: "yamato-release-key.jks")
            storePassword = System.getenv("YAMATO_RELEASE_STORE_PASSWORD")
            keyAlias = System.getenv("YAMATO_RELEASE_KEY_ALIAS")
            keyPassword = System.getenv("YAMATO_RELEASE_KEY_PASSWORD")
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            // ... other config
        }
    }
}
```

## Huawei Device Testing

### Enable Developer Mode on Huawei

1. Settings → About Phone
2. Tap "Build Number" 7 times
3. Go back to Settings → System & Updates → Developer Options
4. Enable "USB Debugging"

### Install APK on Huawei

```bash
# Connect device via USB
adb devices

# Install debug APK
adb install app/build/outputs/apk/debug/app-debug.apk

# Or use Huawei HiSuite for wireless installation
```

## Troubleshooting

### Gradle Sync Failed

```bash
# Clean and rebuild
./gradlew clean
./gradlew build --refresh-dependencies
```

### SDK Not Found

Update `local.properties`:
```properties
sdk.dir=/path/to/Android/sdk
```

### Out of Memory

Increase Gradle heap in `gradle.properties`:
```properties
org.gradle.jvmargs=-Xmx4096m -XX:MaxPermSize=1024m
```

## Performance Optimization

### Enable R8 Full Mode

In `gradle.properties`:
```properties
android.enableR8.fullMode=true
```

### Split APKs by ABI

Modify `app/build.gradle.kts`:
```kotlin
splits {
    abi {
        isEnable = true
        reset()
        include("armeabi-v7a", "arm64-v8a", "x86_64")
        isUniversalApk = true
    }
}
```

## Continuous Integration

### GitHub Actions Workflow

Create `.github/workflows/android-build.yml`:

```yaml
name: Android CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up JDK 17
      uses: actions/setup-java@v3
      with:
        java-version: '17'
        distribution: 'temurin'
    
    - name: Grant execute permission
      run: chmod +x gradlew
    
    - name: Build with Gradle
      run: ./gradlew build
    
    - name: Run tests
      run: ./gradlew test
    
    - name: Build APK
      run: ./gradlew assembleDebug
    
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: app-debug
        path: app/build/outputs/apk/debug/app-debug.apk
```

## Distribution

### Google Play Store

1. Create signed release APK or AAB
2. Prepare store listing
3. Submit for review

### Huawei AppGallery

1. Register as Huawei developer
2. Create signed APK
3. Submit through AppGallery Connect

### Direct APK Distribution

Share APK via:
- GitHub Releases
- Website download
- QR code for direct install

## License

MIT License - See main project LICENSE
