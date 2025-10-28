*** MERGE DATA WITH OTHER INFORMATION AND CLEAN UP ***

// put data sets together
clear
clear matrix

gen year = 0
forvalues y = 2004(1)2007 {
local endMonth = 12
if (`y'==2007) {
	local endMonth = 6
}
forvalues m = 1(1)`endMonth' {
	capture append using "$dirpath/stata_data/auxiliary/data_bidding_base_`y'_`m'.dta"
}
}

compress

// Re-define firm names (largest is 1)
replace firm_code = 110 if firm_code == 1
replace firm_code = 1 if firm_code == 2
replace firm_code = 2 if firm_code == 110
	
replace firm_code = 110 if firm_code == 4
replace firm_code = 4 if firm_code == 3
replace firm_code = 3 if firm_code == 110

// Drop if thermal plant out of the market or still under testing
sort up year month
merge up year month using $dirpath/stata_data/data_active.dta, keep(active) nokeep
drop if active == 0
drop active _merge

// Thermal plant characteristics & engineering cost estimates
sort up
merge up using $dirpath/stata_data/data_thermalplant_erate.dta, nokeep keep(fuel mw minmw erate vintage) replace update
drop _merge

sort up
merge up using $dirpath/stata_data/data_costs.dta, nokeep keep(param*) replace update
drop _merge

sort year month day up
merge year month day using $dirpath/stata_data/data_inputs.dta, nokeep replace update
drop _merge

gen mg_cost = param4*coal*param7 + param8 if fuel == "HA" | fuel == "LN" | fuel == "LP" | fuel == "CI"
replace mg_cost = param4*gas*param7 + param8 if fuel == "CCGT"
replace mg_cost = param4*oil*param7 + param8 if fuel == "FU"
replace mg_cost = mg_cost * 10
drop if mg_cost == .
drop param*

// CO2 prices -- spot market
sort year month day
merge year month day using $dirpath/stata_data/data_eua_prices.dta, nokeep keep(eprice)
drop _merge
replace eprice = 0 if eprice == .
gen cost_CO2 = erate*eprice
replace cost_CO2 = 0 if cost_CO2 == .

// Weekday data
sort year month day
merge year month day using $dirpath/stata_data/data_weekday.dta, nokeep keep(weekd) replace update
drop _merge

// Generate Season Dummies 
gen summer = 0
gen spring = 0	
gen winter = 0
replace summer = 1 if month == 7 | month == 8 | month == 9
replace spring = 1 if month == 4 | month == 5 | month == 6
replace winter = 1 if month == 1 | month == 2 | month == 3

gen summerw = 0
gen springw = 0	
gen winterw = 0
replace summerw = 1 if summer == 1 & weekd < 6
replace springw = 1 if spring == 1 & weekd < 6
replace winterw = 1 if winter == 1 & weekd < 6

compress

* HOURLY DATA CLEAN-UP *********************************************************
keep up year month day hour price mg_price mwh cummwh accepted rejected bilateral ///
		firm firm_code share on qj net_supply q_total slope fuel mg_cost eprice cost_CO2 mw minmw ///
		vintage erate summer* winter* spring* weekd coal gas oil brent
order up year month day hour price mg_price mwh cummwh accepted rejected bilateral ///
		firm firm_code share on qj net_supply q_total slope fuel mg_cost eprice cost_CO2 mw minmw ///
		vintage erate summer* winter* spring* weekd coal gas oil brent

sort up year month day hour
save  $dirpath/stata_data/data_regressions.dta, replace


* DAILY DATA (on/off) **********************************************************
use $dirpath/stata_data/data_regressions.dta, clear

keep on price mg_price mg_cost cost_CO2 eprice net_supply qj q_total cummwh up year month ///
		day hour weekd firm firm_code erate fuel mw minmw ///
		summer* winter* spring* coal gas oil

gen pq = mg_price*cummwh if mg_price >= price
replace pq = 0 if pq == .
gen q = cummwh if mg_price >= price
replace q = 0 if q == .

collapse (mean) on price mg_price mg_cost cost_CO2 eprice net_supply qj q_total (max) pq q, by(up year month day hour weekd firm firm_code erate fuel mw minmw summer* winter* spring* coal gas oil)
collapse (mean) on price mg_price mg_cost cost_CO2 eprice net_supply qj q_total (sum) pq q, by(up year month day weekd firm firm_code fuel mw minmw  summer* winter* spring* coal gas oil erate)

gen wmg_price = pq/q
drop q pq
replace wmg_price = mg_price if wmg_price == .

