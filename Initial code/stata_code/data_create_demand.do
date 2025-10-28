*** CREATE DATA WITH AGGREGATE MARKET OUTCOMES (Demand and Prices) ***

clear
clear matrix
set type double
set more off
program drop _all
mat drop _all

clear
gen year = 0
save $dirpath/stata_data/data_market.dta, replace

qui forvalues y = 2004(1)2007 {

forvalues m = 1(1)12 {

forvalues d = 1(1)31 {
  
local file =  `y'*10000 + `m'*100 + `d'
local ym = `y'*100 + `m'
capture confirm file `"$datapath/data_sem/ene/ene_`y'/ene_`ym'/ene_`file'.1"'
di `file'

if _rc == 0 {
qui {
// for now only look at market before integrating with Portugal
    * INSHEET BASIC DATA FROM OFFER CURVE
	clear
	insheet using $datapath/data_sem/ene/ene_`y'/ene_`ym'/ene_`file'.1, delimiter(";")
	drop if _n < 3	
	drop if v1 == ""
	forvalues i = 1(1)24 {
		local j = `i' + 2
		replace v`j' = subinstr(v`j',",",".",.)
		gen h`i' = real(v`j')
		replace h`i' = 0 if h`i' == .
	}
	drop v*
	gen p = 1 if _n == 1
	replace p = 0 if p == .
	collapse (sum) h*, by(p)
	 
	reshape long h, i(p) j(hour)
	reshape wide h, i(hour) j(p)
	rename h0 quantity
	rename h1 mg_price
	replace quantity = quantity/2
	
	gen day = 	`d'
	gen month = `m'
	gen year = `y'
	
	// add observation if one hour less, drop if one hour more
	summ hour	
	drop if hour > 24
	if (r(max) ==  23) {
		expand 2 if hour == 23, generate(new)
		replace hour = 24 if new == 1
		drop new
	}
	
	* INSHEET INFORMATION ON BILATERAL CONTRACTS
	gen bilateral = .
	capture confirm file `"$datapath/data_sem/pdbf/pdbf_`y'/pdbf_`ym'/pdbf_`file'.1"'
	if _rc == 0 {
	preserve
		* PDBF DATA *************************** 
		* type of agent with bilateral contracts
		// create bilateral contract data at the firm level (just for four major firms)
		insheet using  "$datapath/data_sem/pdbf/pdbf_`y'/pdbf_`ym'/pdbf_`file'.1", delimit(";") clear
		rename v1 year
		rename v2 month
		rename v3 day
		rename v4 hour
		rename v5 up
		rename v6 mwh
		rename v8 type
		rename v9 code
		drop if month == .		
		drop if type != 4
		gen test = floor(code/100)
		drop if test == 8 & (year == "2006" & month >= 6) | (year == "2007" & month < 3)
		if (year == "2006" & month >= 3 & month <= 5) {
			sort code hour
			gen regulation = 1
			by code hour: replace regulation = 0 if _N <= 2		
			drop if regulation == 1
			drop regulation
		}
		drop v* year month day
		if (_N == 0) {	
			set obs 1		
			replace up =""
			replace hour = 0
			replace mwh = 0
		}		
		* add firm information - take into account mutual ownership
		drop if mwh < 0
		collapse (sum) mwh, by(hour)
		summ hour
		drop if hour > 24
		if (r(max) ==  23) {
			expand 2 if hour == 23, generate(new)
			replace hour = 24 if new == 1
			drop new
		}
		rename mwh bilateral			
		keep hour bilateral
		duplicates drop
		sort hour
		save temp.dta, replace
	restore
	}
	sort hour
	merge hour using temp.dta, nokeep replace update
	drop _merge
	replace bilateral = 0 if bilateral == .
	replace quantity = quantity + bilateral
	drop bilateral
	duplicates drop
		
}

sort year month day hour
append using $dirpath/stata_data/data_market.dta
save  $dirpath/stata_data/data_market.dta, replace

}



}
}
}

duplicates drop
rename mg_price price_ene
replace price_ene = price_ene*10

order year month day hour
sort year month day hour

label var quantity "Total Hourly Electricity Demand (MWh)"
label var price_ene "Marginal Energy Price (E/MWh)"

save  $dirpath/stata_data/data_market.dta, replace
