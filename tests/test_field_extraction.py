import unittest

from field_extraction import (
    extract_from_tags,
    normalize_process,
    clean_varietal,
    clean_origin,
    clean_flavour,
    extract_from_body_labels,
    extract_structured,
)

MARKET_LANE = ("80% São Benedito Origin: Piatã, Bahia, Brazil Variety: Catuaí "
               "Processing Method: Pulped Natural Producers: Silvio Leite "
               "Relationship Length: Since 2020 20% San Antonio Origin: Inzá, "
               "Cauca, Colombia Varieties: Caturra Processing Method: Washed")

SEVEN_SEEDS = ("Origin: Chirinos, Cajamarca, Peru Producer: Various Process: "
               "Fully Washed Altitude: 1700-1900 masl Varietal: Caturra, Bourbon, Catimor")


class TestTags(unittest.TestCase):
    def test_code_black_underscore(self):
        tags = ["COFFEE_Espresso", "FLAVOUR_Chocolate", "FLAVOUR_Nutty",
                "ORIGIN_Brazil", "ORIGIN_Ethiopia", "PROCESSING_Natural", "PROCESSING_Washed"]
        out = extract_from_tags(tags)
        self.assertEqual(out["origin"], "Brazil, Ethiopia")
        self.assertEqual(out["process"], "Natural, Washed")
        self.assertEqual(out["flavour"], "Chocolate, Nutty")
        self.assertEqual(out["varietal"], "")

    def test_ona_dot(self):
        tags = ["Brew Method.Pour over", "Coffee Type.Filter",
                "Origin.South America", "Taste Notes.Floral", "Taste Notes.Nutty", "Rare Coffee"]
        out = extract_from_tags(tags)
        self.assertEqual(out["origin"], "South America")
        self.assertEqual(out["flavour"], "Floral, Nutty")

    def test_proud_mary_colon_custom_key(self):
        tags = ["Feeling: Mild", "For: Espresso", "From: Nicaragua", "Process: Washed", "Type: Single Origin"]
        out = extract_from_tags(tags)
        self.assertEqual(out["origin"], "Nicaragua")
        self.assertEqual(out["process"], "Washed")

    def test_ignores_bare_tags(self):
        out = extract_from_tags(["coffee", "All Products", "SINGLE ORIGIN"])
        self.assertEqual(out, {"origin": "", "process": "", "varietal": "", "flavour": ""})


class TestProcess(unittest.TestCase):
    def test_strips_trailing_label(self):
        self.assertEqual(normalize_process("Fully Washed ALTITUDE"), "Fully Washed")
        self.assertEqual(normalize_process("Pulped Natural Producers"), "Pulped Natural")

    def test_multi_process(self):
        self.assertEqual(normalize_process("WASHED & NATURAL REGION"), "Washed, Natural")

    def test_keeps_specific_over_generic(self):
        self.assertEqual(normalize_process("Carbonic Maceration"), "Carbonic Maceration")
        self.assertEqual(normalize_process("pulped natural"), "Pulped Natural")

    def test_empty_when_no_known_term(self):
        self.assertEqual(normalize_process("Single Origin Goodness"), "")
        self.assertEqual(normalize_process(""), "")


class TestVarietal(unittest.TestCase):
    def test_salvages_list_before_prose(self):
        self.assertEqual(clean_varietal("Caturra In the hills of Cauca, Colombia"), "Caturra")

    def test_rejects_prose_leading(self):
        self.assertEqual(clean_varietal("his farm has pink bourbon, bourbon aji, caturra"), "")

    def test_keeps_clean_lists(self):
        self.assertEqual(clean_varietal("Caturra & Catuaí"), "Caturra & Catuaí")
        self.assertEqual(clean_varietal("Catuaí"), "Catuaí")
        self.assertEqual(clean_varietal("Caturra, Bourbon, Catimor"), "Caturra, Bourbon, Catimor")

    def test_cuts_cup_label_and_trailing_country(self):
        self.assertEqual(clean_varietal("HEIRLOOM, CASTILLO, CATURRA, COLOMBIA CUP"),
                         "HEIRLOOM, CASTILLO, CATURRA")
        self.assertEqual(clean_varietal("GESHA CUP: HONEY, JASMINE, FRUIT TEA"), "GESHA")
        self.assertEqual(clean_varietal("COLOMBIA CUP: BERRY, TAMARIND"), "")

    def test_empty(self):
        self.assertEqual(clean_varietal(""), "")


