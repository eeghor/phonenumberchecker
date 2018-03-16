import pandas as pd
from collections import defaultdict

class PhoneNumberChecker:
    
    AUS_STATE_PREFIXES = {str(n) for n in range(1,9)}

    # ACMA data is available at https://www.thenumberingsystem.com.au/download/InquiryFullDownload.zip

    NUMB_ALLOCS = pd.read_csv('/Users/ik/Data/phone-numbers/InquiryFullDownload.csv', 
                             dtype={'Prefix': int, 'From': int, 'To': int}, 
                   usecols=["Service Type", "Prefix", "From", "To", "Latest Holder"]).loc[lambda _: _['Service Type'].isin({'Digital mobile', 'Local rate', 'Freephone'})]
    """
    create dictionaries of the sort {service_type1: {prefix1: [(from, to, holder), ..], prefix2: [(..), ..]},...
    e.g. {'mob': {40: [(400000000, 400299999, 'TELSTRA CORPORATION LIMITED'),..],..}
    """

    PREF2SERVICE = {'13': 'Local rate', '18': 'Freephone', '4': 'Digital mobile'}
    PREF2ABBR = {'13': 'loc', '18': 'free', '4': 'mob'}

    ALLOCS_DICT = defaultdict(lambda: defaultdict(list))

    for pref in PREF2SERVICE:
        for row in NUMB_ALLOCS[NUMB_ALLOCS['Service Type'] == PREF2SERVICE[pref]].iterrows():
            ALLOCS_DICT[PREF2ABBR[pref]][row[1].Prefix].append((row[1].From, row[1].To, 
                ' '.join(str(row[1]["Latest Holder"]).lower().replace('pty', ' ').replace('ltd', ' ')
                                                    .replace('limited', ' ').split())))

    LNDL_PREFIXES = {a[1:] if a.startswith('0') else a for a in 
                     set(pd.read_csv('/Users/ik/Data/phone-numbers/landline_prefix_by_area.txt', dtype=str)['prefix'])}
    
    def __init__(self):
        pass
    
    @staticmethod
    def verify_prefix(phone_number):
        """
        input: NORMALISED phone_number
        returns: tuple ([NORMALISED PHONE NUMBER], [NUMBER HOLDER])
        """
        pref = phone_number[:2] if phone_number[0] != '4' else phone_number[0]

        for match_pref in set(PhoneNumberChecker.ALLOCS_DICT[PhoneNumberChecker.PREF2ABBR[pref]]):
            if  str(match_pref).startswith(phone_number[:2]):
                for number_range in PhoneNumberChecker.ALLOCS_DICT[PhoneNumberChecker.PREF2ABBR[pref]][match_pref]:
                    if number_range[0] <= int(phone_number) <= number_range[1]:
                        return (phone_number, number_range[2])
        return (phone_number, 'invalid')

    @staticmethod
    def normalise(ph):

        assert isinstance(ph, str), 'phone number must be a string!'
        # remove  and any non-numbers
        ph = ''.join([c for c in ph if c.isdigit()])
        # remove leading 0
        while ph[0] == '0':
            ph = ph[1:]
        # remove leading 61
        if ph[:2] == '61':
            ph = ph[2:]

        return ph


    @staticmethod
    def verify(ph):  # 114 ms
        
        """
        normalized number may be valid only if it's one of the following:
        
            a 9-digit mobile, e.g. 408621608
            a 9-digit land line, e.g. 355983589
            a 8-digit land line, e.g. 55983582
            a 6-digit 'local rate' number, e.g. 131028
            a 7-digit 'free' number, e.g. 1802099
            a 10-digit 'free' number
            a 10-digit 'local rate' number
            
        """
        ph = PhoneNumberChecker.normalise(ph)

        # check if the length of number is 6 to 10
        if any([len(ph) not in range(6,11), 
                len(ph) == 9 and ph[0] not in PhoneNumberChecker.AUS_STATE_PREFIXES]):
            return (ph, 'invalid')

        # check mobile numbers (note: 9-digits)
        if ph[0] == '4' or len(ph) in {6,7,10}:
            return (PhoneNumberChecker.verify_prefix(ph))

        # deal with the 8- and 9-digit landlines
        if len(ph) == 9 and ph[0] != '4':

            for pref in PhoneNumberChecker.LNDL_PREFIXES:
                if ph.startswith(pref):
                    return (ph, 'valid landline number')
            return (ph, 'invalid')

        if len(ph) == 8:

            for l in PhoneNumberChecker.AUS_STATE_PREFIXES - {'4'}:
                for pref in PhoneNumberChecker.LNDL_PREFIXES:
                    if (l + ph).startswith(pref):
                        return (ph, 'valid landline number')
            return (ph, 'invalid')

if __name__ == '__main__':

    print(f'initializing phone checker...', end='')
    pnc = PhoneNumberChecker()
    print('ok')
    print(pnc.verify('0061475001329'))
    print(pnc.verify('  934400221'))
    print(pnc.verify('1 33030'))
    print(pnc.verify('$##04 .. 24103473'))
    print(pnc.verify('+ 614 78 001 873'))
    print(pnc.verify('42217002'))