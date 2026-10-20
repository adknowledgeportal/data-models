#!/usr/bin/env python3
# ------------------------------------------------------------------------------
# Title:        Show the Excel template build's status on the release page
# Stage:        Data dictionary templates (not stage-specific)
# Author:       @grayjulia
# Description:  Used by .github/workflows/build-excel-templates.yml so the
#               person doing a release can see the Excel build without
#               opening the Actions tab
#
# Inputs:       the build's state and results (command-line arguments);
#               GitHub release notes and open Dependabot PRs (gh CLI)
# Outputs:      an "Excel templates" section at the end of the release notes,
#               also written to the workflow run's Summary tab
#
# Usage:        python scripts/excel_templates_release_status.py --tag v1.2.3 --state building --run-url URL
# Dependencies: Python standard library; gh CLI (installed on GitHub runners)
# ------------------------------------------------------------------------------
"""Write the Excel template build's status into the GitHub release notes.

The section sits between two hidden markers at the end of the release notes
and is replaced on each update, so the notes above it are never changed:

  building  - the build has started; reminds the release manager to update
              Core Models (release Step 5) while it runs
  success   - how many templates were uploaded, where, and their labels
  failure   - the build failed; links to the maintenance doc

Open Dependabot PRs are listed too, as a reminder of release Step 1.

This never fails the workflow: if the release can't be read or edited, it
prints a warning and the status is still in the run's Summary tab.
"""

import argparse
import json
import os
import re
import subprocess
import tempfile

START = "<!-- excel-templates-status:start -->"
END = "<!-- excel-templates-status:end -->"
MAINTENANCE_DOC = "docs/excel-templates-maintenance.md"


def status_block(state: str, tag: str, run_url: str, repo_url: str, *, uploaded: str = "",
                 model_version: str = "", release_date: str = "", folder_id: str = "",
                 dependabot_prs: list[dict] | None = None) -> str:
    """The markdown for the release notes' Excel templates section."""
    run = f"[workflow run]({run_url})"
    release_steps = f"[release process]({repo_url}#release-process)"
    doc = f"{repo_url}/blob/main/{MAINTENANCE_DOC}"
    folder = (f"[AD Metadata Dictionary folder](https://www.synapse.org/Synapse:{folder_id})"
              if folder_id else "AD Metadata Dictionary folder")

    if state == "building":
        lines = [
            f"⏳ **Building the Excel templates for {tag}** ({run}). This takes about 5 minutes.",
            "",
            f"**While this runs:** do Step 5 of the {release_steps}: start the Core Models "
            "update, then approve and merge its pull request.",
        ]
    elif state == "success":
        lines = [
            f"✅ **Uploaded {uploaded} Excel templates for {tag}** to the {folder}, labeled "
            f"`modelVersion` {model_version} and `releaseDate` {release_date} ({run}).",
            "",
            f"Next: check a few templates (Step 4), make sure Core Models is merged "
            f"(Step 5), then announce the update (Step 6). See the {release_steps}.",
        ]
    else:
        lines = [
            f"❌ **The Excel template build failed for {tag}** ({run}). The Excel templates "
            "on Synapse were not updated for this release. The rest of the release "
            "(schemas, Core Models) is not affected.",
            "",
            f"See [what to do when the Excel build fails]({doc}).",
        ]

    if dependabot_prs:
        links = ", ".join(f"[#{pr['number']}]({pr['url']})" for pr in dependabot_prs)
        lines += [
            "",
            f"🔧 **Dependabot package update PR open:** {links}. These are handled at "
            f"Step 1 of the {release_steps}; if it wasn't done for this release, do it "
            f"once this release is finished. See the [maintenance doc]({doc}).",
        ]
    return "### Excel templates\n\n" + "\n".join(lines)


def replace_block(body: str, block: str) -> str:
    """The release notes with the Excel templates section added or replaced."""
    section = f"{START}\n{block}\n{END}"
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if pattern.search(body):
        return pattern.sub(lambda _: section, body)
    return f"{body.rstrip()}\n\n{section}\n" if body.strip() else f"{section}\n"


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def open_dependabot_prs(repo: str) -> list[dict]:
    try:
        return json.loads(gh("pr", "list", "--repo", repo, "--author", "app/dependabot",
                             "--state", "open", "--json", "number,url"))
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"::warning::Couldn't list Dependabot PRs: {e}")
        return []


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--tag", required=True, help="release tag, e.g. v1.2.3")
    parser.add_argument("--state", required=True, choices=["building", "success", "failure"])
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--uploaded", default="", help="number of templates uploaded")
    parser.add_argument("--model-version", default="")
    parser.add_argument("--release-date", default="")
    parser.add_argument("--folder-id", default="")
    args = parser.parse_args()

    repo = os.environ["GITHUB_REPOSITORY"]
    repo_url = f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}"
    block = status_block(args.state, args.tag, args.run_url, repo_url,
                         uploaded=args.uploaded, model_version=args.model_version,
                         release_date=args.release_date, folder_id=args.folder_id,
                         dependabot_prs=open_dependabot_prs(repo))

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(block + "\n\n")

    try:
        body = gh("release", "view", args.tag, "--repo", repo, "--json", "body", "--jq", ".body")
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(replace_block(body, block))
        gh("release", "edit", args.tag, "--repo", repo, "--notes-file", f.name)
        print(f"Release {args.tag} notes updated: Excel templates {args.state}")
    except subprocess.CalledProcessError as e:
        print(f"::warning::Couldn't update the notes of release {args.tag} "
              f"({(e.stderr or '').strip() or e}); the status is in this run's Summary tab.")


if __name__ == "__main__":
    main()
