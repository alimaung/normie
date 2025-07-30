# Flatirons Styles project
This project contains Flatirons styling (logo, icons and corresponding fonts). 

Refer details: https://wiki.flatironssolutions.com/display/ENGOPS/DDL+-+Flatirons+Icon+Font

# Versioning - Flatirons Icon Font
When doing any changes to this repo please update `package.json` version. This repo contains both Flatirons logos and icon font.

Please follow these rules when updating logos or icon font:
* if you add/remove/update image under `logo` directory please increment the minor version (second digit) in package.json version:
  * e.g. current version is `3.1.6`, you add a new image `FS-Logo-small.png` to `/logo` directory, update the version to `3.2.6`
* if you add new version of the icon font please increment the patch version (third digit) in package.json version:
  * e.g. current version is `3.1.6`, you add a new icon font with name `Flatirons-DDL_Icon-Font-v307`, update the version to `3.1.7`
* if you add both icon font and logo, then please increment  minor (second digit) and patch (third digit) version  in package.json
  * e.g. current version is `3.1.6`, you add a new image `FS-Logo-small.png` to `/logo` directory and a new icon font with name `Flatirons-DDL_Icon-Font-v307`, update the version to `3.2.7`

# Usage
Lets say, you wanted to add Flatirons Stlyes in your project (say Pinpoint Client),
# Bower
* In bower.json, update flatironsstyles.git url - so that, flatironsstyles are added as dependency to your project.
* Update your task runners - gulp or grunt - to add these styles and font to distributables.

# NPM 
* Run `npm install @flatirons/flatirons-styles@<version> -S` - this will add as dependency.

# Author
Any clarification on icons - please reach out to `Ann Criqui` [Ann.Criqui@FlatironsSolutions.com]

