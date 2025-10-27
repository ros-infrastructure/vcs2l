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

## 2. Tagging the release and automated publishing
* After merging the PR, create a new tag for the repository using the following commands:

   ```bash
   git checkout main
   git tag x.y.z
   git push origin x.y.z
   ```
* Pushing the tag will automatically create a GitHub release with assets - `*.whl` and `*.tar.gz`.
  The release notes will be generated automatically based on the merged PRs since the last release.

* This would also publish the package onto PyPI with the newly created version.
