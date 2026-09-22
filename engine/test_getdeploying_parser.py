import unittest
import re
from bs4 import BeautifulSoup

def parse_getdeploying_html(html: str):
    """
    Simulate the multi-strategy price extractor from scraper.py
    """
    soup = BeautifulSoup(html, "html.parser")
    price = None

    # Strategy 1: "Median price (current)" stat card badge
    for dt in soup.find_all("dt"):
        if "median price" in dt.get_text().lower():
            dd = dt.find_next_sibling("dd")
            if dd:
                m = re.search(r'\$(\d+\.?\d*)', dd.get_text())
                if m:
                    price = float(m.group(1))
                    return price, "stat_card"

    # Strategy 2: Schema.org JSON-LD FAQ/Metadata
    for script in soup.find_all("script", type="application/ld+json"):
        content = script.string or ""
        m = re.search(r'median on-demand price is \$(\d+\.?\d*)', content, re.IGNORECASE)
        if m:
            price = float(m.group(1))
            return price, "schema_faq"

    # Strategy 3: Narrative paragraphs/headings
    for p in soup.find_all(["p", "h2", "strong", "div"]):
        txt = p.get_text()
        m = re.search(r'(?:median|average).*?\$(\d+\.?\d*)', txt, re.IGNORECASE)
        if m:
            val = float(m.group(1))
            if 0.1 <= val <= 100.0:
                price = val
                return price, "narrative"

    # Strategy 4: Table td elements
    prices = []
    for td in soup.find_all("td"):
        txt = td.get_text(strip=True)
        m = re.search(r'^\$(\d+\.?\d*)(?:/hr)?$', txt)
        if m:
            val = float(m.group(1))
            if 0.1 <= val <= 100.0:
                prices.append(val)
    if prices:
        prices.sort()
        price = prices[len(prices) // 2]
        return price, "table_median"

    return None, "not_found"


class TestGetDeployingParser(unittest.TestCase):
    def test_stat_card_extraction(self):
        html = """
        <div>
            <dt class="k">Median price (current)</dt>
            <dd class="m-0 flex items-baseline gap-1.5">
                <span class="v">$3.39</span>
                <span class="unit">/GPU/hr</span>
            </dd>
        </div>
        """
        price, method = parse_getdeploying_html(html)
        self.assertEqual(price, 3.39)
        self.assertEqual(method, "stat_card")

    def test_schema_faq_extraction(self):
        html = """
        <script type="application/ld+json">
        {
            "@type": "Question",
            "name": "How much does the H100 cost per hour?",
            "acceptedAnswer": {
                "text": "As of September 22, 2026, the median on-demand price is $4.48 per GPU per hour across 42 providers."
            }
        }
        </script>
        """
        price, method = parse_getdeploying_html(html)
        self.assertEqual(price, 4.48)
        self.assertEqual(method, "schema_faq")

    def test_table_median_extraction(self):
        html = """
        <table>
            <tr><td>$2.00</td></tr>
            <tr><td>$3.50</td></tr>
            <tr><td>$5.00</td></tr>
        </table>
        """
        price, method = parse_getdeploying_html(html)
        self.assertEqual(price, 3.50)
        self.assertEqual(method, "table_median")

    def test_table_median_with_hr_suffix(self):
        html = """
        <table>
            <tr><td>$1.50/hr</td></tr>
            <tr><td>$2.50/hr</td></tr>
            <tr><td>$4.00/hr</td></tr>
        </table>
        """
        price, method = parse_getdeploying_html(html)
        self.assertEqual(price, 2.50)
        self.assertEqual(method, "table_median")

    def test_narrative_extraction(self):
        html = """
        <p>The current median price for this accelerator sits at $6.75 per GPU hour.</p>
        """
        price, method = parse_getdeploying_html(html)
        self.assertEqual(price, 6.75)
        self.assertEqual(method, "narrative")


if __name__ == "__main__":
    unittest.main()