class TestOrigin(unittest.TestCase):
    def test_trims_flavour_prose(self):
        self.assertEqual(clean_origin("Limu Kossa, Ethiopia, delivers notes of smooth milk chocolate"),
                         "Limu Kossa, Ethiopia")

    def test_rejects_company_without_place(self):
        self.assertEqual(clean_origin("Unex Exporters based in coffee"), "")

    def test_rejects_leading_article(self):
        self.assertEqual(clean_origin("the highlands of Tarqui where the family built a farm"), "")

    def test_keeps_clean(self):
        self.assertEqual(clean_origin("Carmo de Minas, Minas Gerais, Brazil"),
                         "Carmo de Minas, Minas Gerais, Brazil")
        self.assertEqual(clean_origin("South America"), "South America")
        self.assertEqual(clean_origin("Nicaragua"), "Nicaragua")


class TestFlavour(unittest.TestCase):
    def test_rejects_recipe_text(self):
        self.assertEqual(clean_flavour("FILTER RECIPE + V60 RECIPE This is just a starting place"), "")

    def test_cuts_blend_composition_and_prose(self):
        self.assertEqual(clean_flavour("DARK CHOCOLATE, CHERRY, VANILLA 50% BRAZIL | Samba - Natural"),
                         "DARK CHOCOLATE, CHERRY, VANILLA")
        self.assertEqual(clean_flavour("Milk chocolate, caramel, stone fruit The thoughtful combination"),
                         "Milk chocolate, caramel, stone fruit")

    def test_rejects_marketing_prose(self):
        self.assertEqual(clean_flavour("with enough clarity to hold your attention, and enough familiarity"), "")
        self.assertEqual(clean_flavour("will deliver flavours of chocolate and cherry through both espresso"), "")

    def test_trims_trailing_blurb(self):
        self.assertEqual(clean_flavour("Milk chocolate, red apple + almond praline Our Seasonal Blend is"),
                         "Milk chocolate, red apple + almond praline")

    def test_keeps_clean_notes(self):
        self.assertEqual(clean_flavour("Floral, Nutty"), "Floral, Nutty")
        self.assertEqual(clean_flavour("Citrus, Floral, Stone Fruit"), "Citrus, Floral, Stone Fruit")
        self.assertEqual(clean_flavour("PLUM, DARK CHOCOLATE, PEACH, MACADAMIA, APRICOT, MAPLE SYRUP"),
                         "PLUM, DARK CHOCOLATE, PEACH, MACADAMIA, APRICOT, MAPLE SYRUP")

    def test_empty(self):
        self.assertEqual(clean_flavour(""), "")


class TestBodyLabels(unittest.TestCase):
    def test_market_lane_first_component(self):
        out = extract_from_body_labels(MARKET_LANE)
        self.assertEqual(out["origin"], "Piatã, Bahia, Brazil")
        self.assertEqual(out["varietal"], "Catuaí")
        self.assertEqual(out["process"], "Pulped Natural")

    def test_seven_seeds_no_bleed(self):
        out = extract_from_body_labels(SEVEN_SEEDS)
        self.assertEqual(out["origin"], "Chirinos, Cajamarca, Peru")
        self.assertEqual(out["process"], "Fully Washed")
        self.assertEqual(out["varietal"], "Caturra, Bourbon, Catimor")

    def test_no_labels(self):
        out = extract_from_body_labels("A delicious everyday espresso blend.")
        self.assertEqual(out, {"origin": "", "process": "", "varietal": "", "flavour": ""})


class TestOrchestrator(unittest.TestCase):
    def test_tags_win_over_body(self):
        out = extract_structured(
            tags=["ORIGIN_Brazil", "PROCESSING_Washed"],
            body_text="Origin: Somewhere Else Process: Natural",
        )
        self.assertEqual(out["origin"], "Brazil")
        self.assertEqual(out["process"], "Washed")

    def test_body_fills_when_no_tags(self):
        out = extract_structured(tags=[], body_text=SEVEN_SEEDS)
        self.assertEqual(out["process"], "Fully Washed")
        self.assertEqual(out["varietal"], "Caturra, Bourbon, Catimor")

    def test_process_always_whitelisted(self):
        out = extract_structured(tags=["PROCESS: Fully Washed ALTITUDE"], body_text="")
        self.assertEqual(out["process"], "Fully Washed")

    def test_skip_sources_body(self):
        out = extract_structured(tags=[], body_text=SEVEN_SEEDS, rules={"skip_sources": ["body"]})
        self.assertEqual(out, {"origin": "", "process": "", "varietal": "", "flavour": ""})


if __name__ == "__main__":
    unittest.main()
