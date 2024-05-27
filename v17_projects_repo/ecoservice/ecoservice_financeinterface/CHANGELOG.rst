Changelog
=========

16.0.1.0.0
----------
* Migration to 16.0

15.0.1.2.0
----------
* Fix visiblity for counter account

15.0.1.1.2
----------
* Fix make line_id in Journal items editable.

15.0.1.1.0
----------
* Add: delivery date to invoice and export

15.0.1.0.0
----------
* Migration to 15.0

14.0.1.2.0
----------
* Add Field to use in Export

14.0.1.1.0
----------
* Optimize and refactor logic for export account moves

14.0.1.0.6
----------
* Ignore encoding errors

14.0.1.0.5
----------
* Migration to 14.0

13.0.1.0.5
----------
* | Fixed a problem where showing the export list took a long time

13.0.1.0.4
----------
* | Added a missing access rule that prevented non finance interface
  | users from posting invoices

13.0.1.0.3
----------
* | Fixed a bug in pre-migration that will fail in the init-process
  | when upgrading from a previous Odoo version

13.0.1.0.2
----------
* | Fixed a flaw at installation process where existing companies
  | wouldn't get the mandatory validation configuration assigned
* | Solved an error in the odoo logs where the database couldn't
  | set a field to required (not null). This issue also caused
  | Odoo.sh instances to be marked as faulty.
* | Resolved a warning in the odoo logs for multiple fields
  | with the same description

13.0.1.0.1
----------
* | Fixed an issue where Unit Tests couldn't run on systems
  | without SKR03 (13004)

13.0.1.0.0
----------
* | Migration to 13.0
