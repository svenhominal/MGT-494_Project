*** READ RAW DATA FOR PASS-THORUGH REGRESSION DATA ***

clear
clear matrix
set type double
set more off
program drop _all
mat drop _all

gen up = ""
save $dirpath/stata_data/auxiliary/unit_matches.dta, replace

qui forvalues y = 2004(1)2007 {

local endMonth = 12
if (`y'==2007) {
	local endMonth = 6
}

forvalues m = 1(1)`endMonth' {

clear
gen year = 0
save  $dirpath/stata_data/auxiliary/data_bidding_base_`y'_`m'.dta, replace

forvalues d = 1(1)31 {
  
local file =  `y'*10000 + `m'*100 + `d'
local ym = `y'*100 + `m'
capture confirm file `"$datapath/data_sem/curva_pbc_uof/curva_pbc_uof_`y'/curva_pbc_uof_`ym'/curva_pbc_uof_`file'.1"'
di `file'
 
if _rc == 0 {
// for now only look at market before integrating with Portugal
if ((`y' == 2007 & `m' < 7) | `y' < 2007) {
    * INSHEET BASIC DATA FROM OFFER CURVE
	clear
	insheet using $datapath/data_sem/curva_pbc_uof/curva_pbc_uof_`y'/curva_pbc_uof_`ym'/curva_pbc_uof_`file'.1, delimiter(";")
	drop if _n < 3	
	drop if v1 == ""
	
	if ((`y' == 2007 & `m' >= 7) | `y' > 2007) {
		drop v3
		rename v4 v3
		rename v5 v4
		rename v6 v5
		rename v7 v6
		rename v8 v7
		rename v9 v8
	}
	
	gen test = string(v8)
	if test[1] == "." {

	gen hour = real(v1)
	replace v2 = rtrim(v2)
	gen year = real(substr(v2,7,4))
	gen month = real(substr(v2,4,2))
	gen day = real(substr(v2,1,2))
	rename v3 up
	gen type = "S" if v4 == "V"
	replace type = "D" if v4 == "C"	
	replace v5 = subinstr(v5,".","",1)
	replace v5 = subinstr(v5,",",".",1)
	replace v6 = subinstr(v6,",",".",1)
	gen mwh = real(v5)
	gen price = 10*real(v6)
	gen accepted = 1 if v7 == "C" | v7 == "P"
	replace accepted = 0 if v7 == "O"
	sort up hour year month price accepted v7
	drop v* test
	
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
		collapse (sum) mwh, by(up hour)
		summ hour
		drop if hour > 24
		if (r(max) ==  23) {
			expand 2 if hour == 23, generate(new)
			replace hour = 24 if new == 1
			drop new
		}
		rename mwh bilateral			
		keep up hour bilateral
		duplicates drop
		sort up hour
		save temp`y'.dta, replace
	restore
	}
	sort up hour
	merge up hour using temp`y'.dta, nokeep replace update
	drop _merge
	replace bilateral = 0 if bilateral == .
	duplicates drop
		
	* INSHEET FIRM INFORMATION
	sort up year month
	merge up year month using $datapath/data_lists/data_firmlist.dta, nokeep keep(share* firm* firm_code* nfirms tipounidad)
	drop _merge
	gen obs = _n
	replace nfirms = 1 if nfirms == .
	replace share1 = 100 if share1 == .
	replace firm1 = "OTH" if firm1 == ""
	replace firm_code1 = 9 if firm_code1 == .
	*replace firm_code1 = 9 if tipounidad == "GENERICA"
	replace firm1 = "OTH" if firm_code1 == 9
	expand nfirms
	gen firm = "OTH"
	gen share = 100
	gen firm_code = 9	
	sort obs
	forvalues i = 1(1)4 {
		by obs: replace firm_code = firm_code`i' if _n ==`i'
		by obs: replace firm = firm`i' if _n == `i'
		by obs: replace share = share`i' if _n == `i'
	}
	drop firm1 firm2 firm3 firm4 share1 share2 share3 share4 firm_code1 firm_code2 firm_code3 firm_code4
	preserve
		keep up firm firm_code share type nfirms
		duplicates drop
		append using $dirpath/stata_data/unit_matches.dta
		duplicates drop
		save $dirpath/stata_data/unit_matches.dta, replace
	restore

	* CLEAR MARKET
	sort hour 
	by hour: egen mgprice = max(price) if accepted == 1 & type == "S"
	replace mgprice = 0 if mgprice == .
	by hour: egen mg_price = max(mgprice)
	drop mgprice
	
	* ON/OFF & ACCEPTED/REJECTED
	gen on_temp = accepted if hour > 3
	replace on_temp = 0 if on == .
	sort up firm_code
	by up firm_code: egen on = max(on_temp)
	drop on_temp
	* clean repeated observations --take accepted
	sort up firm_code hour price accepted mwh
	by up firm_code hour price: drop if _n != _N
	
	gen rejected_temp = 0
	replace rejected_temp = 1 if price < mg_price & type == "S" & accepted == 0
	replace rejected_temp = 1 if price > mg_price & type == "D" & accepted == 0
	sort up firm_code hour price 
	by up firm_code: egen rejected = max(rejected_temp)
	replace rejected = 0 if accepted == 1
	drop rejected_temp
	
	* CUMULATIVE MWH OFFERED
	gen mwh_temp = 0
	replace mwh_temp = mwh if accepted == 1
	sort up firm_code hour price
	by up firm_code hour: gen cummwh = sum(mwh) if type == "S"
	gsort up firm_code hour -price
	by up firm_code hour: replace cummwh = sum(mwh) if type == "D"
	by up firm_code hour: egen qj = total(mwh_temp)
	replace qj = qj + bilateral 
	replace cummwh = cummwh + bilateral
	
	* convert into shares
	replace mwh = mwh*share/100
	replace mwh_temp = mwh if accepted == 1
	
	* FIRM NET QUANTITY
	sort firm_code hour
	by firm_code hour: egen q_supply_temp = total(mwh_temp) if type == "S"
	replace q_supply_temp = 0 if q_supply_temp == .	
	by firm_code hour: egen q_total_supply = max(q_supply_temp)
	by firm_code hour: egen q_demand_temp = total(mwh_temp) if type == "D"
	replace q_demand_temp = 0 if q_demand_temp == .
	by firm_code hour: egen q_total_demand = max(q_demand_temp)	
	gen q_total = q_total_supply - q_total_demand	
	drop mwh_temp q_supply_temp q_demand_temp 
		
	* AGGREGATE DEMAND AND SUPPLY
	gsort hour price mwh -type
	by hour: gen supply = sum(mwh) if type ==  "S" & rejected == 0
	by hour: replace supply = supply[_n-1] if supply == .
	gsort hour -price mwh type
	by hour: gen demand = sum(mwh) if type == "D" & rejected == 0
	by hour: replace demand = demand[_n-1] if demand == .
	*twoway (scatter price supply) (scatter price demand) if hour == 12

	* FIRM DEMAND AND SUPPLY
	sort firm_code hour price
	gen supply_firm = mwh if type == "S"  & rejected == 0
	replace supply_firm = 0 if supply_firm == .
	by firm_code hour: replace supply_firm = sum(supply_firm)
	gsort firm_code hour -price
	gen demand_firm = mwh if type == "D"  & rejected == 0
	replace demand_firm = 0 if demand_firm == .
	by firm_code hour: replace demand_firm = sum(demand_firm)
	gen net_supply = supply_firm - demand_firm

	* SMOOTH DEMAND AND SUPPLY ESTIMATES
	gen slope_RD = .
	gen slope_S = .
	gen slope_D = .
	mkspline price1 20 price2 30 price3 40 price4 50 price5 60 price6 70 price7 80 price8 90 price9 100 price10 = price
	gen base1 = price1/price
	gen base2 = price2/price
	gen base3 = price3/price
	gen base4 = price4/price
	gen base5 = price5/price
	gen base6 = price6/price
	gen base7 = price7/price
	gen base8 = price8/price
	gen base9 = price9/price
	gen base10 = price10/price
	
	// aggregate demand and supply
	forvalues h = 1(1)24 {
  		reg demand price1-price10 if hour == `h'
  		mat b = e(b)
  		replace slope_D = base1*b[1,1] + base2*b[1,2] + base3*b[1,3] + base4*b[1,4] + base5*b[1,5] + ///
					base6*b[1,6] + base7*b[1,7] + base8*b[1,8] + base9*b[1,9] + base10*b[1,10] if hour == `h'
		reg supply price1-price10 if hour == `h' 
		mat b = e(b)
  		replace slope_S = base1*b[1,1] + base2*b[1,2] + base3*b[1,3] + base4*b[1,4] + base5*b[1,5] + ///
					base6*b[1,6] + base7*b[1,7] + base8*b[1,8] + base9*b[1,9] + base10*b[1,10] if hour == `h'
	}

	// residual demand
	forvalues f = 1(1)4 {
		gen dr = 0
		sort hour price mwh
		gen drs_firm = mwh if type == "S" & firm_code != `f'  & rejected == 0
		replace drs_firm = 0 if drs_firm == . 
		by hour: replace drs_firm = sum(drs_firm)
		gsort hour -price mwh
		gen drd_firm = mwh if type == "D"  & firm_code != `f'  & rejected == 0
		replace drd_firm = 0 if drd_firm == .
		by hour: replace drd_firm = sum(drd_firm)
		replace dr = drd_firm - drs_firm
		drop  drd* drs*
		
	*twoway (scatter price net_supply) (scatter price dr) if hour == 12 & firm_code == `f' & price > `r(mean)'-5 & price < `r(mean)'+5, title("`y' `m' `r(mean)'")

		forvalues h = 1(1)24 {
			reg dr price1-price10 if hour == `h' 
			mat b = e(b)
			replace slope_RD = base1*b[1,1] + base2*b[1,2] + base3*b[1,3] + base4*b[1,4] + base5*b[1,5] + ///
					base6*b[1,6] + base7*b[1,7] + base8*b[1,8] + base9*b[1,9] + base10*b[1,10] if hour == `h' & firm_code == `f'
		}
		drop dr	
	}
	drop base1-base10 price1-price10

	gen slope = -1/slope_RD
	sort up
	merge up using $datapath/data_lists/data_thermalplant.dta, nokeep keep(id)
	drop _merge
	drop if id == .
	
	compress
	append using $dirpath/stata_data/auxiliary/data_bidding_base_`y'_`m'.dta
	save  $dirpath/stata_data/auxiliary/data_bidding_base_`y'_`m'.dta, replace
	}
} 
}
}
compress
duplicates drop
sort up year month day hour
save  $dirpath/stata_data/auxiliary/data_bidding_base_`y'_`m'.dta, replace
}
rm temp`y'.dta
}

