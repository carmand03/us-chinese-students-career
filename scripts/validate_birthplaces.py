"""Reconciliation and regression checks for local birthplace lookup matching."""
from pathlib import Path
import json
import pandas as pd
from geocode_birthplaces import geocode_birthplaces
ROOT=Path(__file__).resolve().parent
main=pd.read_csv(ROOT/'data/main.csv',sep=';')
lookup=pd.read_csv(ROOT/'data/chinese_cities_with_coordinates.csv',sep=';',dtype=str)
audit,parsed=geocode_birthplaces(main,lookup)
assert audit.NameID.is_unique and len(audit)==len(main)
recorded=main.Birth_town_py.notna()|main.Birth_town_zh.notna()
assert audit.loc[recorded,'birth_geocode_status'].eq('matched').all()
assert audit.loc[~recorded,'birth_geocode_status'].eq('missing_town').all()
assert audit.loc[~recorded,['birth_lat','birth_lon']].isna().all().all()
valid=audit.loc[audit.birth_geocode_status.eq('matched')]
for row in valid.itertuples():
    source=parsed.loc[parsed['#'].isin(row.birth_lookup_ids.split('|'))]
    assert not source.empty
    assert source.Latitude_parsed.eq(row.birth_lat).all() and source.Longitude_parsed.eq(row.birth_lon).all()
joined=pd.read_csv(ROOT/'tables/career_joined.csv')
assert len(joined)==len(pd.read_csv(ROOT/'data/career.csv',sep=';'))
routes=pd.read_csv(ROOT/'tables/birth_education_work_routes.csv')
by=audit.set_index('NameID')
for r in routes.loc[routes.birth_lat.notna()].itertuples():
    assert abs(r.birth_lat-by.loc[r.NameID,'birth_lat'])<1e-10
    assert abs(r.birth_lon-by.loc[r.NameID,'birth_lon'])<1e-10
# Fixtures: province context, decimal commas, name normalization, contradictory coordinates, missing towns.
fixture=pd.DataFrame([{'#':'1','Province':'Jiangsu 江蘇','City':"Xi'an 西安",'Latitude':'31,25','Longitude':'120,5','Notes':''},{'#':'2','Province':'Zhejiang 浙江','City':"Xi'an 西安",'Latitude':'29.0','Longitude':'119.0','Notes':''}])
people=pd.DataFrame([{'NameID':'T1','Birth_province_py_st':'Jiangsu','Birth_province_zh_st':'江蘇','Birth_town_py':'Xian','Birth_town_zh':'西安'},{'NameID':'T2','Birth_province_py_st':'Zhejiang','Birth_province_zh_st':'浙江','Birth_town_py':"Xi’an",'Birth_town_zh':'西安'},{'NameID':'T3','Birth_province_py_st':'Jiangsu','Birth_province_zh_st':'江蘇','Birth_town_py':None,'Birth_town_zh':None}])
a,_=geocode_birthplaces(people,fixture)
assert a.iloc[0].birth_lat==31.25 and a.iloc[1].birth_lat==29.0
assert a.iloc[2].birth_geocode_status=='missing_town'
conflict=pd.concat([fixture,pd.DataFrame([dict(fixture.iloc[0],**{'#':'3','Latitude':'32.0'})])],ignore_index=True)
a,_=geocode_birthplaces(people,conflict)
assert a.iloc[0].birth_geocode_status=='ambiguous' and pd.isna(a.iloc[0].birth_lat)
invalid=fixture.copy();invalid.loc[0,'Latitude']='200'
a,_=geocode_birthplaces(people,invalid)
assert a.iloc[0].birth_geocode_status=='invalid_lookup_coordinates' and pd.isna(a.iloc[0].birth_lat)
result={'students':len(audit),'matched_birth_localities':len(valid),'missing_birth_town':int(audit.birth_geocode_status.eq('missing_town').sum()),'province_proxy_entries_explicitly_labelled':int(audit.birth_coordinate_precision.eq('province proxy in lookup').sum()),'all_recorded_birth_localities_matched':True,'route_coordinates_match_lookup':True,'ambiguous_and_invalid_coordinates_not_guessed':True,'decimal_comma_and_province_context_tests_passed':True}
(ROOT/'birthplace_validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
