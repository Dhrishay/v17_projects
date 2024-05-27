# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import json
import re
from decimal import Decimal
from odoo import _, api, models


class Ecofi(models.Model):
    _name = 'ecofi'
    _inherit = ['ecofi', 'ecofi.export.columns']
    #done
    def field_config(  # noqa: C901
        self,
        move,
        line,
        errorcount,
        partnererror,
        thislog,
        thismovename,
        faelligkeit,
        datevdict,
    ):
        print("\n\n\nfield_config------------datev----------------")
        print("move-------------------------------",move)
        print("line-------------------------------",line)
        print("errorcount-------------------------------",errorcount)
        print("partnererror-------------------------------",partnererror)
        print("thislog-------------------------------",thislog)
        print("thismovename-------------------------------",thismovename)
        print("datevdict-------------------------------",datevdict)

        """
        Generate the values for the different Datev columns.

        :param move: account_move
        :param line: account_move_line
        :param errorcount: Errorcount
        :param partnererror: Partnererror
        :param thislog: Log
        :param thismovename: Movename
        :param faelligkeit: Fälligkeit
        """
        export_date = move.date
        print("export_date--------------------",export_date)
        if move.invoice_date:
            print("if------------------")
            export_date = move.invoice_date
        datevdict['Datum'] = export_date.strftime('%d%m')
        datevdict['Steuerperiode'] = move.date.strftime('%d%m%Y')

        # Standard
        datevdict['Beleg1'] = move.name
        print("datevdict['Beleg1']------------------",datevdict['Beleg1'])

        # Kundenzahlung
        if move.journal_id.type == 'bank':
            print("if bank------------------------")
            if not move.payment_id:
                datevdict['Buchungstext'] = move.display_name
                # Suche abgestimmte Zeilen
                bank_line = self.env['account.move.line'].search([
                    ('move_name', '=', move.name),
                    ('account_type', '=', 'asset_receivable'),
                ])
                matched_lines = self.env['account.move.line']
                for bline in bank_line:
                    matched_lines += self.env['account.move.line'].search([
                        ('name', '=', bline.name),
                    ])

                if matched_lines:
                    # filte nach Ausgangsrechnung
                    found_lines = matched_lines.filtered(
                        lambda x: x.move_type == 'out_invoice'
                    )
                    datevdict['Beleg1'] = ' '.join([line.move_name for line in found_lines])
            else:
                if move.payment_id.reconciled_invoice_ids:
                    datevdict['Buchungstext'] = datevdict['Beleg1']
                    datevdict['Beleg1'] = move.payment_id.reconciled_invoice_ids.name
                elif move.ref:
                    datevdict['Buchungstext'] = datevdict['Beleg1']
                    datevdict['Beleg1'] = move.ref

        # Kundenrechnung
        if move.journal_id.type == 'sale':
            print("if sale------------------------------")
            if move.name:
                datevdict['Beleg1'] = move.name
                datevdict['Buchungstext'] = move.name

        if move.journal_id.type == 'purchase' and move.ref:
            datevdict['Beleg1'] = move.ref

        if faelligkeit:
            datevdict['Beleg2'] = faelligkeit

        datevdict['Waehrung'], datevdict['Kurs'] = self.with_context(
            lang='de_DE',
            date=move.date,
        ).format_waehrung(line)
        print("datevdict['Waehrung']-----------------------",datevdict['Waehrung'])
        print("datevdict['Kurs']-----------------------",datevdict['Kurs'])

        if move.ecofi_buchungstext:
            datevdict['Buchungstext'] = move.ecofi_buchungstext
            print("datevdict['Buchungstext']---------------------",datevdict['Buchungstext'])

        if line.name and line.name not in ['/', '<p><br></p>', '<p><br/></p>']:
            print("if ********************************************")
            line_name = (
                line.name
                    .replace('<p>', '')
                    .replace('</p>', '')
                    .replace('<br/>', '')
                    .replace('<br>', '')
            )
            print("line_name-----------------------",line_name)

            if datevdict.get('Buchungstext'):
                datevdict['Buchungstext'] = '{m_bu}, {l_bu}'.format(
                    m_bu=datevdict['Buchungstext'],
                    l_bu=line_name,
                )
                print("datevdict['Buchungstext']-----******---------",datevdict['Buchungstext'])
            else:
                datevdict['Buchungstext'] = line_name

            if move.partner_id:
                datevdict['EulandUSTID'] = ''
                if move.partner_id.country_id:
                    datevdict['EulandUSTID'] = move.partner_id.country_id.code
        if line.account_id.datev_vat_handover:
            print("if datev_vat_handover-------------------------- ")
            if move.partner_id:
                if move.partner_id.vat:
                    datevdict['EulandUSTID'] = move.partner_id.vat
            if 'EulandUSTID' in datevdict and datevdict['EulandUSTID'] == '':
                errorcount += 1
                partnererror.append(move.partner_id.id)
                thislog = '{log} {name} {text} \n'.format(
                    log=thislog,
                    name=thismovename,
                    text=_(
                        'Error! No sales tax identification number stored'
                        ' in the partner!',
                    ),
                )
            if line.ecofi_tax_id:
                datevdict['EUSteuer'] = str(
                    line.ecofi_tax_id.amount
                ).replace('.', ',')
                print("datevdict['EUSteuer']---------------------",datevdict['EUSteuer'])
        if line.partner_id:
            datevdict['ZusatzInhalt1'] = line.partner_id.name
        # set values for Beleginfo to bill information
        if (
            (move.journal_id and move.journal_id.type in ['purchase'])
            and line.move_id
        ):
            datevdict['BelegInfoArt1'] = 'Odoo Bill no'
            datevdict['BelegInfoInhalt1'] = line.move_id.name

        # delivery date
        if (
            self.env.user.company_id.export_delivery_date
            and move.delivery_date
            and datevdict['Steuerperiode']
        ):
            datevdict['Leistungsdatum'] = move.delivery_date.strftime('%d%m%Y')

        # beleglink
        move, line, datevdict = self.set_beleglink(move, line, datevdict)
        print("move----------------------",move)
        print("line-----------------------",line)
        print("datevdict-----------------------",datevdict)
        zzzzzzzzzzzzzzzz
        return errorcount, partnererror, thislog, thismovename, datevdict
    #done
    def set_beleglink(self, move, line, datevdict):
        print("\n\n\nset_beleglink-------------datev------------------------")
        # print("move----------------------------",move)
        # print("line----------------------------",line)
        # print("datevdict----------------------------",datevdict)
        return move, line, datevdict

    def format_umsatz(self, lineumsatz):
        print("\n\n\nformat_umsatz-------------datev----------------")
        """
        Return the formatted amount.

        :param lineumsatz: amountC
        """
        soll_haben = 's' if lineumsatz > 0 else 'h'
        umsatz = str(abs(lineumsatz)).replace('.', ',')
        return umsatz, soll_haben
    #done
    def format_waehrung(self, line):
        print("\n\n\nformat_waehrung-----------datev-----------------")
        """
        Format the currency for the export.

        :param line: account_move_line
        """
        factor = ''
        company = line.company_id or self.env.company
        # print("company-------------------",company)
        currency = line.company_currency_id or company.currency_id
        # print("currency---------------",currency)

        if not self.env.context.get('datev_ignore_currency'):
            # print("if not context get-------------------------")
            # print("line.currency_id.name-----------------",line.currency_id.name)
            # print("currency.name-----------------",currency.name)
            if line.currency_id.name != currency.name:
                currency = line.currency_id
                rate = self.env['res.currency.rate'].sudo().search([
                    ('currency_id', '=', currency.id),
                    ('name', '=', line.date),
                ], limit=1)
                # print("rate----------------------",rate)
                factor = str(
                    rate.rate if rate else currency.rate
                ).replace('.', ',')
                # print("factor----------------------------",factor)

        return currency.name if currency else '', factor

    def generate_csv(self, ecofi_csv, bookingdict, log):
        print("\n\n\ngenerate_csv---------datev-------------------------")
        """
        Implement the generate_csv method for the datev interface.
        """
        ecofi_csv.writerow(bookingdict['datevheader'])
        ecofi_csv.writerow(bookingdict['buchungsheader'])
        for buchungsatz in bookingdict['buchungen']:
            ecofi_csv.writerow(buchungsatz)
        return super().generate_csv(ecofi_csv, bookingdict, log)

    def generate_csv_move_lines(  # noqa: C901
        self,
        move,
        buchungserror,
        errorcount,
        thislog,
        thismovename,
        export_method,
        partnererror,
        buchungszeilencount,
        bookingdict
    ):
        print("\n\n\ngenerate_csv_move_lines------------datev---------------------")
        print("move---------------1111------------",move)
        print("buchungserror----------22222-----------------",buchungserror)
        print("errorcount---------------333333------------",errorcount)
        print("thislog--------------444444-------------",thislog)
        print("export_method------------5555555---------------",export_method)
        print("partnererror--------------------66666-------",partnererror)
        print("buchungszeilencount----------------77777-----------",buchungszeilencount)
        print("bookingdict-------------888888888--------------",bookingdict)
        """
        Implement the generate_csv_move_lines method for the datev interface.
        """
        if 'buchungen' not in bookingdict:
            print("if 111111111111")
            bookingdict['buchungen'] = []
        if 'buchungsheader' not in bookingdict:
            print("if 2---2222-------------------")
            bookingdict['buchungsheader'] = (
                self.env['ecofi.export.columns'].get_datev_column_headings()
            )
        if 'datevheader' not in bookingdict:
            print("if 33333333----------------------")
            bookingdict['datevheader'] = (
                self.get_legal_datev_header(move.vorlauf_id)
            )

        tax_mapping_json = self.env['ir.config_parameter'].sudo().get_param('ecoservice_fi.tax_map', False)
        tax_mapping = json.loads(tax_mapping_json) if tax_mapping_json else {}
        faelligkeit = False
        move_tax_lines = 0
        grouped_line = {}
        cash_basis = self.env.user.company_id.tax_cash_basis_journal_id
        tax_exigibility = self.env.user.company_id.tax_exigibility
        rounding_method = self.env.user.company_id.tax_calculation_rounding_method

        move = self._prepare_move(move, export_method)

        for line in move.line_ids:
            if line.debit == 0 and line.credit == 0:
                continue
            datevkonto = line.account_id.code
            datevgegenkonto = line.ecofi_account_counterpart.code
            if datevgegenkonto == datevkonto:
                if line.date_maturity:
                    faelligkeit = line.date_maturity.strftime('%d%m%y')
                continue
            currency = (
                not self.env.context.get('datev_ignore_currency')
                and bool(line.amount_currency)
            )
            line_total = (
                Decimal(str(line.amount_currency))
                if currency else
                Decimal(str(line.debit)) - Decimal(str(line.credit))
            )
            buschluessel = ''
            if export_method == 'gross':
                if (
                    line.account_id.is_tax_account()
                    and not (tax_exigibility and line.journal_id == cash_basis)
                    and not line.datev_posting_key == 'SD'
                    and len(move.line_ids) != 2
                ):
                    print("if ********************************************")
                    move_tax_lines += 1
                    continue
                if line.datev_posting_key == '40':
                    buschluessel = '40'
                else:
                    linetax = line.get_tax()
                    tax_multiplicator = (
                        Decimal(str(1.0 + (tax_mapping.get(str(linetax.id), linetax.amount) / 100)))
                    )
                    gross_value = Decimal(line_total * tax_multiplicator)
                    line_total = Decimal(str(gross_value))

                    if (
                        not line.account_id.datev_automatic_account
                        and linetax
                    ):
                        buschluessel = str(linetax.l10n_de_datev_code)

            # Ugly as fuck, but a rounding error is uglier
            if rounding_method == 'round_per_line':
                line_total = Decimal(str(
                    round(Decimal(str(
                        line_total
                    )), 2)
                ))

            # Fixes rounding mistakes
            if line.datev_export_value:
                # Ugly as fuck, but a rounding error is uglier
                # Deprecated??
                umsatz = self.format_umsatz(
                    Decimal(str(round(
                        Decimal(str(line.datev_export_value)), 2),
                    ))
                )[0]

            umsatz = str(-line_total) if line_total < 0 else str(line_total)
            sollhaben = 's' if line_total > 0 else 'h'

            datevdict = {
                'Sollhaben': sollhaben,
                'Umsatz': umsatz,
                'Gegenkonto': datevgegenkonto,
                'Konto': datevkonto or '',
                'Buschluessel': buschluessel,
                'Movename': move.name,
                'Auftragsnummer': move.invoice_origin or '',
                'Festschreibung': str(int(bool(
                    move.restrict_mode_hash_table and move.inalterable_hash
                ))),
            }

            (
                errorcount,
                partnererror,
                thislog,
                thismovename,
                datevdict
            ) = self.field_config(
                move,
                line,
                errorcount,
                partnererror,
                thislog,
                thismovename,
                faelligkeit,
                datevdict,
            )

            datevdict = self._get_datev_dict(**datevdict)

            # ! TODO grouping does not work properly.
            # ! grouping adds 2*len(lines) lines with the
            # total of the move (2* = s+h each)
            if self.env.user.company_id.datev_group_lines:
                if self.env.user.company_id.datev_group_sh:
                    self._datev_grouping_combined(
                        grouped_line,
                        line,
                        sollhaben,
                        umsatz,
                        datevdict,
                    )
                else:
                    self._datev_grouping(
                        grouped_line,
                        line,
                        sollhaben,
                        umsatz,
                        datevdict,
                    )
            else:
                grouped_line[line.id] = datevdict

            buchungszeilencount += 1
        bookingdict['move_bookings'] = [
            self._create_export_line(datevdict, rounding_method)
            for datevdict in grouped_line.values()
        ]
        aaaaaaaaaaaaaaaaaaaaaaaaaa
        return (
            buchungserror,
            errorcount,
            thislog,
            partnererror,
            buchungszeilencount,
            bookingdict,
            move_tax_lines
        )
    #done
    def _prepare_move(self, move, export_method):
        print("\n\n\n_prepare_move--------------datev--------------------")
        """
        Return the prepared move.

        :param move: account.move to prepare
        """
        if export_method == 'gross':
            move = self._match_journal_items(move)
        return move
    #done
    def _match_journal_items(self, move):
        print("\n\n\n_match_journal_items-----------datev-------------------")
        print("move-------------------------------",move)
        """
        Match journal items.

        Matches the journal items and set the ref to the corresponding
        invoice number or ref.
        :param move: account.move

        :return account.move with matched lines
        """
        if not move.journal_id or move.journal_id.type not in ['bank']:
            # print("if -----------move.journal_id-------------")
            # print(" -----------move.journal_id-------------",move.journal_id)
            # print(" -----------move.journal_id.type-------------",move.journal_id.type)
            return move

        recon_action = move.open_reconcile_view()
        print("recon_action--------------",recon_action)

        # get all non invoice lines
        other_lines = self.env['account.move.line'].search(
            recon_action['domain']
        ).filtered(
            lambda r: r.journal_id.type not in ['sale', 'purchase']
        )
        print("other_lines----------------------",other_lines)

        # get all invoice lines
        for line in move.invoice_line_ids:
            print("for line-------------------",line)
            ref = (
                line.move_id.name
                if line.ref and line.move_id.name in line.ref
                else line.ref or line.move_id.name
            )
            print("ref-------------------------",ref)
            other_lines.filtered(
                lambda r: r.full_reconcile_id == line.full_reconcile_id
            ).write({
                'ref': ref,
            })
        return move

    def _datev_grouping(self, grouped, line, s_h, turnover, datev_dict):
        print("\n\n\n_datev_grouping------------datev----------------------")
        key = '{account_id}:{tax_id}:{s_h}'.format(
            account_id=line.account_id.id,
            tax_id=line.ecofi_tax_id.id,
            s_h=s_h,
        )

        if key not in grouped:
            grouped[key] = datev_dict
            return

        grp_turnover = Decimal(grouped[key]['Umsatz'].replace(',', '.'))
        new_turnover = Decimal(turnover.replace(',', '.'))
        grp_turnover += new_turnover

        grouped[key]['Umsatz'], _ = self.format_umsatz(
            Decimal(str(grp_turnover)),
        )

        if line.name != '/' and grouped.get(key, {}).get('Buchungstext'):
            grouped[key]['Buchungstext'] = '{bu_text}, {nbu_text}'.format(
                bu_text=grouped[key]['Buchungstext'],
                nbu_text=line.name,
            )

    def _datev_grouping_combined(
        self,
        grouped,
        line,
        s_h,
        turnover,
        datev_dict
    ):
        print("\n\n\n_datev_grouping_combined--------------datev------------")
        key = '{account_id}:{tax_id}'.format(
            account_id=line.account_id.id,
            tax_id=line.ecofi_tax_id.id,
        )

        if key not in grouped:
            grouped[key] = datev_dict
            return

        grp_turnover = Decimal(grouped[key]['Umsatz'].replace(',', '.'))
        new_turnover = Decimal(turnover.replace(',', '.'))

        if grouped[key]['Sollhaben'] != s_h:
            new_turnover = -new_turnover

        grp_turnover += new_turnover

        if grp_turnover < 0.0:
            grouped[key]['Sollhaben'] = (
                's'
                if grouped[key]['Sollhaben'] == 'h' else
                'h'
            )

        grouped[key]['Umsatz'], _ = self.format_umsatz(
            Decimal(str(grp_turnover)),
        )

        if line.name != '/' and grouped.get(key, {}).get('Buchungstext'):
            grouped[key]['Buchungstext'] = '{bu_text}, {nbu_text}'.format(
                bu_text=grouped[key]['Buchungstext'],
                nbu_text=line.name,
            )

    @staticmethod
    def _get_datev_dict(**kwargs) -> dict:
        print("\n\n\n_get_datev_dict--------------datev-----------------")
        return {
            'Sollhaben': kwargs.get('Sollhaben', ''),
            'Umsatz': kwargs.get('Umsatz', ''),
            'Gegenkonto': kwargs.get('Gegenkonto', ''),
            'Datum': kwargs.get('Datum', ''),
            'Konto': kwargs.get('Konto', ''),
            'Beleg1': kwargs.get('Beleg1', ''),
            'Beleg2': kwargs.get('Beleg2', ''),
            'Waehrung': kwargs.get('Waehrung', ''),
            'Buschluessel': kwargs.get('Buschluessel', ''),
            'Kost1': kwargs.get('Kost1', ''),
            'Kost2': kwargs.get('Kost2', ''),
            'Kostmenge': kwargs.get('Kostmenge', ''),
            'Skonto': kwargs.get('Skonto', ''),
            'Buchungstext': kwargs.get('Buchungstext', ''),
            'Beleglink': kwargs.get('Beleglink', ''),
            'BelegInfoArt1': kwargs.get('BelegInfoArt1', ''),
            'BelegInfoInhalt1': kwargs.get('BelegInfoInhalt1', ''),
            'EulandUSTID': kwargs.get('EulandUSTID', ''),
            'EUSteuer': kwargs.get('EUSteuer', ''),
            'Basiswaehrungsbetrag': kwargs.get('Basiswaehrungsbetrag', ''),
            'Basiswaehrungskennung': kwargs.get('Basiswaehrungskennung', ''),
            'Kurs': kwargs.get('Kurs', ''),
            'Movename': kwargs.get('Movename', ''),
            'Auftragsnummer': kwargs.get('Auftragsnummer', ''),
            'ZusatzInhalt1': kwargs.get('ZusatzInhalt1', ''),
            'Festschreibung': kwargs.get('Festschreibung', ''),
            'Steuerperiode': kwargs.get('Steuerperiode', ''),
            'Leistungsdatum': kwargs.get('Leistungsdatum', ''),
        }

    @api.model
    def _create_export_line(self, datev_dict: dict, rounding_method):
        print("\n\n\n_create_export_line------------datev-------------------")
        """
        Create the datev csv move line.
        """
        return self.env['ecofi.export.columns'].get_datev_export_line(
            self._normalize_datev_dict(datev_dict, rounding_method),
        )

    def _normalize_datev_dict(self, datev_dict: dict, rounding_method) -> dict:
        print("\n\n\n_normalize_datev_dict----------datev-------------------------")
        normalized_dict = dict(datev_dict)
        print("normalized_dict---------------------",normalized_dict)

        if normalized_dict.get('Buschluessel') == '0':
            normalized_dict['Buschluessel'] = ''

        normalized_dict['Sollhaben'] = normalized_dict['Sollhaben'].upper()

        if normalized_dict.get('Buchungstext'):
            normalized_dict['Buchungstext'] = '{:.60}'.format(
                normalized_dict['Buchungstext'],
            )

        if normalized_dict.get('Beleg1'):
            normalized_dict['Beleg1'] = '{}'.format(
                re.sub(
                    '[^{}]'.format(Ecofi._get_valid_chars()),
                    '',
                    normalized_dict['Beleg1'],
                ).replace('.', ''),
            )[-36:]

        if normalized_dict.get('Beleg2'):
            normalized_dict['Beleg2'] = '{}'.format(
                re.sub(
                    '[^{}]'.format(Ecofi._get_valid_chars()),
                    '',
                    normalized_dict['Beleg2'],
                ).replace('.', ''),
            )[-36:]

        if normalized_dict.get('Umsatz'):
            if rounding_method == 'round_globally':
                normalized_dict['Umsatz'] = str(
                    round(Decimal(str(
                        normalized_dict['Umsatz'].replace(',', '.')
                    )), 2)
                ).replace('.', ',')
            elif rounding_method == 'round_per_line':
                normalized_dict['Umsatz'] = str(normalized_dict['Umsatz']).replace('.', ',')

        return normalized_dict
    #done
    def ecofi_buchungen(self, journal_ids, date_from, date_to):
        print("\n\n\necofi_buchungen---------------datev-------------------")
        # print("journal_ids------------",journal_ids)
        # print("date_from------------",date_from)
        # print("date_to------------",date_to)
        return super(Ecofi, self.with_context(
            datev_ignore_currency=self.env.company.datev_ignore_currency,
        )).ecofi_buchungen(journal_ids, date_from, date_to)

    @api.model
    def set_up_initial_tax_mapping(self):
        print("\n\n\nset_up_initial_tax_mapping-----------datev-------------------")
        if not self.env['ir.config_parameter'].sudo().get_param('ecoservice_fi.tax_map', False):
            external_ids = [
                # SKR03
                'l10n_de.1_tax_eu_19_purchase_skr03',
                'l10n_de.1_tax_eu_19_purchase_no_vst_skr03',
                'l10n_de.1_tax_eu_7_purchase_no_vst_skr03',
                'l10n_de.1_tax_eu_19_purchase_goods_skr03',
                'l10n_de.1_tax_import_19_and_payable_skr03',
                'l10n_de.1_tax_import_7_and_payable_skr03',
                'l10n_de.1_tax_eu_7_purchase_goods_skr03',
                'l10n_de.1_tax_ust_vst_19_purchase_13b_bau_skr03',
                'l10n_de.1_tax_eu_car_purchase_skr03',
                'l10n_de.1_tax_ust_vst_7_purchase_13b_bau_skr03',
                'l10n_de.1_tax_vst_ust_19_purchase_13b_mobil_skr03',
                'l10n_de.1_tax_eu_7_purchase_skr03',
                'l10n_de.1_tax_vst_ust_19_purchase_13b_werk_ausland_skr03',
                'l10n_de.1_tax_vst_ust_7_purchase_13b_werk_ausland_skr03',
                'l10n_de.1_tax_vst_ust_19_purchase_13a_auslagerung_skr03',
                'l10n_de.1_tax_vst_ust_7_purchase_13a_auslagerung_skr03',
                'l10n_de.1_tax_vst_ust_19_purchase_3eck_last_skr03',
                # SKR04
                'l10n_de.1_tax_eu_19_purchase_skr04',
                'l10n_de.1_tax_eu_19_purchase_no_vst_skr04',
                'l10n_de.1_tax_eu_7_purchase_no_vst_skr04',
                'l10n_de.1_tax_eu_19_purchase_goods_skr04',
                'l10n_de.1_tax_import_19_and_payable_skr04',
                'l10n_de.1_tax_import_7_and_payable_skr04',
                'l10n_de.1_tax_eu_7_purchase_goods_skr04',
                'l10n_de.1_tax_ust_vst_19_purchase_13b_bau_skr04',
                'l10n_de.1_tax_eu_car_purchase_skr04',
                'l10n_de.1_tax_ust_vst_7_purchase_13b_bau_skr04',
                'l10n_de.1_tax_vst_ust_19_purchase_13b_mobil_skr04',
                'l10n_de.1_tax_eu_7_purchase_skr04',
                'l10n_de.1_tax_vst_ust_19_purchase_3eck_last_skr04',
                'l10n_de.1_tax_vst_ust_19_purchase_13b_werk_ausland_skr04',
                'l10n_de.1_tax_vst_ust_7_purchase_13b_werk_ausland_skr04',
                'l10n_de.1_tax_vst_ust_19_purchase_13a_auslagerung_skr04',
                'l10n_de.1_tax_vst_ust_7_purchase_13a_auslagerung_skr04',
            ]
            print("external_ids--------------------------------",)

            taxes_to_map = [self.env.ref(tax_ref, raise_if_not_found=False) for tax_ref in external_ids]

            mapping = {str(key.id): 0.0 for key in taxes_to_map if key}

            self.env['ir.config_parameter'].sudo().set_param('ecoservice_fi.tax_map', json.dumps(mapping))

    @staticmethod
    def _get_valid_chars(additional_chars=None):
        print("\n\n\n_get_valid_chars---------------------datev-------------------")
        """
        Get valid chars for Belegfeld 1 and Belegfeld 2.

        Those can be used e.g. in a RegEx.

        :param str additional_chars:
        :return: a string containing valid chars
        :rtype: str
        """
        chars = r'a-zA-Z0-9$%&*+\-/'

        if additional_chars and isinstance(additional_chars, str):
            chars += additional_chars

        return chars
