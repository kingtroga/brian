# Scraper Collection for Brain: README

## Overview

This repository contains three web scrapers designed to extract specific data from various sources. These scrapers are tailored for different websites and are intended to be used for data collection and analysis.

### Scraper 1: Wikimedia Scraper
This scraper extracts images and their metadata from Wikimedia.

### Scraper 2: DVISDSHUB Scraper
This scraper collects full-size images along with their titles, descriptions, dates, and locations from the DVISDSHUB website.

### Scraper 3: MET Museum Website Scraper
This scraper gathers data from the Metropolitan Museum of Art's website.

## Scraper Details

### Scraper 1: Wikimedia Scraper
- **Functionality**: Extracts images and metadata from Wikimedia.
- **Data Collected**:
  - Full-size images
  - Titles
  - Descriptions
  - Metadata available on the image page

### Scraper 2: DVISDSHUB Scraper
- **Functionality**: Scrapes images and associated metadata from DVISDSHUB.
- **Data Collected**:
  - Full-size images
  - Title (extracted from above the image on the image page)
  - Description (extracted from below the image on the image page)
  - Date (appended after "ca.")
  - Location (prepended to the description/headline fields)
- **Note**: The scraper excludes wording like "[Image 1 of 7]".
- **Format**: Outputs data in an Excel file with the title and description in the same cell, formatted as: `Location: Title - Description ca. Date`

### Scraper 3: MET Museum Website Scraper
- **Functionality**: Extracts data from the Metropolitan Museum of Art's website.
- **Data Collected**:
  - Full-size images
  - Titles
  - Descriptions
  - Metadata available on the artwork page
