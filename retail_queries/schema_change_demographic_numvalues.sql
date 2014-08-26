--this script was used to determine roughly how much decimal precision & scale 
--is necessary for the demographic_numvalues table
--previous data type was decimal(18,10)
--we had some data values that had more than 8 digits to the left of the decimal
--those were overflowing...

select CONVERT(varchar(max), value) as valuestr into #d from demographic_numvalues;
    
select top 10 * from #d;

--how many non-zero numbers do we have after the decimal place already?
select max(
	len(
	replace(
			substring(valuestr, PATINDEX('%.%', valuestr) + 1, 20) --gets everything after the "."
		, '0','') --replace 0 with nothing
		)
	) from #d;
--8

--test convert on the temp table; works
select CONVERT(decimal(18,9), valuestr) as valuedec into #dec from #d;
--(7398025 row(s) affected)

--do we have any nulls?
select * from demographic_numvalues where value is null;
--none

alter table #d alter column valuestr decimal(19,9) not null;

--alter the real table 
--we did this on retaildb_test_server on 2012-11-03
alter table demographic_numvalues alter column value decimal(19,9) not null;