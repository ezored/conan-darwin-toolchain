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
    builder.add(
        settings={"os": "Macos", "os.version": "10.15", "arch": "x86_64"},
        options={"darwin-toolchain:enable_catalyst": True},
    )
    builder.add(
        settings={"os": "Macos", "os.version": "10.15", "arch": "x86_64"},
        options={
            "darwin-toolchain:enable_catalyst": True,
            "darwin-toolchain:catalyst_version": "13.0",
        },
    )

    builder.run()
