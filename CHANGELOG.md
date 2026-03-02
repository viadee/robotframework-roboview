# Change Log

All notable changes to the "roboview" extension will be documented in this file.

Check [Keep a Changelog](http://keepachangelog.com/) for recommendations on how to structure this file.

## [Unreleased]

- Initial release

## [0.0.3] - 2026-03-02
### Added
- Fixed suite setup and teardown keywords are now included correctly
- Refactored existing webviews using Shadcn components and applied several visual improvements including:
  - Added collapsible sections across all three webviews
  - Adjusted font and badge colors
  - Implemented table pagination in the main content area
  - Ensured VS Code theme compatibility
  - Added several tooltips for more information
- Several maintenance improvements and internal enhancements to keep the extension up to date. 
  - Updated README
  - Updated server port from 8000 to 18123 (less used than 8000)
  - Updated project dependencies to latest versions
  - Refactored keyword similarity without numpy and scikit-learn (backend size is now just around 20 MB instead of 300MB before)
  - Added support for additional libraries including all BuiltIn libraries (Collections, DateTime etc.), Appium and Requests
  - Migrated to Robocop v8.2.2 (code changes were necessary)