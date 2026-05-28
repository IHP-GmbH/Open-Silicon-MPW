# Submission process

The submission process happens on GitHub, and a submission request must be made
before the deadline. All communication with customers is handled via GitHub
issues.

## Request submodule inclusion.

Open a GitHub issue in [Open-Silicon-MPW](https://github.com/IHP-GmbH/Open-Silicon-MPW)
with the title **Request for submission July-2026 repository name**,
requesting the submodule addition. Include a copy-ready `.gitmodules` snippet:
   
> **Note**
> The title must have your repository name in a format: `IHP__<subcategory><4digits>`.


   ```
   ## Submodule request for July-2026 Open-Silicon MPW

   - Repository URL: https://github.com/<org>/<repo>.git
   - Category directory: July-2026/<Category> (Analog, Digital, RF, Mixed-Signal)
   - Submodule path: July-2026/<Category>/IHP__<subcategory-abbrev><4digits>

   ### .gitmodules snippet

   [submodule "July-2026/<Category>/IHP__<subcategory-abbrev><4digits>"]
     path = July-2026/<Category>/IHP__<subcategory-abbrev><4digits>
     url = https://github.com/<org>/<repo>.git
   ```
## Confirmation of the submitted design

After the request your design will be evaluated by the foundry and you will get the confirmation 
via github.

