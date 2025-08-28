
import sys
from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import List, Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
    QHeaderView, QLabel, QSpacerItem, QSizePolicy
)

import pandas as pd

getcontext().prec = 28
D = lambda x: Decimal(str(x))
Q2 = Decimal("0.01")

def money(x: Decimal) -> Decimal:
    return x.quantize(Q2, rounding=ROUND_HALF_UP)

def compute_pricing(quantity, purchase_price, shipping_costs, packaging_costs,
                    margin_pct, amazon_pct, ebay_pct, extra_pct, vat_pct):

    quantity      = int(float(str(quantity) or 0))
    purchase      = D(str(purchase_price or 0))
    shipping      = D(str(shipping_costs or 0))
    packaging     = D(str(packaging_costs or 0))
    margin_pct    = D(str(margin_pct or 0)) / 100
    amazon_pct    = D(str(amazon_pct or 0)) / 100
    ebay_pct      = D(str(ebay_pct or 0)) / 100
    extra_pct     = D(str(extra_pct or 0)) / 100
    vat_pct       = D(str(vat_pct or 0)) / 100

    base_cost = purchase + shipping + packaging
    profit_unit = purchase * margin_pct
    total_costs_unit = base_cost + profit_unit

    total_pct = amazon_pct + ebay_pct + extra_pct + vat_pct
    denominator = (Decimal(1) - total_pct) if (Decimal(1) - total_pct) != 0 else Decimal(1)
    selling_price_unit = total_costs_unit / denominator

    total_tax_unit   = selling_price_unit * vat_pct
    amazon_fee_unit  = selling_price_unit * amazon_pct
    ebay_fee_unit    = selling_price_unit * ebay_pct
    extra_fee_unit   = selling_price_unit * extra_pct

    out_unit = {
        "Quantity": quantity,
        "Purchase Price (€)": money(purchase),
        "Shipping Costs (€)": money(shipping),
        "Packaging Costs (€)": money(packaging),
        "Margin (%)": money(margin_pct * 100),
        "Amazon Fees (%)": money(amazon_pct * 100),
        "eBay Fees (%)": money(ebay_pct * 100),
        "Additional Costs / Advertising Costs (%)": money(extra_pct * 100),
        "VAT (%)": money(vat_pct * 100),
        "Profit (€)": money(profit_unit),
        "Total Tax (€)": money(total_tax_unit),
        "Total Costs (€)": money(total_costs_unit),
        "Total Amazon Fees (€)": money(amazon_fee_unit),
        "Total eBay Fees (€)": money(ebay_fee_unit),
        "Total Additional Costs / Advertising Costs (€)": money(extra_fee_unit),
        "Selling Price (€)": money(selling_price_unit),
    }
    return out_unit


DE_COLS = [
    "Menge",
    "Kaufpreis",
    "Versandkosten",
    "Verpackungskosten",
    "Marge (%)",
    "Amazon-Gebühren (%)",
    "eBay-Gebühren (%)",
    "Zusätzliche Kosten / Werbekosten (%)",
    "MwSt (%)",
    "Profit (€)",
    "Gesamtsteuer (€)",
    "Gesamtkosten (€)",
    "Gesamte Amazon-Gebühren (€)",
    "Gesamte eBay-Gebühren (€)",
    "Gesamte Zusatzkosten / Werbekosten (€)",
    "Verkaufspreis (€)",
]

EN_COLS = [
    "Quantity",
    "Purchase Price (€)",
    "Shipping Costs (€)",
    "Packaging Costs (€)",
    "Margin (%)",
    "Amazon Fees (%)",
    "eBay Fees (%)",
    "Additional Costs / Advertising Costs (%)",
    "VAT (%)",
    "Profit (€)",
    "Total Tax (€)",
    "Total Costs (€)",
    "Total Amazon Fees (€)",
    "Total eBay Fees (€)",
    "Total Additional Costs / Advertising Costs (€)",
    "Selling Price (€)",
]

# Wrapped (multi-line) headers for UI readability
DE_COLS_WRAPPED = [
    "Menge",
    "Kaufpreis",
    "Versand-\nkosten",
    "Verpackungs-\nkosten",
    "Marge (%)",
    "Amazon-\nGebühren (%)",
    "eBay-\nGebühren (%)",
    "Zusätzliche Kosten\n/\nWerbekosten (%)",
    "MwSt (%)",
    "Profit (€)",
    "Gesamt-\nsteuer (€)",
    "Gesamt-\nkosten (€)",
    "Gesamte Amazon-\nGebühren (€)",
    "Gesamte eBay-\nGebühren (€)",
    "Gesamte Zusatzkosten\n/\nWerbekosten (€)",
    "Verkaufs-\npreis (€)",
]

