# HPT - Health Policy Testbed

## Overview


The overall architecture of the system is a Python model and Flask service, hosting a static ReactJS based UI.

## Quick Start Guide
(note: script snippets below reflect MacOS/Linux/Unix terminal style, and may need to be adjusted for Windows usage)

### Setting up Python

Python 3 is required.

To run the UI, `flask` is required, which can be installed by running:
```
hpt $ pip3 install flask
```

### Running The Model

Command Line Version
```
hpt $ python3 cli.py [-p policyFile] [-n numberOfPatients]
```

Web Version
```
hpt $ FLASK_APP=server.py flask run
```


### Setting up for UI development
The UI is compiled down to static HTML/JS which is served from the `./static` directory. To 

Requirements:
 - Node.js
 - Yarn

```
hpt $ pip3 install flask_cors
hpt $ cd ui
ui $ yarn install
```

To run the UI in development mode:
```
ui $ yarn start
```
This will allow you to make changes and have them reflected automatically, without having to manually rebuild and copy the files each time.

To rebuild the static version of the UI:
```
ui $ yarn build
ui $ cd ..
hpt $ rm -rf static
hpt $ mv ui/build static
```
Then re-run the server.

## Adding New Policy Settings
* [ ] Add the policy description to the UI
  * Add a new entry to the `POLICY_OPTIONS` object in `./ui/src/utils.js`, formatted per below guidelines
  * If the new policy setting is not a plain text string, boolean (true/false), or number, additional supporting infrastructure will need to be added to the framework in `./ui/src/App.js`
(out of scope for this checklist)  
  * `POLICY_OPTIONS` format:
```js
'Human Friendly Name on UI': {
  type: 'number', 'text', or 'boolean'
  min: the minimum allowed value, if type is number
  max: the maximum allowed value, if type is number
  defaultValue: default value for the field
  exportName: the variable name to be used within the python model (mandatory)
  exportFn: function to convert the display value to the export value. for some reason numbers all need to be converted to Numbers -- see existing examples in code
}
```
* [ ] Rebuild the static version of the UI as described above
* [ ] Add the policy setting to the model
  * Reference the policy setting as a field within the `policySettings` object, using the same variable name set in `POLICY_OPTIONS.exportName` above. 
  * For example, if in the UI `exportName` above was set to "customSettingX", this setting should be referenced as `policySettings.customSettingX`. It will be a string, boolean, or number as appropriate based on the setting above
* [ ] Add a default value for this setting in the default policy file `./policies/default.json`
  * This should use the same name as the `exportName` above, and should be the same default value as defined in `defaultValue` above
  * Example:
```json
{
  "MedicareAge": 65,
  "MedicaidIncomeElig": 1.38,
  "customSettingX": 1234
}
```

## License