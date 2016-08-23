
try:
    import artifactory_utils
except:
    pass
else:
    dependencies = [
        artifactory_utils.ArtifactSelector(
            project="Toolchain-Release",
            revision="master",
            version="4.*",
            debug=False,
            stable_required=True),
        artifactory_utils.ArtifactSelector(
            project="linaro-linux-gnu",
            revision="master",
            version="4.9.0.0",
            debug=False,
            stable_required=True),
    ]
