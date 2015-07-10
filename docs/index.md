# Welcome to PyUpdater


## What is PyUpdater?

In its simplest form PyUpdater is a collection of modules, when used together, makes its super simple to add auto-update functionality to your app. Support for patch updates are included out of the box :)

A high level break down of the framework consists of 3 parts.

Client
    Is the module you import into your app that provides the update functionality.

Core
    Consists of the KeyHandler, PackageHandler, Uploader & Wrapper.

CLI
    Command line program to help automate the update creation process

When it all comes together you get this


<script type="text/javascript" src="https://asciinema.org/a/15546.js" id="asciicast-15546" async data-theme="solarized-dark"></script>

## Status

[![](https://badge.fury.io/py/PyUpdater.svg)](http://badge.fury.io/py/PyUpdater) [![](https://img.shields.io/circleci/project/JMSwag/PyUpdater.svg)](https://circleci.com/gh/JMSwag/PyUpdater) [![](https://requires.io/github/JMSwag/PyUpdater/requirements.svg?branch=master)](https://requires.io/github/JMSwag/PyUpdater/requirements/?branch=master) [![](https://coveralls.io/repos/JMSwag/PyUpdater/badge.svg)](https://coveralls.io/r/JMSwag/PyUpdater)
