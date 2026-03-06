# GitHub Actions Release Guide

This document explains how to use GitHub Actions to automatically build and release your Yamato Phonetic Transcriber project.

## Overview

GitHub Actions is a CI/CD platform that allows you to automate builds, tests, and deployments directly from your GitHub repository. **It's 100% free for public repositories**.

This project includes two automated workflows:

1. **Android Build & Release** - Builds Android APKs for Huawei and other Android devices
2. **Python Package Build & Release** - Builds Python packages and source archives

## How It Works

```
You create a tag → GitHub Actions triggers → Builds run in the cloud → Binaries attached to Release
```

All builds happen on GitHub's servers - **you don't need to use your own computer**.

## Workflow Files

### 1. Android Release (`.github/workflows/android-release.yml`)

**Triggered by:** Tags matching `v*-android` or `v*-mobile`

**What it does:**
- Sets up JDK 17
- Builds Debug APK
- Builds Release APK (unsigned)
- Uploads both APKs as artifacts
- Creates a GitHub Release with APKs attached

**Example tags:**
- `v1.0.0-android`
- `v1.2.3-mobile`
- `v2.0.0-beta-android`

### 2. Python Release (`.github/workflows/python-release.yml`)

**Triggered by:** All tags starting with `v*` (except Android tags)

**What it does:**
- Sets up Python 3.10
- Installs build dependencies
- Builds Python package (wheel and sdist)
- Creates source code ZIP archive
- Creates a GitHub Release with all files attached

**Example tags:**
- `v1.0.0`
- `v1.2.3-beta`
- `v2.0.0-rc1`

## How to Create a Release

### Step 1: Make Your Changes

Ensure all your code changes are committed and pushed to GitHub:

```bash
git add .
git commit -m "Prepare for release v1.0.0"
git push origin main
```

### Step 2: Create a Tag

**For Android/Huawei Release:**
```bash
git tag v1.0.0-android
git push origin v1.0.0-android
```

**For Python Release:**
```bash
git tag v1.0.0
git push origin v1.0.0
```

**For Pre-release (Beta/Alpha):**
```bash
git tag v1.0.0-beta-android
git push origin v1.0.0-beta-android
```

### Step 3: Wait for GitHub Actions

1. Go to your repository on GitHub
2. Click on the **"Actions"** tab
3. You'll see the workflow running (green checkmark or yellow dot)
4. Wait for it to complete (usually 5-15 minutes)

### Step 4: Check the Release

Once the workflow completes:

1. Go to the **"Releases"** section (right sidebar)
2. Click on your new release tag
3. You'll see the built files under **"Assets"**

**Android releases will include:**
- `app-debug.apk` - For testing
- `app-release-unsigned.apk` - For distribution (needs signing)

**Python releases will include:**
- `yamato_phonetic_transcriber-*.whl` - Wheel package
- `yamato_phonetic_transcriber-*.tar.gz` - Source distribution
- `yamato-phonetic-transcriber-v*.zip` - Source code archive

## Signing Android APKs for Production

The automatic build creates **unsigned** release APKs. For production distribution:

### Option 1: Manual Signing (Recommended for First Releases)

1. Download the unsigned APK from the release
2. Sign it locally using Android Studio or `jarsigner`
3. Re-upload to the release manually

### Option 2: Automated Signing (Advanced)

Store your keystore passwords as GitHub Secrets:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:
   - `YAMATO_RELEASE_STORE_FILE` (base64 encoded keystore)
   - `YAMATO_RELEASE_STORE_PASSWORD`
   - `YAMATO_RELEASE_KEY_ALIAS`
   - `YAMATO_RELEASE_KEY_PASSWORD`

Then modify the workflow to sign the APK automatically.

## Troubleshooting

### Build Failed

1. Click on the failed workflow in the Actions tab
2. Read the error logs
3. Common issues:
   - Missing `gradlew` file: Ensure `mobile-android/gradlew` exists and is executable
   - JDK version mismatch: The workflow uses JDK 17
   - Out of memory: GitHub runners have 7GB RAM

### No Assets in Release

- Check if the workflow completed successfully
- Verify the tag name matches the pattern (`v*-android` or `v*`)
- Check the workflow logs for upload errors

### Want to Re-run a Build

1. Go to the Actions tab
2. Click on the workflow run
3. Click **"Re-run jobs"** button

## Advanced Usage

### Triggering Manual Builds

You can modify workflows to allow manual triggering:

```yaml
on:
  workflow_dispatch:  # Adds a "Run workflow" button
  push:
    tags:
      - "v*"
```

### Building for Specific Platforms

Create separate workflows for:
- Huawei AppGallery (AAB format)
- Google Play Store (signed AAB)
- Different Android API levels

### Publishing to Package Registries

Add steps to publish automatically to:
- PyPI (Python Package Index)
- Google Play Console
- Huawei AppGallery Connect

## Benefits of Automated Releases

✅ **Consistent builds** - Same environment every time  
✅ **No local setup needed** - Builds in the cloud  
✅ **Versioned artifacts** - Every release has downloadable binaries  
✅ **Audit trail** - Complete build history in GitHub  
✅ **Free for open source** - No cost for public repositories  
✅ **Automatic changelog** - Release notes generated from commits  

## Next Steps

1. Test the workflow with a beta tag: `git tag v0.1.0-test-android`
2. Monitor the build in the Actions tab
3. Download and test the APK on a Huawei device
4. Create your first production release!

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Android CI/CD Best Practices](https://developer.android.com/studio/build/building-cmdline)
- [softprops/action-gh-release](https://github.com/softprops/action-gh-release)

---

**Need help?** Open an issue on GitHub or check the workflow logs for detailed error messages.
