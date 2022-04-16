# Nasuta's [Achaea](https://www.achaea.com/) Package Tools

## Usage

Just run the script! (by default `./achpkg.py`)
**Note:** Currently expects Python3 to be installed.

```
└──╼ ./achpkg.py 

    Nasuta's Achaea Packaging Tools
    ===============================

    1. Extract a package into files and folders
    2. Compile files and folders into a package
    3. Quit

    Your choice? 1

    Enter the path to your package: examples/nexMap version 1.4.nxs

    Enter the path to store the result: nexmap

    Overwrite the target directory? (Y/n) y
```

Extracting (option 1) takes either a [Mudlet](https://www.mudlet.org/) `.xml`
or [Nexus](https://nexus.ironrealms.com/) `.nxs` package and extracts it into
a directory of your choice with a file and folder structure mimicking what it
would have in its native client.

Code is extracted into editable `.js` files and `.json` config (which you are
**NOT** meant to edit) which can then be re-compiled (option 2) into a
hopefully working `.nxs` package.

```
└──╼ tree nexmap
nexmap
├── alias19.js
├── alias19.json
├── Aliases
│   ├── alias50.js
│   ├── alias50.json
│   ├── alias76.js
│   └── alias76.json
├── Functions
│   ├── customTabs_function.js
│   ├── customTabs_function.json
│   ├── onGMCP_function.js
│   └── onGMCP_function.json
├── onLoad_function.js
├── onLoad_function.json
├── README_function.js
├── README_function.json
└── Triggers
    ├── Anti Universe Area_trigger.js
    ├── Anti Universe Area_trigger.json
    ├── Farsee
    │   ├── trigger41.js
    │   ├── trigger41.json
    │   ├── trigger59.js
    │   ├── trigger59.json
    │   ├── trigger60.js
    │   └── trigger60.json
    ├── Gags
    │   ├── trigger33.js
    │   ├── trigger33.json
    │   ├── trigger35.js
    │   ├── trigger35.json
    │   ├── trigger36.js
    │   ├── trigger36.json
    │   ├── trigger37.js
    │   ├── trigger37.json
    │   ├── trigger38.js
    │   ├── trigger38.json
    │   ├── trigger43.js
    │   ├── trigger43.json
    │   ├── trigger58.js
    │   ├── trigger58.json
    │   ├── trigger68.js
    │   └── trigger68.json
    ├── trigger40.js
    ├── trigger40.json
    ├── trigger62.js
    ├── trigger62.json
    ├── trigger65.js
    ├── trigger65.json
    ├── trigger74.json
    ├── trigger75.js
    ├── trigger75.json
    ├── Universe Tarot_trigger.js
    └── Universe Tarot_trigger.json

5 directories, 49 files
```

## EXPERIMENTAL FEATURES

Mudlet `lua` is currently 'transpiled' into JavaScript. This is a work in
progress and will still need a lot of manual intervention to produce something
working.

Mudlet `.mpackage` files are currently unsupported, but will be at some point
in the near future.
