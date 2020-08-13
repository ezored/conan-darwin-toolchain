from conan.packager import ConanMultiPackager


if __name__ == "__main__":
    builder = ConanMultiPackager()

    builder.add(settings={"os": "Macos", "arch": "x86_64"})
    builder.add(
        settings={"os": "Macos", "arch": "x86_64"},
        options={"darwin-toolchain:system_name": "Darwin"},
    )
    builder.add(settings={"os": "iOS", "os.version": "9.0", "arch": "armv8.3"})
    builder.add(settings={"os": "watchOS", "os.version": "4.0", "arch": "armv7k"})
    builder.add(settings={"os": "tvOS", "os.version": "11.0", "arch": "armv8"})

    builder.run()
