from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration

import os
import platform
import copy


class DarwinToolchainConan(ConanFile):
    name = "darwin-toolchain"
    version = "1.0.0"
    license = "Apple"
    settings = "os", "arch", "build_type"
    options = {
        "enable_bitcode": [True, False],
        "enable_arc": [True, False],
        "enable_visibility": [True, False],
    }
    default_options = {
        "enable_bitcode": True,
        "enable_arc": True,
        "enable_visibility": False,
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

    def config_options(self):
        # remove unsed options on Macos
        if self.settings.os == "Macos":
            del self.options.enable_bitcode
            del self.options.enable_arc
            del self.options.enable_visibility

    def configure(self):
        if platform.system() != "Darwin":
            raise ConanInvalidConfiguration("Build machine must be macOS")

        if not tools.is_apple_os(self.settings.os):
            raise ConanInvalidConfiguration("OS must be an Apple OS")

        if self.settings.os in ["watchOS", "tvOS"] and not self.options.enable_bitcode:
            raise ConanInvalidConfiguration(
                "Bitcode is required on watchOS/tvOS")

        if self.settings.os == "Macos" and self.settings.arch not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration(
                "macOS: Only supported archs: [x86, x86_64]"
            )

        if self.settings.os == "iOS" and self.settings.arch not in ["armv7", "armv7s", "armv8", "armv8.3", "x86", "x86_64"]:
            raise ConanInvalidConfiguration(
                "iOS: Only supported archs: [armv7, armv7s, armv8, armv8.3, x86, x86_64]"
            )

        if self.settings.os == "tvOS" and self.settings.arch not in ["armv8", "x86_64"]:
            raise ConanInvalidConfiguration(
                "tvOS: Only supported archs: [armv8, x86_64]"
            )

        if self.settings.os == "watchOS" and self.settings.arch not in ["armv7k", "armv8_32", "x86", "x86_64"]:
            raise ConanInvalidConfiguration(
                "watchOS: Only supported archs: [armv7k, armv8_32, x86, x86_64]"
            )

    def package(self):
        self.copy("darwin-macos-toolchain.cmake")
        self.copy("darwin-ios-toolchain.cmake")

    def package_info(self):
        darwin_arch = tools.to_apple_arch(self.settings.arch)

        if self.settings.os == "Macos":
            xcrun = tools.XCRun(self.settings)
            sysroot = xcrun.sdk_path

            self.cpp_info.sysroot = sysroot

            common_flags = ["-isysroot%s" % sysroot]

            if self.settings.get_safe("os.version"):
                common_flags.append(tools.apple_deployment_target_flag(
                    self.settings.os, self.settings.os.version)
                )

            # CMake issue, for details look https://github.com/conan-io/conan/issues/2378
            cflags = copy.copy(common_flags)
            cflags.extend(["-arch", darwin_arch])
            self.cpp_info.cflags = cflags
            link_flags = copy.copy(common_flags)
            link_flags.append("-arch %s" % darwin_arch)

            self.cpp_info.sharedlinkflags.extend(link_flags)
            self.cpp_info.exelinkflags.extend(link_flags)

            # Set flags in environment too, so that CMake Helper finds them
            cflags_str = " ".join(cflags)
            ldflags_str = " ".join(link_flags)
            self.env_info.CC = xcrun.cc
            self.env_info.CPP = "%s -E" % xcrun.cc
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

            if self.settings.get_safe("os.version"):
                self.env_info.CONAN_CMAKE_DEPLOYMENT_TARGET = str(
                    self.settings.os.version
                )

            self.env_info.CONAN_CMAKE_ARCH = str(darwin_arch)
            self.env_info.CONAN_CMAKE_SYSROOT = sysroot
            self.env_info.CONAN_CMAKE_TOOLCHAIN_FILE = os.path.join(
                self.package_folder, "darwin-macos-toolchain.cmake"
            )
        else:
            if self.settings.get_safe("os.version"):
                self.env_info.CONAN_CMAKE_DEPLOYMENT_TARGET = str(
                    self.settings.os.version
                )

            self.env_info.CONAN_CMAKE_ARCH = str(darwin_arch)
            self.env_info.CONAN_CMAKE_PLATFORM = self._os_to_platform()

            self.env_info.CONAN_CMAKE_TOOLCHAIN_FILE = os.path.join(
                self.package_folder, "darwin-ios-toolchain.cmake"
            )

            self.env_info.CONAN_CMAKE_ENABLE_BITCODE = self._bool_to_str(
                self.options.enable_bitcode
            )

            self.env_info.CONAN_CMAKE_ENABLE_ARC = self._bool_to_str(
                self.options.enable_arc
            )

            self.env_info.CONAN_CMAKE_ENABLE_VISIBILITY = self._bool_to_str(
                self.options.enable_visibility
            )

    def package_id(self):
        self.info.header_only()

    def _bool_to_str(self, value):
        return "1" if value == True else "0"

    def _os_to_platform(self):
        if self.settings.os == "iOS" and self.settings.arch in ["armv7", "armv7s", "armv8", "armv8.3"]:
            return 'OS'

        if self.settings.os == "iOS" and self.settings.arch in ["x86"]:
            return 'SIMULATOR'

        if self.settings.os == "iOS" and self.settings.arch in ["x86_64"]:
            return 'SIMULATOR64'

        if self.settings.os == "tvOS" and self.settings.arch in ["armv8"]:
            return 'TVOS'

        if self.settings.os == "tvOS" and self.settings.arch in ["x86_64"]:
            return 'SIMULATOR_TVOS'

        if self.settings.os == "watchOS" and self.settings.arch in ["armv7k", "armv8_32"]:
            return 'WATCHOS'

        if self.settings.os == "watchOS" and self.settings.arch in ["x86", "x86_64"]:
            return 'SIMULATOR_WATCHOS'

        raise Exception("Invalid OS")
