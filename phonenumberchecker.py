import pandas as pd
from collections import defaultdict
import sys

class PhoneNumberChecker:
    
    AUS_STATE_PREFIXES = {str(n) for n in range(1,9)}

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
                ' '.join(str(row[1]["Latest Holder"]).lower().replace('pty', ' ')
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
    def verify(ph):  # 114 ms
        """
        returns a normalised version of possilby a phone number ph or None 
        if ph turns out to be clearly not a phone number
        """
        assert isinstance(ph, str), 'phone number must be a string!'
        
        # remove all leading or trainline white spaces
        ph = ph.strip()
        # remove leading 0 and +
        while ph[0] in {'0', '+'}:
            ph = ph[1:]
        # remove  and any non-numbers
        ph = ''.join([c for c in ph if c.isdigit()])
        """
        the remaining number may be valid only if it's one of the following:
        
            a 9-digit mobile, e.g. 408621608
            a 9-digit landline, e.g. 355983589
            a 8-digit landline, e.g. 55983582
            an 11-digit mobile with Australian country code, e.g. 61408621608
            an 11-digit landline with Australian coutry code, e.g. 61355983589
            a 6-digit 'local rate' number, e.g. 131028
            a 7-digit 'free' number, e.g. 1802099
            a 10-digit 'free' number
            a 10-digit 'local rate' number
            
        """
        # check if the length of number is now 8,9 or 11; if not, then it's a faulty number
        if len(ph) not in {6,7, 8,9,10,11}:
            return (ph, 'invalid')
        # make all 11-digit numbers 9-digit by cutting off the 61 prefix 
        # (if it's not 61, it's not a valid number)
        if len(ph) == 11:
            if ph[:2] == '61':
                ph = ph[2:]
            else:
                return (ph, 'invalid') 
        # at this stage, only the 6-, 8- and 9-digit numbers left
        # deal with the 9-digit numbers: these must start from one of the AUS_STATE_PREFIXES
        if len(ph) == 9 and ph[0] not in PhoneNumberChecker.AUS_STATE_PREFIXES:
            return None
        # check mobile numbers (note: 9-digits)
        return(PhoneNumberChecker.verify_prefix(ph))
        sys.exit(0)

        # if ph[0] == '4':
        #     prefix_ranges = PhoneNumberChecker.NUMB_ALLOCS[PhoneNumberChecker.NUMB_ALLOCS.Prefix == int(ph[:2])]
        #     if prefix_ranges.empty:  # empty dataframe, no such prefixes
        #         return None
        #     else:
        #         for row in prefix_ranges.iterrows():
        #             if row[1].From <= int(ph) <= row[1].To:
        #                 holder = row[1]["Latest Holder"] if len(row[1]["Latest Holder"]) > 4 else 'unknown'
        #                 return (ph, PhoneNumberChecker.TELCO_DICT[holder.strip()])
        # # check local rate numbers (6 digits)
        # if ph[:2] == '13':
        #     for row in PhoneNumberChecker.NUMB_ALLOCS[PhoneNumberChecker.NUMB_ALLOCS['Service Type'] == 'Local rate'].iterrows():
        #         if ph.startswith(str(row[1].Prefix)):
        #             if row[1].From <= int(ph) <= row[1].To:
        #                 if len(row[1]["Latest Holder"]) > 7:
        #                     return (ph, 'valid local rate')
        #     return (ph, 'invalid')
        # # check free numbers
        # if ph[:2] == '18':
        #     for row in PhoneNumberChecker.NUMB_ALLOCS[PhoneNumberChecker.NUMB_ALLOCS['Service Type'] == 'Freephone'].iterrows():
        #         if ph.startswith(str(row[1].Prefix)):
        #             if row[1].From <= int(ph) <= row[1].To:
        #                 if len(row[1]["Latest Holder"]) > 7:
        #                     return (ph, 'valid free number')
        #     return (ph, 'invalid')
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

    pnc = PhoneNumberChecker()
    print(pnc.verify('0061475001329'))