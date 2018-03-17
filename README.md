# phonenumberchecker
Perform basic validity checks on a string that is presumably an Australian phone number. Specifically,  this package tell you whether the number exists and if it does, what telco it was allocated to.

## Australian phone numbers
Apart from the mobile numbers that start from 04, the following numbers are often in use in Australia:

### 1800 Numbers
These **toll free** numbers allow customers to reach a business without being charged for the call. Typically, 1800 numbers are free to call from landlines, but not from mobile phones.

### 1300 Numbers
These are so-called **local call** numbers that allow customers to call businesses at the cost of a local call. However, a mobile call is billed at a rate that is determined by their mobile service provider.

### 13 numbers
These are the same as the 1300 numbers.

## Number Allocation Data
We use the data by ACMA available [here](https://thenumberingsystem.com.au/download/InquiryFullDownload.zip) (a ~6 Mb zip file).
## Geographic Numbers Data
Currently, we simply use a [Wikipedia page](https://en.wikipedia.org/wiki/Telephone_numbers_in_Australia) about telephone numbers in Australia.

## Installation 
```
pip3 install phonenumberchecker
```
## Quickstart
```
pnc = PhoneNumberChecker()
pnc.verify('61401547982')
```
You get a tuple with a normalised version of the number and telco name (or ‘invalid’ if the number doesn’t exist): 
```
('401547982', 'optus mobile')
```