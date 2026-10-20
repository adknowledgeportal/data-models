"""Tests for scripts/excel_templates_release_status.py, which shows the Excel
template build's status on the GitHub release page."""
import excel_templates_release_status as status

REPO_URL = "https://github.com/example-org/data-models"
RUN_URL = f"{REPO_URL}/actions/runs/1"


def test_building_status_reminds_about_core_models():
    block = status.status_block("building", "v1.2.3", RUN_URL, REPO_URL)
    assert "Building the Excel templates for v1.2.3" in block
    assert "Core Models" in block and "Step 4" in block
    assert RUN_URL in block


def test_success_status_says_what_was_uploaded_and_where():
    block = status.status_block("success", "v1.2.3", RUN_URL, REPO_URL, uploaded="37",
                                model_version="1.2.3", release_date="2026-01-02",
                                folder_id="syn00000000")
    assert "Uploaded 37 Excel templates for v1.2.3" in block
    assert "https://www.synapse.org/Synapse:syn00000000" in block
    assert "`modelVersion` 1.2.3" in block and "`releaseDate` 2026-01-02" in block


def test_failure_status_links_to_the_maintenance_doc():
    block = status.status_block("failure", "v1.2.3", RUN_URL, REPO_URL)
    assert "failed" in block and "not affected" in block
    assert f"{REPO_URL}/blob/main/{status.MAINTENANCE_DOC}" in block


def test_open_dependabot_prs_are_listed():
    prs = [{"number": 7, "url": f"{REPO_URL}/pull/7"}]
    block = status.status_block("success", "v1.2.3", RUN_URL, REPO_URL, dependabot_prs=prs)
    assert f"[#7]({REPO_URL}/pull/7)" in block and f"{REPO_URL}#monthly-maintenance" in block
    assert "Dependabot" not in status.status_block("success", "v1.2.3", RUN_URL, REPO_URL)


def test_status_is_added_after_the_release_notes():
    notes = "## What's changed\n- Added an attribute\n"
    updated = status.replace_block(notes, "BUILDING")
    assert updated.startswith(notes.rstrip())
    assert updated.rstrip().endswith(f"{status.START}\nBUILDING\n{status.END}")


def test_status_is_replaced_not_repeated():
    notes = status.replace_block("Release notes", "BUILDING")
    notes = status.replace_block(notes + "\nA later edit by hand\n", "DONE")
    assert notes.count(status.START) == 1
    assert "BUILDING" not in notes and "DONE" in notes
    assert notes.startswith("Release notes") and "A later edit by hand" in notes


def test_status_on_empty_release_notes():
    assert status.replace_block("", "DONE") == f"{status.START}\nDONE\n{status.END}\n"
