
from pyparsing import *
import re

# Pulled from: http://pyparsing.wikispaces.com/file/view/streetAddressParser.py

__author__ = 'spacecowboy'

"""
Wrapped the parser in a class and increased address parsing performance
"""

class AddressParser(object):
    #static instance variable
    instance = None

    def __init__(self):
        # singleton check
        if AddressParser.instance is None:

            # define number as a set of words
            units = oneOf("Zero One Two Three Four Five Six Seven Eight Nine Ten"
                        "Eleven Twelve Thirteen Fourteen Fifteen Sixteen Seventeen Eighteen Nineteen",
                        caseless=True)
            tens = oneOf("Ten Twenty Thirty Forty Fourty Fifty Sixty Seventy Eighty Ninety",caseless=True)
            hundred = CaselessLiteral("Hundred")
            thousand = CaselessLiteral("Thousand")
            OPT_DASH = Optional("-")
            numberword = ((( units + OPT_DASH + Optional(thousand) + OPT_DASH +
                             Optional(units + OPT_DASH + hundred) + OPT_DASH +
                             Optional(tens)) ^ tens )
                          + OPT_DASH + Optional(units) )

            # number can be any of the forms 123, 21B, 222-A or 23 1/2
            housenumber = originalTextFor( numberword | Combine(Word(nums) +
                                Optional(OPT_DASH + oneOf(list(alphas))+FollowedBy(White())) +
                                Optional(OPT_DASH + Word(nums) + FollowedBy(White()))) +
                                Optional(OPT_DASH + "1/2"))

            numberSuffix = oneOf("st th nd rd").setName("numberSuffix")
            streetnumber = originalTextFor( Word(nums) +
                            Optional(OPT_DASH + "1/2") +
                            Optional(numberSuffix) )

            # just a basic word of alpha characters, Maple, Main, etc.
            name = ~numberSuffix + Word(alphas)

            street_types = "Street St Boulevard Blvd Lane Ln Terrace Ter Road Rd Avenue Ave" "Circle Cir Cove Cv Drive Dr Parkway Pkwy Court Ct Square Sq" "Loop Lp".split()

            # types of streets - extend as desired

            type_ = Combine(MatchFirst(map(lambda street_type: Keyword(street_type, caseless = True), street_types)) + Optional(".").suppress())

            # street name
            nsew = Combine(oneOf("N S E W North South East West NW NE SW SE") + Optional("."))
            streetName = (Combine( Optional(nsew) + streetnumber +
                                   Optional("1/2") +
                                   Optional(numberSuffix), joinString=" ", adjacent=False )
                          ^ Combine(~numberSuffix + OneOrMore(~type_ + Combine(Word(alphas) + Optional("."))), joinString=" ", adjacent=False)
                          ^ Combine("Avenue" + Word(alphas) + Optional(OneOrMore(Word(alphas))), joinString=" ", adjacent=False)).setName("streetName")

            # PO Box handling
            acronym = lambda s : Regex(r"\.?\s*".join(s)+r"\.?")
            poBoxRef = ((acronym("PO") | acronym("APO") | acronym("AFP")) +
                        Optional(CaselessLiteral("BOX"))) + Word(alphanums)("boxnumber")

            # basic street address
            streetReference = streetName.setResultsName("name") + Optional(type_).setResultsName("type")
            direct = housenumber.setResultsName("number") + streetReference
            intersection = ( streetReference.setResultsName("crossStreet") +
                             ( '@' | Keyword("and",caseless=True)) +
                             streetReference.setResultsName("street") )
            streetAddress = ( poBoxRef("street")
                              ^ direct.setResultsName("street")
                              ^ streetReference.setResultsName("street")
                              ^ intersection )

            self.tests = """\
                3120 De la Cruz Boulevard
                100 South Street
                123 Main
                221B Baker Street
                10 Downing St
                1600 Pennsylvania Ave
                33 1/2 W 42nd St.
                454 N 38 1/2
                21A Deer Run Drive
                256K Memory Lane
                12-1/2 Lincoln
                23N W Loop South
                23 N W Loop South
                25 Main St
                2500 14th St
                12 Bennet Pkwy
                Pearl St
                Bennet Rd and Main St
                19th St
                1500 Deer Creek Lane
                186 Avenue A
                2081 N Webb Rd
                2081 N. Webb Rd
                1515 West 22nd Street
                2029 Stierlin Court
                P.O. Box 33170
                The Landmark @ One Market, Suite 200
                One Market, Suite 200
                One Market
                One Union Square
                One Union Square, Apt 22-C
                4234 Palisades Mall, Apt 22-C
                6200 Grand River Blvd., Suites 130 & 131
                6200 Grand River Blvd., Suites 130,131
                6200 Grand River Blvd., Suites 130, 131
                55 Mall Of America, Suite #130
                123 Avenue of the Americas
                123-34 Grand River Boulevard
                11601 CENTURY OAKS Terrace STE 121
                """.split("\n")

            self.new_tests = """Space 135 - Truck Court
                             """.split("\n")


            # how to add Apt, Suite, etc.
            # TODO: don't just allow two suite_numbers, let the parser clump them together and then use splits around delimiters to get multiple
            suiteRef = (
                oneOf("Suite Suites Ste Apt Apartment Room Rm", caseless=True) +
                Optional(". ") +
                Word('#'+alphanums+'-')("suite_number_1") + Optional("&") + Optional(",") +

                Optional(Word('#'+alphanums+'-')("suite_number_2")))

            self.streetAddress = Combine(streetAddress + Optional(Suppress(',')) + Optional(suiteRef("suite")), joinString=" ", adjacent=False)

            # instantiate singleton
            AddressParser.instance = self

    def _run_test_suite(self):

        for t in map(str.strip, self.instance.new_tests):
            if t:
                #~ print "1234567890"*3
                t = t.replace('#', '')
                print t

                addr = self.instance.streetAddress.parseString(t, parseAll=True)
                #~ # use this version for testing
                #~ addr = streetAddress.parseString(t)
                print "Number:", addr.street.number
                print "Street:", addr.street.name
                print "Type:", addr.street.type
                if addr.street.boxnumber:
                    print "Box:", addr.street.boxnumber
                print addr.dump()
                print


    def get_parsed_address(self, unparsed_address):
        try:
            address = self.instance.streetAddress.parseString(unparsed_address, parseAll = True)
            if not address.number:
                address.number = None


            address = self.__clean_up_suites(address)
        except:

            address = self.backup_parser(unparsed_address)

            # print unparsed_address, '||', address.number, '|', address.name, address.type, '|', address.suite_numbers

        return address

    def backup_parser(self, unparsed_address):

        #primitive_parser = re.match('([\S-]+)\s([A-Za-z\d\W\s-]+).*', unparsed_address)
        unparsed_address = unparsed_address.replace('#', '')
        primitive_parser = re.match('(\d[\S-]+)\s(.*)$', unparsed_address)
        try:
            street_number = primitive_parser.group(1).strip()
            street_with_suite_list = [primitive_parser.group(2).strip()]
            street_with_suite = street_with_suite_list[0]
        except:
            street_number = None
            street_with_suite_list = [unparsed_address]
            street_with_suite = street_with_suite_list[0]
        suite_numbers = ''
        suite_numbers_list = []

        #TODO: clean up

        for suite in 'Space Suite Suites Ste Apt Apartment Room Rm'.split():
            if suite in street_with_suite.split():

                street_with_suite_list = street_with_suite.split(suite)
                suite_numbers = street_with_suite_list[-1].strip()
                street_with_suite = street_with_suite_list[0].strip()
                if ',' in suite_numbers or '&' in suite_numbers:
                    for delim in ', &'.split():
                        if delim in suite_numbers:
                            suite_numbers_list = suite_numbers.split(delim)
                else:
                    suite_numbers_list = [suite_numbers]

        # to handle cases like [street number] + [street name] + [suite number] without a qualifier (suite, apartment, etc) except #
        if '#' in street_with_suite:
            street_with_suite_list = street_with_suite.split('#')
            suite_numbers = street_with_suite_list[-1].strip()
            suite_with_street = street_with_suite_list[0].strip()
            if ',' in suite_numbers or '&' in suite_numbers:
                for delim in ', &'.split():
                    if delim in suite_numbers:
                        suite_numbers_list = suite_numbers.split(delim)
            else:
                suite_numbers_list = [suite_numbers]

        # feed a dummy address, then re-assign
        # ER - this is a hack to make sure we keep the same exact format that the regular parser uses.
        # ER cont - as of now, we don't use the internal street values (the ones that will print 123 Easy St).
        address = self.instance.streetAddress.parseString("123 Easy St", parseAll = True)
        address.name = street_with_suite_list[0].strip().strip(',')
        address.type = ''
        address.number = street_number

        if suite_numbers_list:
            suite_numbers_list = [suite_number.strip().strip(',').strip('#') for suite_number in suite_numbers_list]
            address.suite_numbers = suite_numbers_list

        if not address.name:
            address.name = unparsed_address
            address.number = None
            address.type = ''
            return address
        else:
            return address

    def __clean_up_suites(self, address):

        if address.suite_number_1:
            address.suite_number_1 = address.suite_number_1.strip('#')
        if address.suite_number_2:
            address.suite_number_2 = address.suite_number_2.strip('#')
        if address.street_number:
            address.number = address.number.strip('#')

        if not address.suite_numbers:

            suite_numbers_list = []

            if address.suite_number_1:
                suite_numbers_list.append(address.suite_number_1)
            if address.suite_number_2:
                suite_numbers_list.append(address.suite_number_2)

            address.suite_numbers = suite_numbers_list

        return address




# TODO: address parser needs to handle 'Suites', shorthand translation
def main():
    testing_parser = AddressParser()
    print testing_parser.get_parsed_address('Space 135 - Truck Court')
    results = AddressParser().get_parsed_address("werawfa njkdshaes jhoasdgfjh - Truck Court")
    print results;



if __name__ == '__main__':
    main()