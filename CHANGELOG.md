# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
