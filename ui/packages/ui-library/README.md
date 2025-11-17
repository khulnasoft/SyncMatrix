# ui-library
This library is the Vue and Typescript component library for [Syncmatrix 2](https://github.com/KhulnaSoft/syncmatrix) and [Syncmatrix Cloud 2](https://www.khulnasoft.com/cloud/). _The components and utilities in this project are not meant to be used independently_. 

## Install
```
npm i @syncmatrix/ui-library --save --save-exact
```

## Developing with Syncmatrix UI

If you plan to develop against the Syncmatrix UI you can install the ui-library package locally.

We recommend using the cli and running

`npm i @syncmatrix/ui-library@../../ui-library --save`

in the Syncmatrix UI project where `../../ui-library` is the relative path from your Syncmatrix UI project’s directory to the ui-library project directory. You can also use an absolute path. 

If you have done this succesfully, you should see your Syncmatrix UI package.json and package-lock.json updated to show your local ui-library. 

<aside>
💡 Keep in mind this will update both the package.json and package-lock.json files. Be sure to not commit the changes to these two files.

💡 Linking a package this way is the safest as it avoids having to do an `npm i`.

</aside>

Then when linking ui-library to the syncmatrix/UI project you can do the following:

In ui-library (this repo):

`npm run dev`

In [ui](https://github.com/KhulnaSoft/syncmatrix/tree/main/ui):

`npm run serve`

Now any change you make in ui-library will trigger a reload in UI. 

## Update
To update a package in a project you can either install `latest` or a specific version like

```
npm i @syncmatrix/ui-library@latest --save --save-exact
```
OR
```
npm i @syncmatrix/ui-library@0.1.60 --save --save-exact
```

## Versioning
This project does not follow SEM versioning and major, minor, and patch updates mostly signify progress toward objectives. Breaking changes are introduced regularly without releasing a major version. For more information, see the [Syncmatrix versioning docs](https://docs.khulnasoft.com/contributing/versioning/)
