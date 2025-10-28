*** Create bidding data for Matlab to estimate slopes ***

set more off


* ESTIMATION OF STRUCTURAL MARKUPS
forvalues y = 2004(1)2006 {
local endMonth = 12
if (`y'==2006) {
	local endMonth = 2
}
forvalues m = 1(1)`endMonth' {
forvalues d = 1(1)31 {
  
local file =  `y'*10000 + `m'*100 + `d'
local ym = `y'*100 + `m'
capture confirm file `"$datapath/data_sem/curva_pbc_uof/curva_pbc_uof_`y'/curva_pbc_uof_`ym'/curva_pbc_uof_`file'.1"'
di `file'
 
if _rc == 0 {
qui {
   * INSHEET BASIC DATA FROM OFFER CURVE
	clear
	insheet using $datapath/data_sem/curva_pbc_uof/curva_pbc_uof_`y'/curva_pbc_uof_`ym'/curva_pbc_uof_`file'.1, delimiter(";")
	drop if _n < 3	
	drop if v1 == ""

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
	drop v*
	
	// add observation if one hour less, drop if one hour more
	summ hour	
	drop if hour > 24
	if (r(max) ==  23) {
		expand 2 if hour == 23
		sort up hour price accepted
		by up hour price accepted: replace hour = 24 if hour == 23 & _n == 2
	}
		
	// INSHEET FIRM AND PLANT INFORMATION
	sort up year month
	merge up year month using $datapath/data_lists/data_firmlist.dta, nokeep keep(firm1 firm_code1)
	drop _merge
	sort up year month
	merge up using $datapath/data_emissions/data_thermalplant_erate.dta, nokeep keep(erate id fuel)
	drop _merge
	summ id
	replace erate = 0 if erate == .	
	
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
	
	
	* CLEAR MARKET
	sort hour 
	by hour: egen mgprice = max(price) if accepted == 1 & type == "S"
	replace mgprice = 0 if mgprice == .
	by hour: egen mg_price = max(mgprice)
	drop mgprice
	rename mg_price mg_price_original


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
	replace mwh = mwh*share/100
	replace mwh_temp = mwh if accepted == 1	

	* add distortions marginal cost
	replace erate = 0 if type == "D"
	replace erate = 0 if erate == .
	
	* add mg. cost
	
	sort up
	merge up using $dirpath/stata_data/data_costs.dta, nokeep keep(param*) replace update
	drop _merge

	sort year month day up
	merge year month day using $dirpath/stata_data/data_inputs.dta, nokeep 
	drop _merge
	
	sort year month day
	merge year month day using $dirpath/stata_data/data_eua_prices.dta, nokeep keep(eprice)
	drop _merge
	gen cost_CO2 = erate*eprice
	replace cost_CO2 = 0 if cost_CO2 == . & `y' == 2004

	gen mg_cost = price
	replace mg_cost = 10*(param4*coal*param7 + param8) + cost_CO2 if (fuel == "HA" | fuel == "LN" | fuel == "LP" | fuel == "CI") & price > 10 & price < 120
	replace mg_cost = 10*(param4*gas*param7 + param8) + cost_CO2 if fuel == "CCGT" & price > 10 & price < 120
	replace mg_cost = 10*(param4*oil*param7 + param8) + cost_CO2 if fuel == "FU" & price > 10 & price < 120
	drop param*
	
	foreach fueltype in HA LN LP CI CCGT FU {
	 	di  "`fueltype'"
	 	qui summ mg_cost if fuel == "`fueltype'"
	 	replace mg_cost = `r(mean)' if mg_cost == . & fuel == "`fueltype'" 
	}
	
	* clean up before porting to Matlab
	replace id = id + 1000 if id != .
	egen id2 = group(up)
	replace id = id2 if id == .
	egen direction = group(type)
	replace mwh = round(mwh,.1)
	replace price = round(price,.01)
	outsheet year month day hour firm_code id price mwh erate direction accepted rejected mg_cost using "$dirpath/matlab_data/data_`file'.csv", replace comma
	outsheet up id using "$dirpath/matlab_data/data_up_`file'.csv", replace comma
}
count if mg_cost == .
}
}	
}
}