order up year month day on price mg_price wmg_price mg_cost cost_CO2 eprice net_supply qj q_total ///
		weekd firm firm_code erate fuel mw minmw ///
		summer* winter* spring* coal gas oil

sort up year month day
save  $dirpath/stata_data/data_regressions_daily.dta, replace

* ADDING LABELS FOR BETTER DOCUMENTATION ***************************************

* hourly
use $dirpath/stata_data/data_regressions.dta, clear
label var price           "Price offered by the unit (E/MWh)"                 
label var mg_price        "Market Clearing Price (E/MWh)"
label var mwh             "Quantity offered by the unit at given price (MWh)"
label var cummwh          "Cumulative quantity offered by unit at given price or less (MWh)"                
label var accepted        "Dummy equals 1 if quantity was accepted in the market"
label var rejected        "Dummy equals 1 if unit not considered for the daily market"
label var bilateral       "Physical Bilateral contracts (MWh)"
label var firm            "Main Firm name"
label var firm_code       "Firm code"                 
label var share           "Ownership share of main firm (usually 100%)"                 
label var on              "Dummy equals 1 if unit is producing positive quantity"
label var qj              "Quantity accepted in the market (MWh)"
label var net_supply      "Net Supply of Main Firm at price offered by unit (MWh)"
label var q_total         "Net Quantity sold by the Firm (MWh)"
label var slope           "Slope of residual demand at given price"
label var mg_cost         "Engineering Marginal Cost estimate for the unit (E/MWh)"
label var cost_CO2        "Emissions cost per MWh produced (E/MWh)"
label var summer          "Summer Dummy"
label var summerw         "Summer Weekday Dummy"
label var winter          "Winter Dummy"              
label var winterw         "Winter Weekday Dummy"
label var spring          "Spring Dummy"         
label var springw         "Spring Weekday Dummy"
sort up year month day hour
save  $dirpath/stata_data/data_regressions.dta, replace

* daily
use  $dirpath/stata_data/data_regressions_daily.dta, clear
label var price           "Price offered by the unit (E/MWh)"                 
label var mg_price        "Market Clearing Price (E/MWh)"
label var wmg_price       "Market Clearing Price Weighted by Unit Output (E/MWh)"
label var firm            "Main Firm name"
label var firm_code       "Firm code"      
label var on              "Dummy equals 1 if unit is producing positive quantity"
label var qj              "Quantity accepted in the market (MWh)"
label var net_supply      "Net Supply of Main Firm at price offered by unit (MWh)"
label var q_total         "Net Quantity sold by the Firm (MWh)"
label var mg_cost         "Engineering Marginal Cost estimate for the unit (E/MWh)"
label var cost_CO2        "Emissions cost per MWh produced (E/MWh)"
label var summer          "Summer Dummy"
label var summerw         "Summer Weekday Dummy"
label var winter          "Winter Dummy"              
label var winterw         "Winter Weekday Dummy"
label var spring          "Spring Dummy"         
label var springw         "Spring Weekday Dummy"
sort up year month day
save  $dirpath/stata_data/data_regressions_daily.dta, replace


// REDUCED FORM DATA SET *******************************************************
use "$dirpath/stata_data/data_regressions.dta", clear	

// generate measures of emissions cost and marginal cost
drop if abs(price-mg_price) > .5
drop if cost_CO2 == .

drop if rejected == 1

sort day hour month year
by day hour month year: egen ecost = mean(cost_CO2) if price == mg_price
by day hour month year: egen ecost2 = mean(cost_CO2)
by day hour month year: egen ecost3 = max(cost_CO2)
by day hour month year: egen ecost4 = min(cost_CO2)

by day hour month year: egen mgcost = mean(mg_cost) if price == mg_price
by day hour month year: egen mgcost2 = mean(mg_cost)
by day hour month year: egen totalcost = mean(mg_cost + cost_CO2) if price == mg_price
by day hour month year: egen totalcost2 = mean(mg_cost + cost_CO2) 	

keep year month day hour mg_price mgcost* totalcost* ecost* eprice erate gas coal brent oil
duplicates drop
	
collapse (mean) totalcost* mgcost* ecost* erate, by(year month day hour mg_price eprice gas coal brent oil)

sort year month day hour
merge year month day hour using "$dirpath/stata_data/data_market.dta", replace update
drop _merge
replace mg_price = price_ene if mg_price == .
drop if month > 6 & year == 2007
	
sort year month day hour
merge year month day using "$dirpath/stata_data/data_market.dta", nokeep replace update
drop _merge
	
