# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## [0.1.15] - 2025-04-10

### Changed

- Changed the LLMSettings schema for LLM proxy settings instead of Pulumi class

## [0.1.14] - 2025-04-07

### Added 

- Predictive Content Generator now uses a DataRobot LLM Blueprint
- LLM use is now optional
- Resource bundle config option for the custom model
- Improved error handling for package installations

### Changed

- Installed [the datarobot-pulumi-utils library](https://github.com/datarobot-oss/datarobot-pulumi-utils) to incorporate majority of reused logic in the `infra.*` subpackages.

## [0.1.13] - 2025-03-06

### Fixed 
- "Already Linked" issue
- "version name required" issue

## [0.1.12] - 2025-02-18

### Fixed
- Shap deployments now properly supported
- Remove hard-coded environment ID from LLM custom model

## [0.1.11] - 2025-02-10

### Fixed

- Frontend for binary classification deployments no longer misses prediction explanations

## [0.1.10] - 2025-01-15

### Fixed

- Codespace python env no longer broken by quickstart

### Changed

- Move pulumi entrypoint to the infra directory

## [0.1.9] - 2025-01-06

### Fixed

- quickstart.py now supports multiline values correctly
- quickstart now asks you to change the default project name
- quickstart now prints the application URL

### Changed

- Add python 3.9 requirement to README
- More detailed .env.template
- Change of LLM single code change
- More prominent LLM setting
- pulumi-datarobot bumped to 0.5.3
- Instructions to change the LLM in Readme adjusted to the new process
- Better exception handling around credential validation
- Update safe_dump to support unicode
- Sanitised input column names for the NBO data set

### Added

- Support for AWS Credential type and AWS-based LLM blueprints
- Full testing of the LLM credentials before start
  
## [0.1.8] - 2024-12-03

### Added

- add context tracing to this recipe.

### Changed

- update pulumi-datarobot to >=0.4.5
- Changed default target name to the buzok standard "resultText"
- improvements to the README
- Custom Metrics consolidated under `nbo/custom_metrics.py`
- add 3.9 compatibility check to mypy
- add pyproject.toml to store lint and test configuration
- Use Playground LLM instead of custom model for the generative deployment
- Use chat endpoint
- Removed temperature and llm model control to support change of LLM's
- Use python 3.12 app source environment

### Fixed

- Remove hardcoded endpoint in frontend project and deployment urls
- Fix comment handling in quickstart

## [0.1.7] - 2024-11-12

### Changed

- Bring release/10.2 in sync with main

## [0.1.6] - 2024-11-12

### Fixed

- Hide the Streamlit `deploy` button
- Ensure app settings update does not cause `pulumi up` to fail

### Changed

- Update DataRobot logo

## [0.1.5] - 2024-11-07

### Changed

- Bring release/10.2 in sync with main

## [0.1.4] - 2024-11-07

### Added

- quickstart.py script for getting started more quickly

## [0.1.3] - 2024-10-28

### Added

- Changelog file to keep track of changes in the project.
- Multi language support in frontend (Spanish, French, Japanese, Korean, Portuguese)
- Link Application, Deployment and Registered model to the use case in DR

### Removed

- datarobot_drum dependency to enable autopilot statusing from Pulumi CLI on first run
