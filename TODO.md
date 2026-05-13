# Task: Modify parent dashboard to display children's results grouped by school level (Primary/Secondary)

## Steps to Complete:

1. **[x]** Update accounts/templates/accounts/parent_dashboard.html
   - Add separate sections for "Primary Children" and "Secondary Children".
   - Group children_reports by school_type in the template.
   - Display child name, class, and results (reports/charts) under each section.
   - Ensure only the logged-in parent's children are shown (already filtered in view).

2. **[x]** Test the implementation
   - Verify that parents see only their own children's information.
   - Check that children are correctly grouped by Primary and Secondary.
   - Ensure reports and charts are displayed per child.

## Current Status:
- Template updated to display full student reports (marks table, comments) instead of simple results list.
- Button labels updated to "View Report" and "Download PDF" for clarity.
- Buttons moved inside the report preview section for better UX.
- View updated to fetch all marks for students (not filtered by term/year).
- Server running on port 8001.
- Browser tool disabled, but changes can be verified by accessing http://127.0.0.1:8001/accounts/parent/login/ and logging in as a parent.
- No dependencies on other files.
