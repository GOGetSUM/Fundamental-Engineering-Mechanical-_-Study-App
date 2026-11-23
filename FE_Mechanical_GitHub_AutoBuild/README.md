# FE Mechanical Study — automatic Windows builds

Offline Tkinter study app with glasses icon, previous/next navigation, shuffle, and solution reveal.

## For maintainers: no manual build
1. Create a **private GitHub repository** (the bundled exam scans are copyrighted; do not publish or redistribute them without authorization).
2. Upload all files and folders from this package, including `.github/workflows/windows-release.yml` and `assets/`.
3. Open **Actions → Windows desktop build → Run workflow**. Wait for completion.
4. Download the **FE-Mechanical-Study-Windows** artifact from the workflow run. Extract the ZIP; it contains the portable Windows application.
5. **Only if you have redistribution rights**, publish a versioned GitHub Release: create/push a tag such as `v1.0.0`. The workflow automatically attaches the Windows ZIP to the release.

## For users
Download the Windows ZIP, extract it, and run `FE-Mechanical-Study.exe`. No Python or batch file needed. See `INSTALL_WINDOWS.txt`.

## Security
The workflow builds on a GitHub-hosted Windows runner. It uses no PowerShell execution-policy bypass or auto-run batch file. PyInstaller executables may still trigger reputation warnings. Do not disable antivirus; consider code signing and dependency pinning for production distribution. Review Actions logs and SHA256 hashes.

## Copyright
The problem and solution images originate from a commercial FE exam preparation book. A private repository is not a substitute for a license to distribute them. For a public GitHub release, obtain rights or replace these images with your own/licensed material. Publishing the source code alone is a separate option.

## New interface
The app includes Home, Study, Features, and About & Support pages. Zoom controls remain on the solution view.

## Customize branding before release
Edit `branding.py` to add your verified Buy Me a Coffee URL and complete source citation. The Home page currently uses the existing `glasses.png` as a **placeholder**, not an asserted official business logo. Replace that image with your own logo if desired (and update `glasses.ico` separately for the Windows icon).

**Important for public GitHub distribution:** The bundled `assets/problems` and `assets/solutions` contain commercial-book-derived images according to the original project documentation. Do **not** publish this complete ZIP or build a public release containing those images unless you have redistribution permission. The app code can be released separately; replace study assets with original or properly licensed material before distributing a complete public application. The Buy Me a Coffee link is voluntary and never required to access features.
