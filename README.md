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
