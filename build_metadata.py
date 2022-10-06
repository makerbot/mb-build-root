
try:
    import artifactory_utils
except:
    pass
else:
    dependencies = [
        artifactory_utils.ArtifactSelector(
            project="Toolchain-Release",
            revision="ReleaseMorepork1.12",
            version="^4.6",
            debug=False,
            stable_required=True),
        artifactory_utils.ArtifactSelector(
            project="linaro-linux-gnu",
            revision="master",
            version="5.3.1.0",
            debug=False,
            stable_required=True),
    ]
