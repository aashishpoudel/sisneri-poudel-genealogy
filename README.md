# Sisneri Poudel Genealogy Project

## Project Overview

This project builds and hosts a **genealogy website** for the *Sisneri
Poudel* family lineage. The central logic is in **`genealogy.py`**,
which takes structured family data and generates **interactive HTML
family trees** in both **English** and **Nepali**.

## Main Components

### 1. Data Definition

-   Family members are defined in **`genealogy_poudel_data.py`** using a
    custom `Person` class.
-   Each `Person` has attributes like name (English/Nepali), gender,
    birth year, place, comments, and an `addition` flag.
-   This data is exported to **`genealogy_tree.json`**, which provides a
    hierarchical JSON version of the tree.

### 2. Tree Generation (`genealogy.py`)

-   Reads the family data and traverses through each person.
-   Creates both **text-based trees** and **HTML trees** with:
    -   Colored connectors per generation.
    -   Gender-specific icons (e.g., girl icons).
    -   Optional **plus (+) marker** if a person was newly added
        (`addition=True`).
    -   Hoverable **comment asterisks** that display pop-ups with notes.

### 3. HTML Outputs

-   **`sisneri_poudel_tree_en.html`** → English version of the tree.
-   **`sisneri_poudel_tree_np.html`** → Nepali version of the tree.
-   Both display multi-generational trees with expandable data embedded
    in `<span>` attributes (name, father, grandfather, etc.).

### 4. Website Frontend

-   **`index.html`** hosts the trees inside an iframe with language
    tabs, a **search bar** (with autocomplete pills), and a **hamburger
    menu** that opens side navigation.
-   **`about.html`** describes the genealogy source, methodology, and
    FAQ in both Nepali and English.
-   **`contact.html`** provides professional contact options (WhatsApp,
    email) with styled clickable cards.

## Key Features

-   Bilingual support: every page has both Nepali and English content.
-   Family trees are color-coded by generation, with metadata embedded
    for advanced search.
-   Visual icons and symbols (+ for new additions, \* for notes) make
    the tree easy to interpret.
-   Modern UI: responsive design, sticky search, hamburger side menu,
    professional About & Contact pages.

------------------------------------------------------------------------

👉 In short:\
The project is a **custom genealogy publishing system** ---
`genealogy.py` transforms structured family data into **interactive,
bilingual, web-ready family trees** that are deployed as a website
(sisneripoudel.com).

## Architecture Diagram

``` mermaid
flowchart TD
    A[genealogy_poudel_data.py] -->|Defines Person data| B[genealogy.py]
    B -->|Generates JSON| C[genealogy_tree.json]
    B -->|Generates HTML| D[sisneri_poudel_tree_en.html]
    B -->|Generates HTML| E[sisneri_poudel_tree_np.html]
    D --> F[index.html]
    E --> F[index.html]
    F --> G[Website (sisneripoudel.com)]
    H[about.html & contact.html] --> G
```