EN_COLS_WRAPPED = [
    "Quantity",
    "Purchase\nPrice (€)",
    "Shipping\nCosts (€)",
    "Packaging\nCosts (€)",
    "Margin (%)",
    "Amazon\nFees (%)",
    "eBay\nFees (%)",
    "Additional Costs\n/\nAdvertising Costs (%)",
    "VAT (%)",
    "Profit (€)",
    "Total\nTax (€)",
    "Total\nCosts (€)",
    "Total Amazon\nFees (€)",
    "Total eBay\nFees (€)",
    "Total Additional Costs\n/\nAdvertising Costs (€)",
    "Selling\nPrice (€)",
]


COL_MAP_EN_TO_DE = dict(zip(EN_COLS, DE_COLS))

INPUT_COLS_IDX = list(range(0, 9))   # first 9 columns are inputs


class PricingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GR24")
        self.language = "de"  # default DE
        self.buttons: Dict[str, QPushButton] = {}
        self._building_ui = False

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 6, 10, 10)
        main_layout.setSpacing(8)

        # Top bar (logo placeholder + buttons)
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        logo = QLabel("GR24")
        logo.setStyleSheet("font-weight: 800; font-size: 28px; color: #1E3A8A;")
        top_bar.addWidget(logo)

        top_bar.addSpacing(16)

        # Buttons
        for key in ["start", "copy", "expand", "delete", "save", "delete_all", "download"]:
            btn = QPushButton()
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(34)
            btn.setStyleSheet(self._button_style())
            self.buttons[key] = btn
            top_bar.addWidget(btn)

        # Spacer
        top_bar.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Language toggle button (EN/DE)
        lang_btn = QPushButton()
        lang_btn.setCursor(Qt.PointingHandCursor)
        lang_btn.setMinimumHeight(34)
        lang_btn.setFixedWidth(60)
        lang_btn.setStyleSheet(self._button_style())
        self.buttons["lang"] = lang_btn
        top_bar.addWidget(lang_btn)

        main_layout.addLayout(top_bar)

        # Table
        self.table = QTableWidget(0, len(EN_COLS))
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setMinimumHeight(48)   # give space for two-line headers
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(True)  # for body cells
        self.table.setStyleSheet("""
            QTableWidget::item { padding: 6px; }
            QHeaderView::section {
                background: #F0F4FF; padding: 8px; border: 1px solid #CBD5E1;
                font-weight: 700;            /* bold headers */
            }
        """)
        main_layout.addWidget(self.table)

        # Wire button actions
        self.buttons["start"].clicked.connect(self.action_start)
        self.buttons["copy"].clicked.connect(self.action_copy)
        self.buttons["expand"].clicked.connect(self.action_expand)
        self.buttons["delete"].clicked.connect(self.action_delete)
        self.buttons["save"].clicked.connect(self.action_save)
        self.buttons["delete_all"].clicked.connect(self.action_delete_all)
        self.buttons["download"].clicked.connect(self.action_download_excel)
        self.buttons["lang"].clicked.connect(self.toggle_language)

        # React to cell edits
        self.table.itemChanged.connect(self._on_cell_changed)

        # Apply language & initialize a single blank row
        self.apply_language()
        self.action_start()

        # Make window large-ish
        self.resize(1200, 700)

    # ---- Styling ----
    def _button_style(self) -> str:
        return """
        QPushButton {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                              stop:0 #1f3aed, stop:1 #0a1cb8);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 6px 14px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                              stop:0 #3044f0, stop:1 #1423c2);
        }
        QPushButton:pressed {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                              stop:0 #1228c9, stop:1 #0a1aa3);
        }
        """

    # ---- Language helpers ----
    def _headers_for_ui(self) -> List[str]:
        if self.language == "de":
            return DE_COLS_WRAPPED
        else:
            return EN_COLS_WRAPPED

    def apply_language(self):
        self._building_ui = True
        if self.language == "de":
            btns = {
                "start": "Start", "copy": "Kopieren", "expand": "Expandieren",
                "delete": "Löschen", "save": "Speichern", "delete_all": "Alles löschen",
                "download": "Download (Excel)", "lang": "EN"
            }
        else:
            btns = {
                "start": "Start", "copy": "Copy", "expand": "Expand",
                "delete": "Delete", "save": "Save", "delete_all": "Delete All",
                "download": "Download (Excel)", "lang": "DE"
            }

        for key, btn in self.buttons.items():
            btn.setText(btns.get(key, key))

        # Table headers (wrapped for UI)
        self.table.setHorizontalHeaderLabels(self._headers_for_ui())
        self._building_ui = False

    def toggle_language(self):
        self.language = "en" if self.language == "de" else "de"
        self.apply_language()

    # ---- Data helpers ----
    def _new_row_defaults(self) -> List[str]:
        return ["0", "0.00", "0.00", "0.00", "0.00", "0.00", "0.00", "0.00", "0.00",
                "", "", "", "", "", "", ""]

    def _add_row(self, values: List[str] = None):
        values = values or self._new_row_defaults()
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.table.blockSignals(True)
        for c, val in enumerate(values):
            item = QTableWidgetItem(str(val))
            flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
            if c in INPUT_COLS_IDX:
                flags |= Qt.ItemIsEditable
            item.setFlags(flags)
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.table.setItem(r, c, item)
        self.table.blockSignals(False)
        self._recompute_row(r)

    def _on_cell_changed(self, item: QTableWidgetItem):
        if self._building_ui:
            return
        if item.column() in INPUT_COLS_IDX:
            self._recompute_row(item.row())

    def _get_row_inputs(self, row: int) -> Dict[str, str]:
        def txt(c):
            it = self.table.item(row, c)
            return (it.text() if it else "0").replace(",", ".").strip()
        return {
            "quantity": txt(0),
            "purchase_price": txt(1),
            "shipping_costs": txt(2),
            "packaging_costs": txt(3),
            "margin_pct": txt(4),
            "amazon_pct": txt(5),
            "ebay_pct": txt(6),
            "extra_pct": txt(7),
            "vat_pct": txt(8),
        }

    def _recompute_row(self, row: int):
        inputs = self._get_row_inputs(row)
        try:
            out = compute_pricing(**inputs)
        except Exception:
            return

        outputs = [
            f"{out['Profit (€)']}",
            f"{out['Total Tax (€)']}",
            f"{out['Total Costs (€)']}",
            f"{out['Total Amazon Fees (€)']}",
            f"{out['Total eBay Fees (€)']}",
            f"{out['Total Additional Costs / Advertising Costs (€)']}",
            f"{out['Selling Price (€)']}",
        ]

        self.table.blockSignals(True)
        for i, val in enumerate(outputs, start=9):
            item = self.table.item(row, i)
            if item is None:
                item = QTableWidgetItem()
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                self.table.setItem(row, i, item)
            item.setText(str(val))
        self.table.blockSignals(False)

    def _gather_dataframe(self) -> pd.DataFrame:
        # Always build with EN keys (since compute_pricing returns EN labels),
        # then rename to DE if language is DE at export time.
        rows: List[Dict[str, str]] = []
        for r in range(self.table.rowCount()):
            inputs = self._get_row_inputs(r)
            out = compute_pricing(**inputs)
            rows.append(out)
        df = pd.DataFrame(rows, columns=EN_COLS)
        if self.language == "de":
            df = df.rename(columns=COL_MAP_EN_TO_DE)
        return df

    # ---- Button actions ----
    def action_start(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        self.table.blockSignals(False)
        self._add_row()

    def action_copy(self):
        r = self.table.currentRow()
        if r < 0:
            r = self.table.rowCount() - 1
            if r < 0:
                self._add_row()
                return
        vals = [self.table.item(r, c).text() if self.table.item(r, c) else "" for c in range(self.table.columnCount())]
        self._add_row(vals[:9] + ["", "", "", "", "", "", ""])

    def action_expand(self):
        self._add_row()

    def action_delete(self):
        r = self.table.currentRow()
        if r >= 0:
            self.table.removeRow(r)

    def action_delete_all(self):
        self.table.setRowCount(0)

    def action_save(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save data", "pricing_data.json", "JSON (*.json)")
        if not path:
            return
        data = []
        for r in range(self.table.rowCount()):
            row_vals = [self.table.item(r, c).text() if self.table.item(r, c) else "" for c in range(self.table.columnCount())]
            data.append(row_vals)
        try:
            import json
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"language": self.language, "rows": data}, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Saved", "Data saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")

    def action_download_excel(self):

        suggested = "pricing_DE.xlsx" if self.language == "de" else "pricing_EN.xlsx"
        path, _ = QFileDialog.getSaveFileName(self, "Export to Excel", suggested, "Excel Workbook (*.xlsx)")
        if not path:
            return
        try:
            df = self._gather_dataframe()
            df.to_excel(path, index=False)
            QMessageBox.information(self, "Exported", "Excel file created successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export Excel:\n{e}")


def main():
    app = QApplication(sys.argv)
    win = PricingApp()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
