
# conan-darwin-toolchain

[![conan](https://github.com/ezored/conan-darwin-toolchain/actions/workflows/conan.yml/badge.svg)](https://github.com/ezored/conan-darwin-toolchain/actions/workflows/conan.yml)

Toolchain required to cross build to any darwin platform.

## Setup

This package **REQUIRES** Xcode to be installed.

In the future, it might be added as a build_requirement.

Add the following repository to conan find it:

```
conan remote add ezored https://ezoredrepository.jfrog.io/artifactory/api/conan/conan-local
```

Create a profile for cross building and including this toolchain, example:

### iOS

Create a file called **ios_profile** with content:
    
```
include(default)

[settings]
os=iOS
os.version=9.0
arch=armv7

[build_requires]
darwin-toolchain/1.5.0@ezored/stable
```
    
Go to your project and cross-build your dependency tree with this toolchain:

`conan install . --profile ios_profile`

### Other platforms

This toolchain works with every darwin platform (macOS/iOS/tvOS/watchOS).

You only need to create a slightly different profile, example:

**watchOS**


```
include(default)

[settings]
os=watchOS
os.version=5.0
arch=armv8_32

[build_requires]
darwin-toolchain/1.5.0@ezored/stable
```

**tvOS**

```
include(default)

[settings]
os=tvOS
os.version=11.0
arch=armv8

[build_requires]
darwin-toolchain/1.5.0@ezored/stable
```

**macOS catalyst**

```
include(default)

[settings]
os=Macos
os.subsystem=catalyst
arch=x86_64

[build_requires]
darwin-toolchain/1.5.0@ezored/stable
```

## Bitcode support

Bitcode is an option available on iOS, it is **required** on tvOS/watchOS.

It is set by default to `True`.

So you can only set it to `False` for iOS. Note that it is not defined for macOS.

## Local development

1. Install python packages:  
```pip install conan_package_tools bincrafters_package_tools```
2. Clone the project:  
```git clone https://github.com/ezored/conan-darwin-toolchain.git```
3. Enter on project folder:  
```cd conan-darwin-toolchain```
4. Install:  
```conan create . ezored/stable```
5. Build:  
```python build.py```  
or  
```rm -rf test_package/build/ && python build.py```  
6. Check all generated files:  
```find test_package/build -name hello -exec lipo -info {} \;```
7. To install it as local package:  
```conan export-pkg . darwin-toolchain/1.5.0@ezored/stable -f```