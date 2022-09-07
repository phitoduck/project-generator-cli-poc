# RFC for `template-generator-cli` (name TBD)

Discussion and reactions to this RFC belong [in this issue](https://github.com/phitoduck/project-generator-cli-poc/issues/1).

## Executive Summary

Here, we propose a tool that makes Python software development and deployment as frictionless as possible--both for individuals and for teams.

## Movivations

- Python packaging is hard
  - There are many tools, templates, frameworks, build chains, linters, etc. It's overwhelming to get started.

## Philosophies

*Philosophies* are statements of opinion that we must agree upon. An *Implementation* will not be considered
valid unless it can be shown to satisfy the philosophies.

- #TemplatesAreEvil 
    - Templates get stale over time
    - A process should exist so that projects are always up to date
- ... but they are helpful:
    - In the overwhelming space of Python software development, starting from an opinionated framework helps learn best practices with minimal cognitive load.
- ... but they often lack desirable features, outside the scope of generating code:
    - Writing/releasing production-worthy code requires infrastructure (i.e. GitHub account/repo). These
    tools also have a non-trivial learning curve that should be automated where possible.
- Automation eliminates avoidable errors caused by manual steps
- The average use should not have to learn the entire Python ecosystem--thanks to abstractions.
- The advanced user should be able to extend the abstractions; you should not need to "grow out" of the tool.
- Where possible, we should avoid rebuilding what has already been built/standardized on by the community.
- The iteration cycle should be fast:
    - developers should be able to run builds locally
    - processes that can be run in parallel should be run in parallel (both locally and in CI)
- Released software and docs should be immutable. Once package `v0.0.0` is out there,
  consumers of the software should be able to rely on the fact that it won't disappear and that the behavior
  won't change.
- The tool should be built with both open- and closed-source development in mind.
- The trunk-based development branching model should have first-class support.
- Multi-project repositories (mono-repos) have a place in modern software development, and should be supported to an extent (e.g. `frontend` and `backend` projects, or `src` and `iac` might reside in one repository)
    - ... but the framework should encourage developers to modularize projects in separate repos as much as possible

## Implementation

### Note 1:

Think of this proposal as defining an interface. We don't *need* a `Makefile`, but having
some sort of CLI interface is an example of how we might satisfy the philosophy of 
developers being able to run builds locally.

### Note 2:

while commands like `precommit autoupdate`, `cz bump`, and `cs changelog` *could* be moved
into `template-generator-cli`, they could also be called outside of `template-generator-cli`. 

Advantage: in GitHub actions,
we could have those commands be parallel steps. That way they could be parallelized accross multiple
GitHub actions workers, each with their own CPU, rather than be parallelized on a single worker
with one CPU. 

### Component: CLI tool

```bash
# create a properly configured repository with GitHub secrets for publishing to PyPI
template-generator-cli new --publish-to github --pypi-config-file ~/.tg/credentials
```

### Component: Config file

This is inspired by `projen`. We may even use `projen` for the final implementation.

This file would be executed by the ``template-generator-cli``.

```python
from template_cli_tool import AwesomeProjectTemplate, PyPIConfig, SphinxConfig

# would result in a pyproject.toml, setup.cfg, setup.py, Pipfile, Pipfile.lock, makefile, .github/ folder, etc.
project = AwesomeProjectTemplate(
    pypi=PyPIConfig(
        url="https://your.private.pypi.server.com",
        # these secrets would be created and populated in the GitHub (or Bitbucket, etc.) repo
        pypi_username_env_var="PYPI_USER",
        pypi_password_env_var="PYPI_PASSWORD",
    ),
    install_requires=[
        "pandas>=9.9.9",
    ],
    extras_require={
        "test": ["pytest", "pytest-cov"],
        "docs": ["sphinx"],
    },
    # no more MANIFEST.in headaches!
    inlude_assets_at_fpaths=[
        "**.json",
        "**.csv",
    ],
    sphinx=SphinxConfig(
        plugins=[
            "copybutton",
            "furo" # cool Material UI theme 😎
        ],
        backend=SphinxConfig.backends.S3StaticSite(
            bucket_name="docs.yourproject.com",
            # these would be GitHub secrets, possibly placed by the CLI if you give it your aws credentials file
            aws_secret_key_id__secret="AWS_SECRET_KEY_ID",
            aws_secret_key__secret="AWS_SECRET_ACCESS_KEY",
        ),
    ),
    # generate a Pipfile and Pipfile.lock
    lock_dependencies=True,
)



# generate files and their contents based on the config file
project.render()
```

### Component: `makefile`

```makefile
# WARNING! DO NOT MODIFY THIS FILE! This file is autogenerated by template-generator-cli. 
# Customizations can be made by modifying the .template-generator-cli-config.py file 
# in the root of this repository.

test:
    echo "Not implemented"

# update the template-generator-cli-managed project files and build the project for distribution
build:
    aws codeartifact login ... # authenticate with our private pypi server

    # update the project template using the latest version of template-generator-cli
    # NOTE: several commands below also mutate files, those could be moved
    #       into this CLI tool
    pipx run --index-url "https://your.private.pypi.server.com" \
        template-generator-cli update-project-in-place

    # (mutates files) update .pre-commit.config.yml with latest versions of code quality tools
    pipx run precommit autoupdate

    # run code quality tools (linters, formatters, etc.) with max parallelism
    pipx run precommit run --all-files

    # (mutates file) autogenerate CHANGELOG from "conventional commit" compliant commit messages
    pipx run --spec "commitizen==latest" \
        cz changelog

    # (mutates file) derive semver from "conventional commit" compliant commit messages and bump version.txt 
    pipx run --spec "commitizen==latest" \
        cz bump

    # build the docs
    pipx run --index-url "https://your.private.pypi.server.com" \
        --spec "easy-sphinx-docs-cli==latest" \
        easy-sphinx-docs-cli build

    # build the .whl and .tgz versions of the python package
    git tag $(cat version.txt)
    pipx run build


# publish built artifacts including docs and the python package
release:
    aws codeartifact login ... # authenticate with our private pypi server

    # update the project in place; imagine that this command includes
    # "precommit autoupdate; cz changelog; cz bump"; fail if any changes
    # are made to any files when running this--a diff would mean that
    # a developer modified a restricted file by hand and not via the template-generator-cli
    # config file
    pipx run --index-url "https://your.private.pypi.server.com" \
        template-generator-cli update-project-in-place --fail-if-diff

    # make sure this is a new version being released; "git push --tags"
    # fails if the tags already exist in the remote
    git tag $(cat version.txt) "latest"
    git push --tags

    # publish the docs
    pipx run --index-url "https://your.private.pypi.server.com" \
        --spec "easy-sphinx-docs-cli==latest" \
        easy-sphinx-docs-cli publish

    # publish the python package (.whl and .tgz files)
    pipx run twine upload ./dist/*
```


### Implementation Features

- If linting config files are present locally (`.pylintrc`, `.flake8`, etc.) then
  editors like VS Code an PyCharm can be configured to use them real time. This
  means you can make linting fixes as you develop instead of having to wait until
  a PR is submitted.
- Projects never go out of date from their template.
- version and CHANGELOG are automatically updated (reduced merge conflicts dramatically over manual editing)
- The pre-commit framework allows 
