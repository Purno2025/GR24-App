from decimal import Decimal, ROUND_HALF_UP, getcontext
import pandas as pd

getcontext().prec = 28
D = lambda x: Decimal(str(x))
Q2 = Decimal("0.01")

def money(x: Decimal) -> Decimal:
    return x.quantize(Q2, rounding=ROUND_HALF_UP)

def compute_pricing(quantity, purchase_price, shipping_costs, packaging_costs,
                    margin_pct, amazon_pct, ebay_pct, extra_pct, vat_pct):

    # Convert to Decimal
    quantity      = int(quantity)
    purchase      = D(purchase_price)
    shipping      = D(shipping_costs)
    packaging     = D(packaging_costs)
    margin_pct    = D(margin_pct) / 100
    amazon_pct    = D(amazon_pct) / 100
    ebay_pct      = D(ebay_pct) / 100
    extra_pct     = D(extra_pct) / 100
    vat_pct       = D(vat_pct) / 100

    # Base cost
    base_cost = purchase + shipping + packaging

    # Profit = margin% of purchase price
    profit_unit = purchase * margin_pct

    # Total cost before percentages
    total_costs_unit = base_cost + profit_unit

    # Selling price calculation
    total_pct = amazon_pct + ebay_pct + extra_pct + vat_pct
    selling_price_unit = total_costs_unit / (1 - total_pct)

    # Breakdowns
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


if __name__ == "__main__":
    # Take input from user
    quantity = input("Enter Quantity: ")
    purchase_price = input("Enter Purchase Price (€): ")
    shipping_costs = input("Enter Shipping Costs (€): ")
    packaging_costs = input("Enter Packaging Costs (€): ")
    margin_pct = input("Enter Margin (%): ")
    amazon_pct = input("Enter Amazon Fees (%): ")
    ebay_pct = input("Enter eBay Fees (%): ")
    extra_pct = input("Enter Additional Costs / Advertising Costs (%): ")
    vat_pct = input("Enter VAT (%): ")

    row = compute_pricing(quantity, purchase_price, shipping_costs, packaging_costs,
                          margin_pct, amazon_pct, ebay_pct, extra_pct, vat_pct)

    # Show as table
    df = pd.DataFrame([row])
    print("\n=== Calculation Result ===")
    print(df.to_string(index=False))
