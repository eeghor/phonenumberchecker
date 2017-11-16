import pandas as pd
from collections import defaultdict

class PhoneNumberChecker:
    
    AUS_STATE_PREFIXES = {str(n) for n in range(1,9)}

    NUMB_ALLOCS = pd.read_csv('/Users/ik/Data/phone-numbers/InquiryFullDownload.csv', 
                             dtype={'Prefix': int, 'From': int, 'To': int}, 
                   usecols=["Service Type", "Prefix", "From", "To", "Latest Holder"]).loc[lambda _: _['Service Type'].isin({'Digital mobile', 'Local rate', 'Freephone'})]
    """
    create dictionaries of the sort {prefix1: [(from, to, holder), ..], prefix2: [(..), ..]}
    e.g. {40: [(400000000, 400299999, 'TELSTRA CORPORATION LIMITED'),..],..}
    """

    MOB_ALLOCS_DICT = defaultdict(list)
    for row in NUMB_ALLOCS[NUMB_ALLOCS['Service Type'] == 'Digital mobile'].iterrows():
        MOB_ALLOCS_DICT[row[1].Prefix].append((row[1].From, row[1].To, row[1]["Latest Holder"]))
    
    LOCAL_ALLOCS_DICT = defaultdict(list)
    for row in NUMB_ALLOCS[NUMB_ALLOCS['Service Type'] == 'Local rate'].iterrows():
        LOCAL_ALLOCS_DICT[row[1].Prefix].append((row[1].From, row[1].To, row[1]["Latest Holder"]))

    FREE_ALLOCS_DICT = defaultdict(list)
    for row in NUMB_ALLOCS[NUMB_ALLOCS['Service Type'] == 'Freephone'].iterrows():
        FREE_ALLOCS_DICT[row[1].Prefix].append((row[1].From, row[1].To, row[1]["Latest Holder"]))

    LNDL_PREFIXES = {a[1:] if a.startswith('0') else a for a in 
                     set(pd.read_csv('/Users/ik/Data/phone-numbers/landline_prefix_by_area.txt', dtype=str)['prefix'])}
    
    TELCO_DICT = {'AUSTRALIAN COMMUNICATIONS AND MEDIA AUTHORITY': 'acma',
                     'COMPATEL LIMITED': 'compatel',
                     'DIALOGUE COMMUNICATIONS PTY LIMITED': 'dialogue',
                     'LYCAMOBILE PTY LTD': 'lycamobile',
                     'MESSAGEBIRD PTY LTD': 'messagebird',
                     'OPTUS MOBILE PTY LIMITED': 'optus',
                     'PIVOTEL SATELLITE PTY LIMITED': 'pivotel',
                     'SOUL PATTINSON TELECOMMUNICATIONS PTY LIMITED': 'soul pattison',
                     'SYDNEY TRAINS': 'sydney trains',
                     'SYMBIO NETWORKS PTY LTD': 'symbio',
                     'TELSTRA CORPORATION LIMITED': 'telstra',
                     'VICTORIAN RAIL TRACK': 'victorian rail track',
                     'VODAFONE AUSTRALIA PTY LIMITED': 'vodafone'}
    
    def __init__(self):
        pass
    
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
        if ph[0] == '4':
            prefix_ranges = PhoneNumberChecker.NUMB_ALLOCS[PhoneNumberChecker.NUMB_ALLOCS.Prefix == int(ph[:2])]
            if prefix_ranges.empty:  # empty dataframe, no such prefixes
                return None
            else:
                for row in prefix_ranges.iterrows():
                    if row[1].From <= int(ph) <= row[1].To:
                        holder = row[1]["Latest Holder"] if len(row[1]["Latest Holder"]) > 4 else 'unknown'
                        return (ph, PhoneNumberChecker.TELCO_DICT[holder.strip()])
        # check local rate numbers (6 digits)
        if ph[:2] == '13':
            for row in PhoneNumberChecker.NUMB_ALLOCS[PhoneNumberChecker.NUMB_ALLOCS['Service Type'] == 'Local rate'].iterrows():
                if ph.startswith(str(row[1].Prefix)):
                    if row[1].From <= int(ph) <= row[1].To:
                        if len(row[1]["Latest Holder"]) > 7:
                            return (ph, 'valid local rate')
            return (ph, 'invalid')
        # check free numbers
        if ph[:2] == '18':
            for row in PhoneNumberChecker.NUMB_ALLOCS[PhoneNumberChecker.NUMB_ALLOCS['Service Type'] == 'Freephone'].iterrows():
                if ph.startswith(str(row[1].Prefix)):
                    if row[1].From <= int(ph) <= row[1].To:
                        if len(row[1]["Latest Holder"]) > 7:
                            return (ph, 'valid free number')
            return (ph, 'invalid')
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