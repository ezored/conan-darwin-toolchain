from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration

import os
import platform
import copy


class DarwinToolchainConan(ConanFile):
    name = "darwin-toolchain"
    version = "1.1.0"
    license = "Apple"
    settings = "os", "arch", "build_type"
    options = {
        "enable_bitcode": [True, False, None],
        "enable_arc": [True, False, None],
        "enable_visibility": [True, False, None],
        "enable_catalyst": [True, False],
        "catalyst_version": "ANY",
    }
    default_options = {
        "enable_bitcode": None,
        "enable_arc": None,
        "enable_visibility": None,
        "enable_catalyst": False,
        "catalyst_version": "13.0",
    }
    description = "Darwin toolchain to (cross) compile macOS/iOS/watchOS/tvOS"
    url = "https://github.com/ezored/conan-darwin-tooolchain"
    build_policy = "missing"
    exports_sources = "*.cmake"

    @property
    def cmake_system_name(self):
        if self.settings.os == "Macos":
            return "macOS"
        return str(self.settings.os)

    @property
    def cmake_system_processor(self):
        return {
            "x86": "i386",
            "x86_64": "x86_64",
            "armv7": "arm",
            "armv8": "aarch64",
        }.get(str(self.settings.arch))

    def config_options(self):
        if self.settings.os == "Macos":
            self.options.enable_bitcode = None

        if self.settings.os == "watchOS":
            self.options.enable_bitcode = True

        if self.settings.os == "tvOS":
            self.options.enable_bitcode = True

    def configure(self):
        if platform.system() != "Darwin":
            raise ConanInvalidConfiguration("Build machine must be Macos")

        if not tools.is_apple_os(self.settings.os):
            raise ConanInvalidConfiguration("OS must be an Apple OS")

        if self.settings.os in ["watchOS", "tvOS"] and not self.options.enable_bitcode:
            raise ConanInvalidConfiguration("Bitcode is required on watchOS/tvOS")

        if self.settings.os == "Macos" and self.settings.arch not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration(
                "macOS: Only supported archs: [x86, x86_64]"
            )

        if self.settings.os == "iOS" and self.settings.arch not in [
            "armv7",
            "armv7s",
            "armv8",
            "armv8.3",
            "x86",
            "x86_64",
        ]:
            raise ConanInvalidConfiguration(
                "iOS: Only supported archs: [armv7, armv7s, armv8, armv8.3, x86, x86_64]"
            )

        if self.settings.os == "tvOS" and self.settings.arch not in ["armv8", "x86_64"]:
            raise ConanInvalidConfiguration(
                "tvOS: Only supported archs: [armv8, x86_64]"
            )

        if self.settings.os == "watchOS" and self.settings.arch not in [
            "armv7k",
            "armv8_32",
            "x86",
            "x86_64",
        ]:
            raise ConanInvalidConfiguration(
                "watchOS: Only supported archs: [armv7k, armv8_32, x86, x86_64]"
            )

    def package(self):
        self.copy("darwin-toolchain.cmake")

    def package_info(self):
        darwin_arch = tools.to_apple_arch(self.settings.arch)

        if self.options.enable_catalyst == True:
            self.output.info("Catalyst enabled: YES")
        else:
            self.output.info("Catalyst enabled: NO")

        # Common things
        xcrun = tools.XCRun(self.settings)
        sysroot = xcrun.sdk_path

        self.cpp_info.sysroot = sysroot

        common_flags = ["-isysroot%s" % sysroot]

        if self.options.enable_catalyst != True:
            if self.settings.get_safe("os.version"):
                deployment_target_flag = tools.apple_deployment_target_flag(
                    self.settings.os, self.settings.os.version
                )

                self.output.info(
                    "Deployment target: {0}".format(deployment_target_flag)
                )

                common_flags.append(deployment_target_flag)

        # Bitcode
        if self.options.enable_bitcode == "None":
            self.output.info("Bitcode enabled: IGNORED")
        else:
            if self.options.enable_bitcode:
                if self.settings.build_type == "Debug":
                    common_flags.append("-fembed-bitcode-marker")
                    self.env_info.CMAKE_XCODE_ATTRIBUTE_BITCODE_GENERATION_MODE = (
                        "bitcode"
                    )
                    self.output.info("Bitcode enabled: YES")
                else:
                    common_flags.append("-fembed-bitcode")
                    self.env_info.CMAKE_XCODE_ATTRIBUTE_ENABLE_BITCODE = "NO"
                    self.output.info("Bitcode enabled: YES")

        # ARC
        if self.options.enable_arc == "None":
            self.output.info("ObjC ARC enabled: IGNORED")
        else:
            if self.options.enable_arc:
                common_flags.append("-fobjc-arc")
                self.env_info.CMAKE_XCODE_ATTRIBUTE_CLANG_ENABLE_OBJC_ARC = "YES"
                self.output.info("ObjC ARC enabled: YES")
            else:
                common_flags.append("-fno-objc-arc")
                self.env_info.CMAKE_XCODE_ATTRIBUTE_CLANG_ENABLE_OBJC_ARC = "NO"
                self.output.info("ObjC ARC enabled: NO")

        # Visibility
        if self.options.enable_visibility == "None":
            self.output.info("Visibility enabled: IGNORED")
        else:
            if self.options.enable_visibility:
                self.env_info.CMAKE_XCODE_ATTRIBUTE_GCC_SYMBOLS_PRIVATE_EXTERN = "NO"
                self.output.info("Visibility enabled: YES")
            else:
                common_flags.append("-fvisibility=hidden")
                self.env_info.CMAKE_XCODE_ATTRIBUTE_GCC_SYMBOLS_PRIVATE_EXTERN = "YES"
                self.output.info("Visibility enabled: NO")

        # CMake issue, for details look https://github.com/conan-io/conan/issues/2378
        cflags = copy.copy(common_flags)
        cflags.extend(["-arch", darwin_arch])

        self.cpp_info.cflags = cflags
        link_flags = copy.copy(common_flags)
        link_flags.append("-arch %s" % darwin_arch)

        if self.options.enable_catalyst == True:
            cflags.extend(["-target", "%s-apple-ios-macabi" % darwin_arch])
            cflags.extend(["-miphoneos-version-min=%s" % self.options.catalyst_version])

            link_flags.extend(["-target", "%s-apple-ios-macabi" % darwin_arch])
            link_flags.extend(
                ["-miphoneos-version-min=%s" % self.options.catalyst_version]
            )

        self.cpp_info.sharedlinkflags.extend(link_flags)
        self.cpp_info.exelinkflags.extend(link_flags)

        # Set flags in environment too, so that CMake Helper finds them
        cflags_str = " ".join(cflags)
        ldflags_str = " ".join(link_flags)

        self.env_info.CC = xcrun.cc
        self.env_info.CPP = "%s -E" % xcrun.cxx
        self.env_info.CXX = xcrun.cxx
        self.env_info.AR = xcrun.ar
        self.env_info.RANLIB = xcrun.ranlib
        self.env_info.STRIP = xcrun.strip

        self.env_info.CFLAGS = cflags_str
        self.env_info.ASFLAGS = cflags_str
        self.env_info.CPPFLAGS = cflags_str
        self.env_info.CXXFLAGS = cflags_str
        self.env_info.LDFLAGS = ldflags_str

        self.env_info.CONAN_CMAKE_SYSTEM_NAME = self.cmake_system_name

        # Deployment target
        if self.options.enable_catalyst != True:
            if self.settings.get_safe("os.version"):
                self.env_info.CONAN_CMAKE_OSX_DEPLOYMENT_TARGET = str(
                    self.settings.os.version
                )

                self.output.info(
                    "CMake deployment target: {0}".format(str(self.settings.os.version))
                )

        self.env_info.CONAN_CMAKE_OSX_ARCHITECTURES = str(darwin_arch)
        self.output.info("Architecture: {0}".format(str(darwin_arch)))

        # Sysroot
        self.env_info.CONAN_CMAKE_OSX_SYSROOT = sysroot
        self.output.info("Sysroot: {0}".format(sysroot))

        # Toolchain
        self.env_info.CONAN_CMAKE_SYSTEM_PROCESSOR = self.cmake_system_processor

        self.env_info.CONAN_CMAKE_TOOLCHAIN_FILE = os.path.join(
            self.package_folder, "darwin-toolchain.cmake"
        )

    def package_id(self):
        self.info.header_only()
