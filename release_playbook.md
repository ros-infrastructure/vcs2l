# Release Playbook

This playbook outlines the steps to release a new version of the `vcs2l` project. It includes tasks for updating version tags, generating changelogs, and publishing the release to GitHub.

## 1. Release PR

### Creation steps
* Create the PR with the branch name - `github-username/release-x.y.z` where `x.y.z` is the new version number.
* Update the version tag in [`vcs2l/__init__.py`](./vcs2l/__init__.py) file.
* Update the [Changelog](CHANGELOG.rst) to include all the PRs merged since the last release. Also update the contributors involved in this release.
* Make sure that this is done with the commit message as `x.y.z`.
* Push the changes and create a PR against the `main` branch.

### Merging steps
* Make sure to rebase the PR if the `main` branch has moved ahead:
   ```bash
   git fetch origin main
   git checkout github-username/release-x.y.z
   git rebase origin/main
   git push --force-with-lease origin github-username/release-x.y.z
   ```

* Upon approval, use the following commands to merge the PR:

   ```bash
   git checkout main
   git merge --ff-only github-username/release-x.y.z
   git push origin main
   ```

## 2. Tagging the release
After merging the PR, create a new tag for the release using the following commands:

```bash
git checkout main
git tag x.y.z
git push origin x.y.z
```

## 3. Publishing the release on GitHub
* Navigate to the [Releases](https://github.com/ros-infrastructure/vcs2l/releases/new) page, and select the tag you just pushed.
* Fill in the release title as `x.y.z`.
* Create the release notes by using the `Generate release notes` button.
* Publish the release by setting it as the latest release.
* This will automatically trigger the GitHub Actions workflow to publish the package to PyPI.
