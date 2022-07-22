homepage
========

Code to generate page with links to commonly used sites

# Requirements
- Python (3.6 or greater)
- node

# Installation

## 1. Create virtualenv

`python3 -m venv homepage-venv`

## 2. Clone Repo

`git clone https://github.com/jocassid/homepage.git`

## 3. Activate the virtualenv

In Linux / Unix /Mac OS

`source homepage-venv/bin/activate`

Windows (Powershell)

`& homepage-venv\Scripts\activate.ps1`

## 4. Install Python dependencies

```bash
cd homepage
pip install -r requirements.txt
```

## 5. Install JavaScript (Node) dependencies

Run this command within the `homepage` directory

`npm install`

# Using the homepage script

If you just installed the application your virtual environment 
is active, and you can run the `homepage.py` script.  Otherwise, follow the 
steps under [Installation > Activate the virtualenv](#3-activate-the-virtualenv) .

Using example.yaml as a template, create your own `.yaml` file with the links
and other page elements you wish to include.  If you want your yaml file to 
reside within the `homepage` directory created a `homepage/private` directory
and store your `.yaml` file there.

The syntax for running the script under Linux/MacOS/Unix is:

`./homepage.py PATH_TO_YAML_FILE OUTPUT_DIRECTORY`

An example using the Linux/MacOS/Unix of this command would be:

`./homepage.py private/personal_homepage.yaml dist/`

On Windows systems you typically need to use the following command

`python3 .\homepage.py PATH_TO_YAML_FILE OUTPUT_DIRECTORY`

# homepage YAML Syntax

## Basic Structure

The basic structure of the YAML document is shown below.  The intent is for
the YAML file to define one or more[1] HTML files.  Currently, a page contains 
number of cards.  Each card can have a number of items in its contents.

1. I'm not sure of the "or more" part works yet

```yaml
%YAML 1.2
---
pages:
  - file: index.html
    template: index.html
    contents:
      - type: card
        title: Network
        contents:
          - type: link
            label: Python
            href: https://python.org
```

## Cards

A card is a block (`<div>`) containing title and a number of items.  The 
`type: card` and `title` values are required.  The href value is optional.
If the href value is present the title will be a link

```yaml
- type: card
  title: JavaScript
  href: https://developer.mozilla.org/en-US/docs/Web/JavaScript
  contents:
  - type: link
    label: Jquery
    href: https://jquery.com/
```

## Links

A link is one of the items that go in the contents of a Card.  `type`, 
`label`, and `href` are all required.

```yaml
- type: link
  label: Jquery
  href: https://jquery.com/
```

## Link Groups

Link groups allow a few links to be displayed together on the same line.  
In the example below the first `label`, `href` pair is the left-most link on 
the line.  Within the link group's `links` attribute are pairs of `label`, 
`href` pairs defining the rest of the links on the line.

```yaml
- type: link group
  label: nodejs
  href: https://nodejs.org/
  links:
  - label: learn nodejs
    href: https://nodejs.dev/learn
```

## Menus

Menu's display a Number of links in some sort of drop-down (i.e. a `<select>` 
element).  The label is the text shown when the drop-down is collapsed.  The
`label`, `href` pairs define the links shown in the drop-down.

```yaml
- type: menu
  label: Libraries ...
  links:
  - label: Bokeh
    href: https://bokeh.pydata.org
  - label: cyclonedx-python
    href: https://github.com/CycloneDX/cyclonedx-python
  - label: cyclonedx-python-lib
    href: https://github.com/CycloneDX/cyclonedx-python-lib
```

## Searches

Searches are displayed as a text field and a button to run the search.  The
syntax is similar to links, but the URL in the `href` attribute contains the 
string "SEARCH_STRING".  When the button is clicked, SEARCH_STRING is replaced
by the value in the text field, and the resulting URL is opened.

```yaml
- type: search
  label: Wiktionary
  href: https://en.wiktionary.org/w/index.php?search=SEARCH_STRING
```

