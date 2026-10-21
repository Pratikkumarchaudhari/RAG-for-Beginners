const GOVERNANCE_DOCUMENTS = [
  {
    "source": "access_management.md",
    "title": "Access management procedure",
    "text": "# Access management procedure\nFictional learning material. Not an employer policy.\n\nA user requests dataset access by submitting their name, business purpose, requested role, and requested duration. The Data Owner approves or rejects the request. The administrator implements the approved role assignment. The Data Steward verifies that the access record is complete. Requesters may not approve their own access.\n\nGrant access through roles using the principle of least privilege. Review access quarterly. Remove access when the business need ends or the user leaves the team. Record the approver, approval date, assigned role, and removal date in the access register.\n\n"
  },
  {
    "source": "data_issues.md",
    "title": "Data issue management procedure",
    "text": "# Data issue management procedure\nFictional learning material. Not an employer policy.\n\nA data issue record includes an issue ID, affected dataset, description, business impact, priority, Data Owner, assigned Data Steward, target date, current status, and supporting evidence. The Data Steward investigates and tracks remediation. The Data Owner approves the business rule and confirms resolution.\n\nCritical issues that block a scheduled report are escalated to the Data Owner on the same business day. Other unresolved issues are discussed in the monthly governance meeting. Close an issue only after repeating the failed validation and documenting the corrected result. Retain the original evidence for traceability.\n\n"
  },
  {
    "source": "data_quality.md",
    "title": "Data quality validation procedure",
    "text": "# Data quality validation procedure\nFictional learning material. Not an employer policy.\n\nCompleteness measures whether required values are present. Uniqueness checks whether a business identifier appears more than once. Validity checks whether values follow approved formats and ranges. Consistency compares related values across sources. Timeliness checks whether records arrive by the agreed reporting cutoff.\n\nFor address records, verify required street, city, state, and postal code values, validate permitted state codes, and check postal code format. A format check does not prove that a physical address exists. Document suspected issues and send them to the Data Owner for confirmation before correction. Run validation before publishing a reporting dataset.\n\n"
  }
];