egen time = group(year month day hour)
	
// week day data
sort year month day
merge year month day using "$dirpath/stata_data/data_weekday.dta", nokeep keep(weekd) replace update
drop _merge

sort year month day
merge year month day using "$dirpath/stata_data/data_eua_prices.dta", nokeep keep(eprice) replace update
drop _merge	
replace eprice = 0 if year < 2005

// re-generate dummies 
gen summer = 0
gen spring = 0	
gen winter = 0
replace summer = 1 if month == 7 | month == 8 | month == 9
replace spring = 1 if month == 4 | month == 5 | month == 6
replace winter = 1 if month == 1 | month == 2 | month == 3

gen summerw = 0
gen springw = 0	
gen winterw = 0
replace summerw = 1 if summer == 1 & weekd < 6
replace springw = 1 if spring == 1 & weekd < 6
replace winterw = 1 if winter == 1 & weekd < 6
	
gen weekend = 1 if weekd == 6 | weekd == 7
replace weekend = 0 if weekend == .
gen peak = 1 if hour >= 8 & hour < 21
replace peak = 0 if peak == .
		
gen rd = 1 if year == 2006 & month > 2
replace rd = 1 if year == 2007	
replace rd = 0 if rd == .

gen quarter = 1 if month < 4
replace quarter = 2 if month < 7 & month > 3
replace quarter = 3 if month < 10 & month > 6
replace quarter = 4 if month > 9

gen bimonth = ceil(month/2)

// additional data
sort year month day hour
merge year month day hour using "$dirpath/stata_data/data_sregime.dta", nokeep replace update
drop _merge
		
sort year month day 
merge year month day using "$dirpath/stata_data/data_inputs.dta", nokeep replace update
drop _merge

sort year month day
merge year month day using "$dirpath/stata_data/data_weather.dta", nokeep keep(temp tempx windx humid)
drop _merge

sort year month
merge year month using "$dirpath/stata_data/data_demandcontrols.dta", nokeep keep(temperatura activeconmica~s rgimenespecial hidrulica nuclear laboralidad)
drop _merge
	
sort year month
merge year month using "$dirpath/stata_data/data_gdp.dta", nokeep keep(UEM spain france portugal uk unitedstates germany)
drop _merge

gen coal2 = coal*coal
gen gas2 = gas*gas
gen oil2 = oil*oil
gen brent2 = brent*brent

gen lcoal = log(coal + 1)
gen lgas = log(gas + 1)
gen loil = log(oil + 1)
gen lbrent = log(brent + 1)

