# Install your animated GitHub profile

## 1. Create the repository
1. Sign in at https://github.com/new.
2. Create a **Public** repository named exactly `nikhilmeshram2006`.
3. Do not initialize another README; this project includes one.

## 2. Upload the project
1. Download and extract the ZIP.
2. In the new repository, choose **Add file → Upload files**.
3. Upload all extracted project contents, including the `.github` folder. Upload the files inside the project folder, not the ZIP itself.
4. Commit the files to the `main` branch.

## 3. Run the workflow
1. Open **Actions** in the repository.
2. Enable workflows if GitHub asks.
3. Select **Update animated profile art**, then click **Run workflow**.
4. Visit https://github.com/nikhilmeshram2006.

If Actions cannot push commits, open **Settings → Actions → General → Workflow permissions** and enable read/write access to repository contents.

## Optional: run locally on Windows
Install Python 3.11+ from https://www.python.org/downloads/windows/. In Command Prompt, from the project folder run:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/prep_photo.py
python scripts/make_ascii_svg.py
python scripts/make_info_card.py
python scripts/fetch_contributions.py
python scripts/render_heatmap_svg.py
```

## Replace the placeholder portrait
Place your image in the project folder, then run:

```bat
python scripts/prep_photo.py my-photo.jpg
python scripts/make_ascii_svg.py
```

Only upload a photo you're comfortable sharing publicly.

## Notes
- The contribution fetcher reads GitHub's public contribution page. If GitHub changes its markup, that step can fail; inspect workflow logs instead of publishing fabricated statistics.
- GitHub may sanitize SVG animations. Static artwork remains a fallback.
- The initial graph is placeholder data until the workflow fetches live public contribution data.
