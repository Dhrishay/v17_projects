# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

def try_exec(cr, query):
    try:
        cr.execute(query)
        cr.commit()
    except:  # noqa: E722
        cr.rollback()


def migrate(cr, version):
    if not version:
        return

    try_exec(cr, 'ALTER TABLE account_account RENAME COLUMN ustuebergabe TO datev_vat_handover;')
    try_exec(cr, 'ALTER TABLE account_account RENAME COLUMN automatic TO datev_automatic_account;')
    try_exec(cr, 'ALTER TABLE account_account RENAME COLUMN datev_steuer TO datev_tax_ids;')
    try_exec(cr, 'ALTER TABLE account_account RENAME COLUMN datev_steuer_erforderlich TO datev_tax_required;')
    try_exec(cr, 'ALTER TABLE account_invoice RENAME COLUMN enable_datev_checks TO datev_checks_enabled;')
    try_exec(cr, 'ALTER TABLE account_move_line RENAME COLUMN ecofi_bu TO datev_posting_key;')
    try_exec(cr, 'ALTER TABLE account_tax RENAME COLUMN datev_skonto TO datev_cashback_account_id;')
    try_exec(cr, 'ALTER TABLE res_company RENAME COLUMN enable_datev_checks TO datev_checks_enabled;')

    # Create a new column for the renamed field
    try_exec(cr, """
        ALTER TABLE res_company
        ADD COLUMN IF NOT EXISTS datev_export_method VARCHAR;
    """)

    # Insert renamed data in the renamed field
    try_exec(cr, """
        UPDATE res_company
        SET datev_export_method =
            CASE WHEN exportmethod = 'brutto' THEN 'gross'
                 WHEN exportmethod = 'netto'  THEN 'net'
                 ELSE 'gross'
            END;
    """)