_pctile temp, nq(5)
gen tempq1 = temp if temp < `r(r1)'
replace tempq1 = 0 if tempq1 == .
gen tempq2 = temp if temp >= `r(r1)' & temp < `r(r2)'
replace tempq2 = 0 if tempq2 == .
gen tempq3 = temp if temp >= `r(r2)' & temp < `r(r3)'
replace tempq3 = 0 if tempq3 == .
gen tempq4 = temp if temp >= `r(r3)' & temp < `r(r4)'
replace tempq4 = 0 if tempq4 == .
gen tempq5 = temp if temp >= `r(r4)'
replace tempq5 = 0 if tempq5 == .

gen temp2 = temp^2
gen windx2 = windx^2
gen windtime = windx*time/10000

// generate marginal tech cost
sort year month day hour
merge year month day hour using "$dirpath/stata_data/data_mgtech.dta", nokeep
drop _merge
rename mgtech mgtech_org

gen erate2 = ecost2/eprice
gen erate3 = ecost3/eprice	
gen erate4 = ecost4/eprice	
replace erate2 = 0 if eprice == 0
replace erate3 = 0 if eprice == 0
replace erate4 = 0 if eprice == 0
		
replace ecost2 = erate2*eprice if eprice != 0
replace ecost2 = 0 if (year == 2004 | eprice == 0)
replace ecost2 = . if eprice == .
replace ecost  = 0 if (year == 2004 | eprice == 0)
replace ecost  = . if eprice == .

// compute ecost2 using marginal technology information
replace ecost2 = ecost if ecost != .
replace ecost2 = 0.88*eprice if mgtech_org == "COAL" & ecost2 == .
replace ecost2 = 0.51*eprice if mgtech_org == "CCGT" & ecost2 == .

replace totalcost2 = totalcost if totalcost != .
replace totalcost2  = . if eprice == .

sort year month day hour
egen ttime = group(year month day hour)
ipolate ecost2 ttime, generate(ecost_int)
ipolate totalcost2 ttime, generate(totalcost_int)
replace ecost_int = . if eprice == .
replace totalcost_int = . if eprice == .
drop ttime

replace ecost_int = 0.88*eprice if mgtech_int == "COAL" & ecost2 == .
replace ecost_int = 0.51*eprice if mgtech_int == "CCGT" & ecost2 == .

gen leprice = log(eprice + 1)
gen lecost2 = log(ecost2 + 1)
gen lecost_int = log(ecost_int + 1)
gen ltotalcost2 = log(totalcost2 + 1)
gen lmg_price = log(mg_price + 1)

egen ym = group(year month)
egen yb = group(year bimonth)
egen yq = group(year quarter)

gen totalcost2_peak = peak*totalcost2
gen totalcost2_off = (1-peak)*totalcost2
gen ltotalcost2_peak = peak*ltotalcost2
gen ltotalcost2_off = (1-peak)*ltotalcost2

gen ecost2_peak = peak*ecost2
gen ecost2_off = (1-peak)*ecost2
gen lecost2_peak = peak*lecost2
gen lecost2_off = (1-peak)*lecost2

keep year month day hour mg_price lmg_price eprice leprice ecost ecost2 ecost_int ecost2_peak ecost2_off lecost2_peak lecost2_off erate ///
	totalcost totalcost2 totalcost2_peak totalcost2_off ltotalcost2_peak ltotalcost2_off ///
	weekd temp tempx temp2 windx windx2 windtime humid ///
	coal gas brent coal2 gas2 brent2 lcoal lbrent lgas ///
	ym yb yq rd peak time 

label var ecost           "Emissions costs from marginal units"                 
label var ecost2          "Emissions costs using additional marginal technology info"
label var ecost_int       "Interpolated emissions cost"
label var peak            "DUMMY=1 for hours 8am to 8pm"
label var totalcost2      "Marginal engineering cost + Emissions cost"  

save "$dirpath/stata_data/data_regressions_passthrough.dta", replace


* STRUCTURAL DATA SET **********************************************************
use "$dirpath/stata_data/data_regressions.dta", clear

sort up firm year month day hour price
by up firm year month day hour: gen step = _n
by up firm year month day hour: gen Nstep = _N

drop if slope <= 0
drop if slope == .
drop if rejected == 1
replace cost_CO2 = . if eprice == .
compress
	
gen markup = q_total*slope
gen pricehat = price - markup
gen weight_p = normalden((price-mg_price)/3)

gen fuel2 = fuel
replace fuel2 = "COAL" if fuel == "HA" | fuel == "CI" | fuel == "LN" | fuel == "LP"

gen weekend = 1 if weekd == 6 | weekd == 7
replace weekend = 0 if weekend == .
gen weekdays = 0
replace weekdays = 1 if weekend == 1
gen peak = 1 if hour >= 8 & hour < 21
replace peak = 0 if peak == .
	
gen season = 1 if winter == 1
replace season = 2 if spring == 1
replace season = 3 if summer == 1
replace season = 4 if season == .
egen quarter = group(year season)
			
gen rd = 1 if year == 2006 & month > 2
replace rd = 1 if year == 2007 & month < 3	
replace rd = 0 if rd == .

// adding instruments
sort year month day
merge year month day using "$dirpath/stata_data/data_weather.dta", nokeep keep(temp tempx windx humid)
drop _merge

sort year month
merge year month using "$dirpath/stata_data/data_demandcontrols.dta", nokeep keep(temperatura activeconmica~s laboralidad)
drop _merge

capture drop time
egen time = group(year month day)
egen id = group(up)
egen firmday = group(time firm_code)
egen firmym = group(year month firm_code)

* clean up bids to include only bids that are marginal (no capacity constraints)
drop if price <= 10
drop if price >= 120
drop if round(price*100) != round(mg_price*100)
drop if rd != 0
drop if step == 1 & bilateral == 0
drop if step == Nstep

keep year month day hour up id price pricehat markup mg_cost cost_CO2 firm_code firmday firmym ///
		summer* spring* winter* weekdays temp windx humid temperatura

label var pricehat        "Price offered corrected for markup when theta = 1"
label var weekdays	      "Dummy=1 for weekdays"  
label var id		      "Numerical identifier for UP"  
label var firmym	      "Numerical identifier for firm-month-of-sample groups"  
label var firmday	      "Numerical identifier for firm-day groups"  

sort up id year month day hour price pricehat markup mg_cost cost_CO2
save "$dirpath/stata_data/data_regressions_structural.dta", replace	
